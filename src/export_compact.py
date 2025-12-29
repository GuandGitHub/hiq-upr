"""
紧凑格式导出器 - 专为 LLM 处理优化

特点：
1. 完整 ID（不截断）
2. 最小化格式（只用空格缩进）
3. 可选是否包含名称
4. 文件大小大幅减小
"""

from build_process_tree import ProcessTreeBuilder, ProcessTreeNode, OUTPUT_DIR
import config
import os
from typing import List


class CompactExporter:
    """紧凑格式导出器"""
    
    def __init__(self, builder: ProcessTreeBuilder):
        self.builder = builder
    
    def export_compact(self, root: ProcessTreeNode, output_file: str = "process_tree_compact.txt",
                      mode: str = "skeleton", include_names: bool = True):
        """
        导出紧凑格式（优化版，包含名称和说明）
        
        Args:
            root: 根节点
            output_file: 输出文件名
            mode: "skeleton" 或 "full_lci"
            include_names: 是否包含名称（默认包含）
        """
        lines = []
        
        # 详细的标题说明
        lines.append("=" * 80)
        lines.append(f"UPR Process Tree - {mode.upper()} MODE")
        lines.append("=" * 80)
        lines.append("")
        lines.append("## Basic Information")
        lines.append(f"Root Product Flow: {config.ROOT_FLOW_ID}")
        root_flow_name = self.builder.get_flow_name(config.ROOT_FLOW_ID)
        lines.append(f"  Name: {root_flow_name}")
        lines.append("")
        lines.append(f"Root Process: {config.ROOT_PROCESS_ID}")
        root_process_name = self.builder.get_process_name(config.ROOT_PROCESS_ID)
        lines.append(f"  Name: {root_process_name}")
        lines.append("")
        lines.append(f"Version: {config.VERSION}")
        lines.append(f"Generated: {self._get_timestamp()}")
        lines.append("")
        
        # 格式说明
        lines.append("## Format Description")
        if mode == "skeleton":
            lines.append("Mode: SKELETON TREE (Single Edge)")
            lines.append("  - Each upstream → downstream relationship shows ONE representative flow")
            lines.append("  - Format: process_id | process_name << flow_id | flow_name")
            lines.append("  - Indentation indicates hierarchy level")
        else:
            lines.append("Mode: FULL LCI TREE (Multiple Edges)")
            lines.append("  - Each upstream → downstream relationship shows ALL flows")
            lines.append("  - Format:")
            lines.append("      process_id | process_name")
            lines.append("        << flow_id_1 | flow_name_1")
            lines.append("        << flow_id_2 | flow_name_2")
            lines.append("  - Indentation indicates hierarchy level")
        lines.append("")
        lines.append("Notation:")
        lines.append("  | separates ID and name")
        lines.append("  << indicates flow connection (upstream provides this flow)")
        lines.append("  [CYCLE] marks detected circular dependency")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        # 递归生成树
        self._write_compact_node(root, lines, level=0, mode=mode, include_names=include_names)
        
        # 统计信息
        lines.append("")
        lines.append("=" * 80)
        lines.append("## Statistics")
        lines.append("=" * 80)
        lines.append(f"Total Processes: {len(self.builder.visited)}")
        lines.append(f"Max Depth: {self._get_max_depth(root)}")
        
        if mode == "full_lci" and self.builder.full_lci_edges:
            total_flows = sum(len(flows) for flows in self.builder.full_lci_edges.values())
            total_edges = len(self.builder.full_lci_edges)
            lines.append(f"Total Edges: {total_edges}")
            lines.append(f"Total Flows: {total_flows}")
            lines.append(f"Avg Flows per Edge: {total_flows/total_edges:.2f}")
        
        lines.append("=" * 80)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ 紧凑格式已生成: {output_file}")
        
        # 显示文件大小
        import os
        size = os.path.getsize(output_file)
        size_mb = size / (1024 * 1024)
        print(f"  文件大小: {size_mb:.2f} MB")
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_max_depth(self, node: ProcessTreeNode, current_depth: int = 0) -> int:
        """计算树的最大深度"""
        if not node.children:
            return current_depth
        
        max_child_depth = current_depth
        for child in node.children:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def _write_compact_node(self, node: ProcessTreeNode, lines: List[str], level: int = 0,
                           mode: str = "skeleton", include_names: bool = True):
        """
        写入紧凑格式的节点（优化版）
        
        格式：
        - Skeleton: {indent}process_id | process_name << flow_id | flow_name
        - Full LCI: {indent}process_id | process_name
                    {indent}  << flow_id_1 | flow_name_1
                    {indent}  << flow_id_2 | flow_name_2
        """
        indent = "  " * level
        process_id = node.process_id
        
        # 获取名称
        if include_names:
            process_name = self.builder.get_process_name(process_id)
        else:
            process_name = ""
        
        if mode == "skeleton":
            # Skeleton 模式：一行显示
            if node.flow_id:
                if include_names:
                    flow_name = self.builder.get_flow_name(node.flow_id)
                    line = f"{indent}{process_id} | {process_name} << {node.flow_id} | {flow_name}"
                else:
                    line = f"{indent}{process_id} << {node.flow_id}"
            else:
                # 根节点
                if include_names:
                    line = f"{indent}{process_id} | {process_name}"
                else:
                    line = f"{indent}{process_id}"
            
            lines.append(line)
        
        else:
            # Full LCI 模式：process 一行，每个 flow 单独一行
            if include_names:
                line = f"{indent}{process_id} | {process_name}"
            else:
                line = f"{indent}{process_id}"
            lines.append(line)
            
            # 显示所有 flow
            if node.flows:
                for flow_id in node.flows:
                    if include_names:
                        flow_name = self.builder.get_flow_name(flow_id)
                        flow_line = f"{indent}  << {flow_id} | {flow_name}"
                    else:
                        flow_line = f"{indent}  << {flow_id}"
                    lines.append(flow_line)
            elif node.flow_id:
                # 兼容只有单条 flow 的情况
                if include_names:
                    flow_name = self.builder.get_flow_name(node.flow_id)
                    flow_line = f"{indent}  << {node.flow_id} | {flow_name}"
                else:
                    flow_line = f"{indent}  << {node.flow_id}"
                lines.append(flow_line)
        
        # 递归处理子节点
        for child in node.children:
            self._write_compact_node(child, lines, level + 1, mode, include_names)


