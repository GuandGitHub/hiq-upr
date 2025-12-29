"""
UPR Process Tree Builder

从 PostgreSQL 数据库的 tb_exchanges 表中，以指定的产品和 UPR 过程为根节点，
递归追溯所有上游生产过程（process），构建完整的"生产过程树（Process Tree）"，
并生成 Markdown 格式的树状逻辑图。
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Set, Optional
from datetime import datetime
import os
import config

# 确保输出目录存在
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ProcessTreeNode:
    """表示过程树的一个节点"""
    
    def __init__(self, process_id: str, flow_id: Optional[str] = None, level: int = 0):
        self.process_id = process_id
        self.flow_id = flow_id  # 通过哪个 flow 连接到此 process（Skeleton 模式：单条）
        self.flows = []  # Full LCI 模式：存储所有 flow_id
        self.level = level
        self.children: List[ProcessTreeNode] = []
    
    def add_child(self, child: 'ProcessTreeNode'):
        """添加子节点"""
        self.children.append(child)
    
    def add_flow(self, flow_id: str):
        """添加额外的 flow（用于 Full LCI 模式）"""
        if flow_id and flow_id not in self.flows:
            self.flows.append(flow_id)


class ProcessTreeBuilder:
    """构建 UPR 生产过程树"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.visited: Set[str] = set()  # 记录已访问的 process，防止循环
        self.process_names: Dict[str, str] = {}  # 缓存 process 名称
        self.flow_names: Dict[str, str] = {}  # 缓存 flow 名称
        self.full_lci_edges: Dict[tuple, List[str]] = {}  # Full LCI: (upstream, downstream) -> [flow_ids]
    
    def connect_db(self):
        """连接到 PostgreSQL 数据库"""
        try:
            self.conn = psycopg2.connect(
                host=config.PG_HOST,
                port=config.PG_PORT,
                user=config.PG_USER,
                password=config.PG_PASSWORD,
                database=config.PG_DATABASE
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print(f"✓ 成功连接到数据库: {config.PG_DATABASE}")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            raise
    
    def close_db(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("✓ 数据库连接已关闭")
    
    def get_upstream_exchanges(self, process_id: str) -> List[Dict]:
        """
        获取指定 process 的所有上游 input exchanges
        
        返回满足以下条件的记录：
        - is_input = true
        - provider_id IS NOT NULL
        - is_deleted = false
        - version = VERSION
        """
        query = f"""
            SELECT 
                process_id,
                flow_id,
                provider_id,
                is_input,
                is_product,
                is_deleted,
                version
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE process_id = %s
              AND is_input = true
              AND provider_id IS NOT NULL
              AND is_deleted = false
              AND version = %s
            ORDER BY flow_id
        """
        
        self.cursor.execute(query, (process_id, config.VERSION))
        results = self.cursor.fetchall()
        return results
    
    def get_process_name(self, process_id: str) -> str:
        """获取 process 的名称（如果有的话）"""
        if process_id in self.process_names:
            return self.process_names[process_id]
        
        # 尝试从数据库获取 process 名称
        # 注意：这里假设可能有 tb_processes 表，如果没有则返回 ID
        # 你可以根据实际数据库结构调整
        try:
            query = """
                SELECT name FROM public.tb_processes 
                WHERE id = %s AND version = %s
                LIMIT 1
            """
            self.cursor.execute(query, (process_id, config.VERSION))
            result = self.cursor.fetchone()
            name = result['name'] if result else None
        except:
            name = None
        
        if not name:
            name = f"Process-{process_id[:8]}..."
        
        self.process_names[process_id] = name
        return name
    
    def get_flow_name(self, flow_id: str) -> str:
        """获取 flow 的名称（如果有的话）"""
        if flow_id in self.flow_names:
            return self.flow_names[flow_id]
        
        # 尝试从数据库获取 flow 名称
        try:
            query = """
                SELECT name FROM public.tb_flows 
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
    
    def build_tree_recursive(self, process_id: str, flow_id: Optional[str] = None, level: int = 0, 
                           full_lci_mode: bool = False) -> ProcessTreeNode:
        """
        递归构建过程树
        
        Args:
            process_id: 当前 process ID
            flow_id: 通过哪个 flow 连接到此 process（可选）
            level: 当前层级（用于显示）
            full_lci_mode: 是否为 Full LCI 模式（收集所有 flow）
        
        Returns:
            ProcessTreeNode: 当前节点及其所有子树
        """
        # 创建当前节点
        node = ProcessTreeNode(process_id, flow_id, level)
        
        # 检查是否已访问（防止循环）
        if process_id in self.visited:
            print(f"{'  ' * level}⚠ 检测到循环: {process_id[:8]}... (已访问)")
            return node
        
        # 标记为已访问
        self.visited.add(process_id)
        
        # 获取所有上游 exchanges
        upstream_exchanges = self.get_upstream_exchanges(process_id)
        
        if upstream_exchanges:
            print(f"{'  ' * level}├─ Process: {process_id[:8]}... 发现 {len(upstream_exchanges)} 个上游输入")
        else:
            print(f"{'  ' * level}└─ Process: {process_id[:8]}... (叶子节点)")
        
        # Full LCI 模式：按 provider_id 分组收集所有 flow
        if full_lci_mode and upstream_exchanges:
            from collections import defaultdict
            provider_flows = defaultdict(list)
            for exchange in upstream_exchanges:
                upstream_process_id = exchange['provider_id']
                upstream_flow_id = exchange['flow_id']
                provider_flows[upstream_process_id].append(upstream_flow_id)
            
            # 递归处理每个上游 process（去重）
            for upstream_process_id, flow_ids in provider_flows.items():
                # 创建子节点，使用第一个 flow 作为主 flow
                child_node = self.build_tree_recursive(
                    upstream_process_id, 
                    flow_ids[0], 
                    level + 1,
                    full_lci_mode=True
                )
                # 添加所有 flow 到节点
                for fid in flow_ids:
                    child_node.add_flow(fid)
                
                # 记录边的所有 flow（用于后续分析）
                edge_key = (upstream_process_id, process_id)
                if edge_key not in self.full_lci_edges:
                    self.full_lci_edges[edge_key] = []
                self.full_lci_edges[edge_key].extend(flow_ids)
                
                node.add_child(child_node)
        else:
            # Skeleton 模式：每个 provider 只取第一条 flow（原有逻辑）
            for exchange in upstream_exchanges:
                upstream_process_id = exchange['provider_id']
                upstream_flow_id = exchange['flow_id']
                
                # 递归构建子树
                child_node = self.build_tree_recursive(
                    upstream_process_id, 
                    upstream_flow_id, 
                    level + 1,
                    full_lci_mode=False
                )
                node.add_child(child_node)
        
        return node
    
    def generate_markdown(self, root: ProcessTreeNode, output_file: str = "process_tree.md", 
                         mode: str = "skeleton"):
        """
        生成 Markdown 格式的树状结构
        
        Args:
            root: 根节点
            output_file: 输出文件名
            mode: "skeleton" 或 "full_lci"
        """
        lines = []
        
        # 标题
        mode_title = "Skeleton Tree (Single Edge)" if mode == "skeleton" else "Full LCI Tree (Multiple Edges)"
        lines.append(f"# UPR Process Tree Analysis - {mode_title}")
        lines.append(f"")
        lines.append(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Version:** {config.VERSION}")
        lines.append(f"**Mode:** {mode_title}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        
        # 根产品信息
        lines.append(f"## Product (Root Flow)")
        lines.append(f"- **Flow ID:** `{config.ROOT_FLOW_ID}`")
        lines.append(f"- **Flow Name:** {self.get_flow_name(config.ROOT_FLOW_ID)}")
        lines.append(f"")
        
        # 根过程信息
        lines.append(f"## Root Process (UPR)")
        lines.append(f"- **Process ID:** `{config.ROOT_PROCESS_ID}`")
        lines.append(f"- **Process Name:** {self.get_process_name(config.ROOT_PROCESS_ID)}")
        lines.append(f"")
        
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Process Tree Structure")
        lines.append(f"")
        
        if mode == "skeleton":
            lines.append(f"*Note: Each upstream → downstream relationship shows only one representative flow.*")
        else:
            lines.append(f"*Note: Each upstream → downstream relationship shows ALL flows.*")
        lines.append(f"")
        
        # 递归生成树结构
        self._write_tree_node(root, lines, prefix="", is_last=True, mode=mode)
        
        # 统计信息
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Statistics")
        lines.append(f"- **Total Processes:** {len(self.visited)}")
        lines.append(f"- **Max Depth:** {self._get_max_depth(root)}")
        if mode == "full_lci" and self.full_lci_edges:
            total_flows = sum(len(flows) for flows in self.full_lci_edges.values())
            lines.append(f"- **Total Edges:** {len(self.full_lci_edges)}")
            lines.append(f"- **Total Flows:** {total_flows}")
            lines.append(f"- **Avg Flows per Edge:** {total_flows/len(self.full_lci_edges):.2f}")
        lines.append(f"")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n✓ Markdown 树状图已生成: {output_file}")
    
    def _write_tree_node(self, node: ProcessTreeNode, lines: List[str], prefix: str = "", 
                        is_last: bool = True, mode: str = "skeleton"):
        """
        递归写入树节点（Markdown 格式）
        
        Args:
            node: 当前节点
            lines: 输出行列表
            prefix: 前缀（用于缩进）
            is_last: 是否是最后一个子节点
            mode: "skeleton" 或 "full_lci"
        """
        # 构建当前行
        connector = "└─" if is_last else "├─"
        
        # 显示 process 信息
        process_short = node.process_id[:8]
        process_name = self.get_process_name(node.process_id)
        
        if mode == "skeleton":
            # Skeleton 模式：只显示一条 flow
            if node.flow_id:
                flow_short = node.flow_id[:8]
                flow_name = self.get_flow_name(node.flow_id)
                line = f"{prefix}{connector} **[{process_short}...]** {process_name} ← via `{flow_short}...` ({flow_name})"
            else:
                # 根节点
                line = f"{prefix}{connector} **[{process_short}...]** {process_name}"
            lines.append(line)
        else:
            # Full LCI 模式：显示 process，然后列出所有 flow
            if node.flows:
                # 有多条 flow
                line = f"{prefix}{connector} **[{process_short}...]** {process_name}"
                lines.append(line)
                
                # 显示所有 flow
                extension = "    " if is_last else "│   "
                for i, flow_id in enumerate(node.flows):
                    flow_short = flow_id[:8]
                    flow_name = self.get_flow_name(flow_id)
                    flow_line = f"{prefix}{extension}  → via `{flow_short}...` ({flow_name})"
                    lines.append(flow_line)
            elif node.flow_id:
                # 只有一条 flow（向后兼容）
                flow_short = node.flow_id[:8]
                flow_name = self.get_flow_name(node.flow_id)
                line = f"{prefix}{connector} **[{process_short}...]** {process_name}"
                lines.append(line)
                extension = "    " if is_last else "│   "
                flow_line = f"{prefix}{extension}  → via `{flow_short}...` ({flow_name})"
                lines.append(flow_line)
            else:
                # 根节点
                line = f"{prefix}{connector} **[{process_short}...]** {process_name}"
                lines.append(line)
        
        # 递归处理子节点
        if node.children:
            extension = "    " if is_last else "│   "
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                self._write_tree_node(child, lines, prefix + extension, is_last_child, mode=mode)
    
    def _get_max_depth(self, node: ProcessTreeNode, current_depth: int = 0) -> int:
        """计算树的最大深度"""
        if not node.children:
            return current_depth
        
        max_child_depth = current_depth
        for child in node.children:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def run(self, output_file: str = "process_tree.md", generate_both: bool = False):
        """
        运行完整的流程：连接数据库 -> 构建树 -> 生成 Markdown
        
        Args:
            output_file: 输出文件名（Skeleton 模式）
            generate_both: 是否同时生成 Skeleton 和 Full LCI 两个版本
        """
        try:
            print("=" * 60)
            print("UPR Process Tree Builder")
            print("=" * 60)
            print()
            
            # 1. 连接数据库
            self.connect_db()
            
            # 获取 flow_id 的短名称（用于文件名）
            flow_short = config.ROOT_FLOW_ID[:8]
            
            if not generate_both:
                # 只生成 Skeleton Tree（原有逻辑）
                print(f"\n开始构建过程树 (Skeleton Mode)...")
                print(f"根节点: {config.ROOT_PROCESS_ID}")
                print(f"产品 Flow: {config.ROOT_FLOW_ID}")
                print(f"版本: {config.VERSION}")
                print()
                
                root = self.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=False)
                
                print(f"\n生成 Markdown 树状图...")
                self.generate_markdown(root, output_file, mode="skeleton")
                
            else:
                # 生成两个版本
                print(f"\n【模式 1/2】构建 Skeleton Tree (单连接边)...")
                print(f"根节点: {config.ROOT_PROCESS_ID}")
                print(f"产品 Flow: {config.ROOT_FLOW_ID}")
                print(f"版本: {config.VERSION}")
                print()
                
                # 构建 Skeleton Tree
                root_skeleton = self.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=False)
                skeleton_file = os.path.join(OUTPUT_DIR, f"process_tree_skeleton_{flow_short}.md")
                
                print(f"\n生成 Skeleton Markdown...")
                self.generate_markdown(root_skeleton, skeleton_file, mode="skeleton")
                
                # 重置 visited 以便重新构建
                self.visited.clear()
                self.full_lci_edges.clear()
                
                print(f"\n{'='*60}")
                print(f"【模式 2/2】构建 Full LCI Tree (多连接边)...")
                print(f"{'='*60}\n")
                
                # 构建 Full LCI Tree
                root_full = self.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=True)
                full_lci_file = os.path.join(OUTPUT_DIR, f"process_tree_full_lci_{flow_short}.md")
                
                print(f"\n生成 Full LCI Markdown...")
                self.generate_markdown(root_full, full_lci_file, mode="full_lci")
                
                print(f"\n{'='*60}")
                print(f"✓ 两个版本均已生成！")
                print(f"{'='*60}")
                print(f"\n生成文件:")
                print(f"  1. Skeleton Tree: {skeleton_file}")
                print(f"  2. Full LCI Tree: {full_lci_file}")
                return
            
            print("\n" + "=" * 60)
            print("✓ 完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ 执行失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 4. 关闭数据库连接
            self.close_db()


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    generate_both = "--both" in sys.argv or "-b" in sys.argv
    
    builder = ProcessTreeBuilder()
    
    if generate_both:
        print("\n🔄 将生成两个版本：Skeleton Tree 和 Full LCI Tree\n")
        builder.run(generate_both=True)
    else:
        print("\n📝 默认模式：仅生成 Skeleton Tree")
        print("   提示：使用 --both 参数可同时生成两个版本\n")
        output_file = os.path.join(OUTPUT_DIR, "process_tree.md")
        builder.run(output_file=output_file, generate_both=False)


if __name__ == "__main__":
    main()

