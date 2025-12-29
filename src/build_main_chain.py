"""
UPR Main Chain Builder - 主链路生成器

从 PostgreSQL 数据库的 tb_exchanges 表中，以指定的产品和 UPR 过程为根节点，
按照 exchange value 最大值规则，递归追溯上游生产过程，构建单一主链路。

规则：在每个层级，选择 value 最大的 input exchange 作为主要来源
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Optional, List
from datetime import datetime
import os
import config

# 确保输出目录存在
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


class MainChainNode:
    """表示主链路的一个节点"""
    
    def __init__(self, process_id: str, flow_id: Optional[str] = None, 
                 value: float = 0.0, level: int = 0,
                 unit_id: Optional[str] = None,
                 gwp: Optional[float] = None,
                 gwp_contribution: Optional[float] = None):
        self.process_id = process_id
        self.flow_id = flow_id  # 通过哪个 flow 连接到此 process
        self.value = value  # exchange 的 value（权重）
        self.level = level
        self.unit_id = unit_id
        self.gwp = gwp
        self.gwp_contribution = gwp_contribution
        self.next_node: Optional['MainChainNode'] = None  # 下一个节点（上游）
    
    def set_next(self, node: 'MainChainNode'):
        """设置下一个节点"""
        self.next_node = node


class MainChainBuilder:
    """构建 UPR 主链路"""
    
    def __init__(self, mode: str = "production"):
        """
        初始化主链路构建器
        
        Args:
            mode: 运行模式 - "production"（生产模式）或 "editor"（建设模式）
        """
        self.mode = mode
        self.conn = None
        self.cursor = None
        self.visited = set()  # 记录已访问的 process，防止循环
        self.process_names: Dict[str, str] = {}  # 缓存 process 名称
        self.flow_names: Dict[str, str] = {}  # 缓存 flow 名称
        self.unit_names: Dict[str, str] = {}  # 缓存 unit 名称
        
        # 根据模式设置数据库配置
        if mode == "editor":
            # Editor 模式：使用生产数据库的 tb_* 表
            self.database = config.EDITOR_DB_NAME  # hiq_background_db
            self.schema = config.EDITOR_SCHEMA
            self.exchanges_table = config.EDITOR_EXCHANGES_TABLE
            self.processes_table = config.EDITOR_PROCESSES_TABLE
            self.flows_table = config.EDITOR_FLOWS_TABLE
            self.units_table = config.EDITOR_UNITS_TABLE
            # 用于 category 过滤的表（来自 hiq_editor）
            self.filter_db = config.EDITOR_FILTER_DB_NAME  # hiq_editor
            self.process_data_table = config.EDITOR_PROCESS_DATA_TABLE
            self.category_filter = config.EDITOR_CATEGORY_FILTER
        else:
            self.database = config.PG_DATABASE
            self.schema = config.PG_SCHEMA
            self.exchanges_table = config.PG_TABLE
            self.processes_table = "tb_processes"
            self.flows_table = "tb_flows"
            self.units_table = "tb_units"
            self.filter_db = None
            self.process_data_table = None
            self.category_filter = None
    
    def connect_db(self):
        """连接到 PostgreSQL 数据库"""
        try:
            self.conn = psycopg2.connect(
                host=config.PG_HOST,
                port=config.PG_PORT,
                user=config.PG_USER,
                password=config.PG_PASSWORD,
                database=self.database
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            mode_text = "建设模式" if self.mode == "editor" else "生产模式"
            print(f"✓ 成功连接到数据库: {self.database} ({mode_text})")
            
            # Editor 模式需要额外连接 filter 数据库
            if self.mode == "editor" and self.filter_db:
                self.filter_conn = psycopg2.connect(
                    host=config.PG_HOST,
                    port=config.PG_PORT,
                    user=config.PG_USER,
                    password=config.PG_PASSWORD,
                    database=self.filter_db
                )
                self.filter_cursor = self.filter_conn.cursor(cursor_factory=RealDictCursor)
                print(f"✓ 成功连接到过滤数据库: {self.filter_db}")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            raise
    
    def close_db(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.mode == "editor" and hasattr(self, 'filter_cursor'):
            if self.filter_cursor:
                self.filter_cursor.close()
            if self.filter_conn:
                self.filter_conn.close()
        print("✓ 数据库连接已关闭")
    
    def get_max_value_exchange(self, process_id: str) -> Optional[Dict]:
        """
        获取指定 process 的 value 最大的上游 input exchange
        
        在 editor 模式下，只查找"原材料和燃料"类型的物料
        
        返回满足以下条件的记录中 value 最大的一条：
        - is_input = true
        - provider_id IS NOT NULL
        - is_deleted = false
        - version = VERSION
        - value 最大
        - (editor模式) 物料类型为"原材料和燃料"
        """
        if self.mode == "editor" and self.process_data_table:
            # 建设模式：分两步查询（跨数据库）
            # 步骤1：从 hiq_editor.tw_process_data 获取这个 process 下符合 category 的 exchange IDs
            # 优化：只查询当前 process_id 的数据，不全量查询
            filter_query = f"""
                SELECT DISTINCT e.id
                FROM public.tw_exchanges e
                INNER JOIN public.{self.process_data_table} pd ON e.id = pd.id
                WHERE e.process_id = %s
                  AND e.is_input = true
                  AND e.provider_id IS NOT NULL
                  AND e.is_deleted = false
                  AND pd.category_id = %s
            """
            self.filter_cursor.execute(filter_query, (process_id, self.category_filter))
            filter_results = self.filter_cursor.fetchall()
            valid_ids = [row['id'] for row in filter_results]
            
            if not valid_ids:
                return None
            
            # 步骤2：从 hiq_background_db.tb_exchanges 查询这些 IDs 的数据
            query = f"""
                SELECT 
                    process_id,
                    flow_id,
                    provider_id,
                    value,
                    is_input,
                    version,
                    unit_id,
                    gwp,
                    gwp_contribution,
                    exchange_group,
                    description
                FROM {self.schema}.{self.exchanges_table}
                WHERE process_id = %s
                  AND is_input = true
                  AND provider_id IS NOT NULL
                  AND is_deleted = false
                  AND version = %s
                  AND id = ANY(%s)
                ORDER BY value DESC NULLS LAST
                LIMIT 1
            """
            self.cursor.execute(query, (process_id, config.VERSION, valid_ids))
        else:
            # 生产模式：原有逻辑
            query = f"""
                SELECT 
                    process_id,
                    flow_id,
                    provider_id,
                    value,
                    is_input,
                    version,
                    unit_id,
                    gwp,
                    gwp_contribution,
                    exchange_group,
                    description
                FROM {self.schema}.{self.exchanges_table}
                WHERE process_id = %s
                  AND is_input = true
                  AND provider_id IS NOT NULL
                  AND is_deleted = false
                  AND version = %s
                ORDER BY value DESC NULLS LAST
                LIMIT 1
            """
            self.cursor.execute(query, (process_id, config.VERSION))
        
        result = self.cursor.fetchone()
        return result
    
    def get_all_exchanges(self, process_id: str) -> Dict[str, List[Dict]]:
        """
        获取指定 process 的所有输入和输出 exchanges
        
        在 editor 模式下，输入只包含"原材料和燃料"类型
        
        Returns:
            Dict with 'inputs' and 'outputs' keys, each containing list of exchanges
        """
        if self.mode == "editor" and self.process_data_table:
            # 建设模式：分两步查询
            # 步骤1：获取这个 process 下符合 category 的 exchange IDs（优化：不全量查询）
            filter_query = f"""
                SELECT DISTINCT e.id
                FROM public.tw_exchanges e
                INNER JOIN public.{self.process_data_table} pd ON e.id = pd.id
                WHERE e.process_id = %s
                  AND e.is_input = true
                  AND e.is_deleted = false
                  AND pd.category_id = %s
            """
            self.filter_cursor.execute(filter_query, (process_id, self.category_filter))
            filter_results = self.filter_cursor.fetchall()
            valid_ids = [row['id'] for row in filter_results]
            
            # 步骤2：从 tb_exchanges 查询数据
            # 输出：全部显示
            # 输入：只显示在 valid_ids 中的
            query = f"""
                SELECT 
                    flow_id,
                    provider_id,
                    value,
                    is_input,
                    unit_id,
                    gwp,
                    gwp_contribution,
                    description,
                    id
                FROM {self.schema}.{self.exchanges_table}
                WHERE process_id = %s
                  AND is_deleted = false
                  AND version = %s
                  AND (
                    is_input = false 
                    OR (is_input = true AND id = ANY(%s))
                  )
                ORDER BY is_input DESC, value DESC NULLS LAST
            """
            self.cursor.execute(query, (process_id, config.VERSION, valid_ids))
        else:
            # 生产模式：原有逻辑
            query = f"""
                SELECT 
                    flow_id,
                    provider_id,
                    value,
                    is_input,
                    unit_id,
                    gwp,
                    gwp_contribution,
                    description
                FROM {self.schema}.{self.exchanges_table}
                WHERE process_id = %s
                  AND is_deleted = false
                  AND version = %s
                ORDER BY is_input DESC, value DESC NULLS LAST
            """
            self.cursor.execute(query, (process_id, config.VERSION))
        
        results = self.cursor.fetchall()
        
        exchanges = {
            'inputs': [],
            'outputs': []
        }
        
        for row in results:
            exchange_data = {
                'flow_id': row['flow_id'],
                'provider_id': row['provider_id'],
                'value': float(row['value']) if row['value'] else 0.0,
                'unit_id': row['unit_id'],
                'gwp': float(row['gwp']) if row['gwp'] else None,
                'gwp_contribution': float(row['gwp_contribution']) if row['gwp_contribution'] else None,
                'description': row['description']
            }
            
            if row['is_input']:
                exchanges['inputs'].append(exchange_data)
            else:
                exchanges['outputs'].append(exchange_data)
        
        return exchanges
    
    def get_process_name(self, process_id: str) -> str:
        """获取 process 的名称（优先查询指定版本，如果没有则查询任意版本）"""
        if process_id in self.process_names:
            return self.process_names[process_id]
        
        name = None
        try:
            # 先尝试查询指定版本
            query = f"""
                SELECT name, version FROM {self.schema}.{self.processes_table}
                WHERE id = %s AND version = %s
            """
            self.cursor.execute(query, (process_id, config.VERSION))
            result = self.cursor.fetchone()
            
            if result:
                name = result['name']
            else:
                # 如果指定版本没有，尝试查询任意版本（优先较新版本）
                query = f"""
                    SELECT name, version FROM {self.schema}.{self.processes_table}
                    WHERE id = %s
                    ORDER BY version DESC
                    LIMIT 1
                """
                self.cursor.execute(query, (process_id,))
                result = self.cursor.fetchone()
                if result:
                    name = f"{result['name']} [v{result['version']}]"
        except Exception as e:
            print(f"⚠️  获取 process 名称失败: {e}")
        
        if not name:
            name = f"Process-{process_id[:8]}..."
        
        self.process_names[process_id] = name
        return name
    
    def get_flow_name(self, flow_id: str) -> str:
        """获取 flow 的名称"""
        if flow_id in self.flow_names:
            return self.flow_names[flow_id]
        
        try:
            query = f"""
                SELECT name FROM {self.schema}.{self.flows_table}
                WHERE id = %s AND version = %s
                LIMIT 1
            """
            self.cursor.execute(query, (flow_id, config.VERSION))
            
            result = self.cursor.fetchone()
            name = result['name'] if result else None
        except:
            name = None
        
        if not name:
            name = f"Flow-{flow_id[:8]}..."
        
        self.flow_names[flow_id] = name
        return name
    
    def get_unit_name(self, unit_id: str) -> str:
        """获取 unit 的名称"""
        if not unit_id:
            return "N/A"
        
        if unit_id in self.unit_names:
            return self.unit_names[unit_id]
        
        try:
            query = f"""
                SELECT name FROM {self.schema}.{self.units_table}
                WHERE id = %s
                LIMIT 1
            """
            self.cursor.execute(query, (unit_id,))
            result = self.cursor.fetchone()
            name = result['name'] if result else None
        except:
            name = None
        
        if not name:
            name = "N/A"
        
        self.unit_names[unit_id] = name
        return name
    
    def build_chain_recursive(self, process_id: str, flow_id: Optional[str] = None, 
                             value: float = 0.0, level: int = 0,
                             unit_id: Optional[str] = None,
                             gwp: Optional[float] = None,
                             gwp_contribution: Optional[float] = None) -> MainChainNode:
        """
        递归构建主链路
        
        Args:
            process_id: 当前 process ID
            flow_id: 通过哪个 flow 连接到此 process（可选）
            value: 边的权重值
            level: 当前层级
            unit_id: 单位ID
            gwp: 全球变暖潜势
            gwp_contribution: GWP贡献度
        
        Returns:
            MainChainNode: 当前节点
        """
        # 创建当前节点
        node = MainChainNode(process_id, flow_id, value, level, unit_id, gwp, gwp_contribution)
        
        # 检查是否已访问（防止循环）
        if process_id in self.visited:
            print(f"{'  ' * level}⚠ 检测到循环: {process_id[:8]}... (已访问，停止追溯)")
            return node
        
        # 标记为已访问
        self.visited.add(process_id)
        
        # 获取 value 最大的上游 exchange
        max_exchange = self.get_max_value_exchange(process_id)
        
        if max_exchange:
            upstream_process_id = max_exchange['provider_id']
            upstream_flow_id = max_exchange['flow_id']
            upstream_value = float(max_exchange['value']) if max_exchange['value'] else 0.0
            
            process_name = self.get_process_name(process_id)[:50]
            flow_name = self.get_flow_name(upstream_flow_id)[:50]
            unit_name = self.get_unit_name(max_exchange.get('unit_id'))
            gwp = max_exchange.get('gwp')
            gwp_cont = max_exchange.get('gwp_contribution')
            
            print(f"{'  ' * level}├─ Process: {process_name}")
            basis_parts = [f"value={upstream_value:.6f} {unit_name}", f"flow={flow_name}"]
            if gwp is not None:
                basis_parts.append(f"GWP={float(gwp):.6f}")
            if gwp_cont is not None:
                basis_parts.append(f"贡献度={float(gwp_cont)*100:.2f}%")
            print(f"{'  ' * level}│  └─ 选择依据: {', '.join(basis_parts)}")
            
            # 递归处理上游
            next_node = self.build_chain_recursive(
                upstream_process_id,
                upstream_flow_id,
                upstream_value,
                level + 1,
                max_exchange.get('unit_id'),
                float(max_exchange.get('gwp')) if max_exchange.get('gwp') else None,
                float(max_exchange.get('gwp_contribution')) if max_exchange.get('gwp_contribution') else None
            )
            node.set_next(next_node)
        else:
            process_name = self.get_process_name(process_id)[:50]
            print(f"{'  ' * level}└─ Process: {process_name} (叶子节点)")
        
        return node
    
    def generate_markdown(self, head_node: MainChainNode, output_file: str):
        """
        生成 Markdown 格式的主链路
        
        Args:
            head_node: 链路头节点
            output_file: 输出文件路径
        """
        print(f"\n生成 Markdown 文件: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入头部
            f.write("# UPR 主链路 (Main Chain)\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**版本**: {config.VERSION}\n\n")
            f.write(f"**根节点**:\n")
            f.write(f"- Flow ID: `{config.ROOT_FLOW_ID}`\n")
            f.write(f"- Process ID: `{config.ROOT_PROCESS_ID}`\n\n")
            f.write("**规则**: 每个层级选择 exchange value 最大的边作为主要来源\n\n")
            f.write("---\n\n")
            
            # 添加根节点的输入输出信息
            f.write("## 根节点 (Level 0) 详细信息\n\n")
            root_process_name = self.get_process_name(config.ROOT_PROCESS_ID)
            f.write(f"**Process**: {root_process_name}\n\n")
            
            exchanges = self.get_all_exchanges(config.ROOT_PROCESS_ID)
            
            # 输入信息
            f.write(f"### 输入 (Inputs) - 共 {len(exchanges['inputs'])} 项\n\n")
            if exchanges['inputs']:
                f.write("| Flow Name | Flow ID | Provider ID | Value | Unit | GWP | 贡献度 |\n")
                f.write("|-----------|---------|-------------|-------|------|-----|--------|\n")
                for inp in exchanges['inputs']:
                    flow_name = self.get_flow_name(inp['flow_id'])
                    provider_short = inp['provider_id'][:8] if inp['provider_id'] else 'N/A'
                    unit_name = self.get_unit_name(inp['unit_id'])
                    gwp_str = f"{inp['gwp']:.6f}" if inp['gwp'] is not None else "N/A"
                    cont_str = f"{inp['gwp_contribution']*100:.2f}%" if inp['gwp_contribution'] is not None else "N/A"
                    f.write(f"| {flow_name} | `{inp['flow_id'][:8]}...` | `{provider_short}...` | {inp['value']:.6f} | {unit_name} | {gwp_str} | {cont_str} |\n")
            else:
                f.write("_无输入_\n")
            
            f.write("\n")
            
            # 输出信息
            f.write(f"### 输出 (Outputs) - 共 {len(exchanges['outputs'])} 项\n\n")
            if exchanges['outputs']:
                f.write("| Flow Name | Flow ID | Value | Unit | GWP | 贡献度 |\n")
                f.write("|-----------|---------|-------|------|-----|--------|\n")
                for out in exchanges['outputs']:
                    flow_name = self.get_flow_name(out['flow_id'])
                    unit_name = self.get_unit_name(out['unit_id'])
                    gwp_str = f"{out['gwp']:.6f}" if out['gwp'] is not None else "N/A"
                    cont_str = f"{out['gwp_contribution']*100:.2f}%" if out['gwp_contribution'] is not None else "N/A"
                    f.write(f"| {flow_name} | `{out['flow_id'][:8]}...` | {out['value']:.6f} | {unit_name} | {gwp_str} | {cont_str} |\n")
            else:
                f.write("_无输出_\n")
            
            f.write("\n---\n\n")
            
            # 遍历链路
            current = head_node
            chain_length = 0
            
            f.write("## 主链路路径\n\n")
            
            while current:
                chain_length += 1
                indent = "  " * current.level
                
                # Process 信息
                process_name = self.get_process_name(current.process_id)
                f.write(f"{indent}**Level {current.level}**: Process\n")
                f.write(f"{indent}- **ID**: `{current.process_id}`\n")
                f.write(f"{indent}- **Name**: {process_name}\n")
                
                # Flow 信息（如果有）
                if current.flow_id:
                    flow_name = self.get_flow_name(current.flow_id)
                    unit_name = self.get_unit_name(current.unit_id)
                    f.write(f"{indent}- **Via Flow**: {flow_name}\n")
                    f.write(f"{indent}- **Flow ID**: `{current.flow_id}`\n")
                    f.write(f"{indent}- **Value**: {current.value:.6f} {unit_name}\n")
                    if current.gwp is not None:
                        f.write(f"{indent}- **GWP**: {current.gwp:.6f}\n")
                    if current.gwp_contribution is not None:
                        f.write(f"{indent}- **GWP 贡献度**: {current.gwp_contribution*100:.2f}%\n")
                
                f.write("\n")
                
                # 箭头指向下一个
                if current.next_node:
                    f.write(f"{indent}↓\n\n")
                
                current = current.next_node
            
            # 统计信息
            f.write("---\n\n")
            f.write("## 统计信息\n\n")
            f.write(f"- **链路长度**: {chain_length} 个节点\n")
            f.write(f"- **最大深度**: {chain_length - 1} 层\n")
            
        print(f"✓ Markdown 文件已生成")
    
    def generate_compact_txt(self, head_node: MainChainNode, output_file: str):
        """
        生成紧凑格式的 TXT 主链路（专为 LLM 优化）
        
        Args:
            head_node: 链路头节点
            output_file: 输出文件路径
        """
        print(f"\n生成紧凑 TXT 文件: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入头部说明
            f.write("=" * 80 + "\n")
            f.write(f"UPR 主链路 (Main Chain)\n")
            f.write("=" * 80 + "\n\n")
            if self.mode == "editor":
                f.write(f"物料类型过滤: 原材料和燃料 (category_id={self.category_filter})\n")
            f.write(f"分析 Process ID: {head_node.process_id}\n")
            f.write("规则: 每个层级选择 exchange value 最大的边\n")
            if self.mode == "editor":
                f.write("      建设模式下仅追溯\"原材料和燃料\"类型的上游物料\n")
            f.write("\n")
            
            f.write("格式说明:\n")
            f.write("  L<层级>: <Process名称> | <Process完整UUID>\n")
            f.write("    << <Flow名称> | <Flow完整UUID> | value=<数值>\n")
            f.write("    ↓\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 添加根节点详细信息（使用当前分析的 process）
            root_process_name = self.get_process_name(head_node.process_id)
            f.write("[根节点详细信息]\n")
            f.write(f"Process: {root_process_name}\n\n")
            
            exchanges = self.get_all_exchanges(head_node.process_id)
            
            # 输入
            f.write(f"输入 ({len(exchanges['inputs'])}项):\n")
            if exchanges['inputs']:
                for inp in exchanges['inputs']:
                    flow_name = self.get_flow_name(inp['flow_id'])
                    provider_short = inp['provider_id'][:8] if inp['provider_id'] else 'N/A'
                    unit_name = self.get_unit_name(inp['unit_id'])
                    parts = [f"value={inp['value']:.6f}", unit_name]
                    if inp['gwp'] is not None:
                        parts.append(f"GWP={inp['gwp']:.6f}")
                    if inp['gwp_contribution'] is not None:
                        parts.append(f"贡献度={inp['gwp_contribution']*100:.2f}%")
                    f.write(f"  ← {flow_name} | {inp['flow_id']} | provider={provider_short}... | {' | '.join(parts)}\n")
            else:
                f.write("  (无)\n")
            
            f.write("\n")
            
            # 输出
            f.write(f"输出 ({len(exchanges['outputs'])}项):\n")
            if exchanges['outputs']:
                for out in exchanges['outputs']:
                    flow_name = self.get_flow_name(out['flow_id'])
                    unit_name = self.get_unit_name(out['unit_id'])
                    parts = [f"value={out['value']:.6f}", unit_name]
                    if out['gwp'] is not None:
                        parts.append(f"GWP={out['gwp']:.6f}")
                    if out['gwp_contribution'] is not None:
                        parts.append(f"贡献度={out['gwp_contribution']*100:.2f}%")
                    f.write(f"  → {flow_name} | {out['flow_id']} | {' | '.join(parts)}\n")
            else:
                f.write("  (无)\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
            f.write("[主链路路径]\n\n")
            
            # 遍历链路
            current = head_node
            chain_length = 0
            
            while current:
                chain_length += 1
                
                # Process 行
                process_name = self.get_process_name(current.process_id)
                f.write(f"L{current.level}: {process_name} | {current.process_id}\n")
                
                # Flow 信息（只有当前节点有 flow_id 时才显示，即不是根节点）
                if current.flow_id:
                    flow_name = self.get_flow_name(current.flow_id)
                    unit_name = self.get_unit_name(current.unit_id)
                    parts = [f"value={current.value:.6f}", unit_name]
                    if current.gwp is not None:
                        parts.append(f"GWP={current.gwp:.6f}")
                    if current.gwp_contribution is not None:
                        parts.append(f"贡献度={current.gwp_contribution*100:.2f}%")
                    f.write(f"  << {flow_name} | {current.flow_id} | {' | '.join(parts)}\n")
                
                # 如果有下一个节点，显示箭头
                if current.next_node:
                    f.write("  ↓\n")
                
                current = current.next_node
            
            # 统计信息
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"链路长度: {chain_length} 个节点\n")
            f.write(f"最大深度: {chain_length - 1} 层\n")
            f.write("=" * 80 + "\n")
        
        print(f"✓ 紧凑 TXT 文件已生成")
    
    def run(self):
        """运行完整流程"""
        print("=" * 80)
        print("UPR 主链路生成器 (Main Chain Builder)")
        print("=" * 80)
        print(f"数据库: {config.PG_DATABASE}")
        print(f"版本: {config.VERSION}")
        print(f"根节点 Flow ID: {config.ROOT_FLOW_ID}")
        print(f"根节点 Process ID: {config.ROOT_PROCESS_ID}")
        print("=" * 80)
        print()
        
        # 连接数据库
        self.connect_db()
        
        try:
            # 构建主链路
            print("开始构建主链路（按 value 最大值）...\n")
            head_node = self.build_chain_recursive(
                process_id=config.ROOT_PROCESS_ID,
                flow_id=config.ROOT_FLOW_ID,
                value=0.0,
                level=0
            )
            
            # 生成输出文件
            root_flow_short = config.ROOT_FLOW_ID[:8]
            
            # 仅生成紧凑 TXT 格式
            txt_file = os.path.join(OUTPUT_DIR, f"main_chain_{root_flow_short}.txt")
            self.generate_compact_txt(head_node, txt_file)
            
            print("\n" + "=" * 80)
            print("✓ 主链路生成完成!")
            print(f"  - 输出文件: {txt_file}")
            print("=" * 80)
            
        finally:
            self.close_db()


def main():
    """主函数"""
    builder = MainChainBuilder()
    builder.run()


if __name__ == "__main__":
    main()