def main():
    """主函数"""
    import sys
    
    print("=" * 60)
    print("紧凑格式导出器（专为 LLM 优化）")
    print("=" * 60)
    print()
    
    # 检查参数
    include_names = "--no-names" not in sys.argv  # 默认包含名称
    generate_both = "--both" in sys.argv or "-b" in sys.argv
    id_only = "--id-only" in sys.argv  # 仅 ID 模式（超紧凑）
    
    builder = ProcessTreeBuilder()
    exporter = CompactExporter(builder)
    
    try:
        builder.connect_db()
        flow_short = config.ROOT_FLOW_ID[:8]
        
        if generate_both:
            # 生成两种模式
            print("模式 1/2: 生成 Skeleton Tree (紧凑格式)")
            print()
            
            # Skeleton
            builder.visited.clear()
            root_skeleton = builder.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=False)
            skeleton_file = os.path.join(OUTPUT_DIR, f"process_tree_skeleton_compact_{flow_short}.txt")
            exporter.export_compact(root_skeleton, skeleton_file, mode="skeleton", 
                                   include_names=not id_only and include_names)
            
            # Full LCI
            print()
            print("模式 2/2: 生成 Full LCI Tree (紧凑格式)")
            print()
            
            builder.visited.clear()
            builder.full_lci_edges.clear()
            root_full = builder.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=True)
            full_file = os.path.join(OUTPUT_DIR, f"process_tree_full_lci_compact_{flow_short}.txt")
            exporter.export_compact(root_full, full_file, mode="full_lci", 
                                   include_names=not id_only and include_names)
            
            print()
            print("=" * 60)
            print("✓ 两种模式均已生成（紧凑格式）")
            print("=" * 60)
            print(f"\n生成文件:")
            print(f"  1. Skeleton: {skeleton_file}")
            print(f"  2. Full LCI: {full_file}")
            
        else:
            # 只生成 Skeleton
            print("生成 Skeleton Tree (紧凑格式)")
            print()
            
            root = builder.build_tree_recursive(config.ROOT_PROCESS_ID, full_lci_mode=False)
            output_file = os.path.join(OUTPUT_DIR, f"process_tree_compact_{flow_short}.txt")
            exporter.export_compact(root, output_file, mode="skeleton", 
                                   include_names=not id_only and include_names)
            
            print()
            print("=" * 60)
            print("✓ 完成！")
            print("=" * 60)
        
        if id_only or not include_names:
            print("\n提示: 仅包含 ID（文件最小）")
            print("      默认模式会包含名称")
        else:
            print("\n提示: 包含了名称信息（推荐，易于理解）")
            print("      使用 --no-names 或 --id-only 可去除名称")
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close_db()


if __name__ == "__main__":
    main()

