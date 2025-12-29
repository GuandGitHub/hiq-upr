"""
深度统计分析

对过程树进行深度统计分析，包括：
- 节点分布
- 层级分布
- 扇出度（fan-out）统计
- 关键路径分析
"""

from collections import defaultdict
from typing import Dict, List
from build_process_tree import ProcessTreeBuilder, ProcessTreeNode
import config


class TreeStatistics:
    """过程树统计分析"""
    
    def __init__(self, builder: ProcessTreeBuilder, root: ProcessTreeNode):
        self.builder = builder
        self.root = root
        
        # 统计数据
        self.level_distribution: Dict[int, int] = defaultdict(int)
        self.fanout_distribution: Dict[int, int] = defaultdict(int)
        self.leaf_nodes: List[str] = []
        self.all_nodes: List[str] = []
    
    def analyze(self):
        """执行统计分析"""
        self._traverse_tree(self.root)
    
    def _traverse_tree(self, node: ProcessTreeNode):
        """遍历树并收集统计信息"""
        # 记录节点
        self.all_nodes.append(node.process_id)
        
        # 层级分布
        self.level_distribution[node.level] += 1
        
        # 扇出度
        fanout = len(node.children)
        self.fanout_distribution[fanout] += 1
        
        # 叶子节点
        if fanout == 0:
            self.leaf_nodes.append(node.process_id)
        
        # 递归处理子节点
        for child in node.children:
            self._traverse_tree(child)
    
    def get_max_depth(self) -> int:
        """获取最大深度"""
        if not self.level_distribution:
            return 0
        return max(self.level_distribution.keys())
    
    def get_avg_fanout(self) -> float:
        """获取平均扇出度（不含叶子节点）"""
        non_leaf_nodes = [node for node in self.all_nodes 
                         if node not in self.leaf_nodes]
        
        if not non_leaf_nodes:
            return 0.0
        
        total_children = sum(
            fanout * count 
            for fanout, count in self.fanout_distribution.items() 
            if fanout > 0
        )
        
        return total_children / len(non_leaf_nodes)
    
    def get_critical_path(self) -> List[str]:
        """获取关键路径（最长路径）"""
        path = []
        
        def find_longest_path(node: ProcessTreeNode) -> List[str]:
            if not node.children:
                return [node.process_id]
            
            longest = []
            for child in node.children:
                child_path = find_longest_path(child)
                if len(child_path) > len(longest):
                    longest = child_path
            
            return [node.process_id] + longest
        
        return find_longest_path(self.root)
    
    def generate_report(self, output_file: str = "statistics_report.md"):
        """生成统计报告"""
        lines = []
        
        lines.append("# 过程树统计分析报告")
        lines.append("")
        lines.append(f"**版本:** {config.VERSION}")
        lines.append(f"**根节点:** {config.ROOT_PROCESS_ID[:8]}...")
        lines.append("")
        
        # 基本统计
        lines.append("## 基本统计")
        lines.append("")
        lines.append(f"- **总节点数:** {len(self.all_nodes)}")
        lines.append(f"- **叶子节点数:** {len(self.leaf_nodes)}")
        lines.append(f"- **非叶子节点数:** {len(self.all_nodes) - len(self.leaf_nodes)}")
        lines.append(f"- **最大深度:** {self.get_max_depth()}")
        lines.append(f"- **平均扇出度:** {self.get_avg_fanout():.2f}")
        lines.append("")
        
        # 层级分布
        lines.append("## 层级分布")
        lines.append("")
        lines.append("| 层级 | 节点数 | 百分比 |")
        lines.append("|------|--------|--------|")
        
        for level in sorted(self.level_distribution.keys()):
            count = self.level_distribution[level]
            percentage = count / len(self.all_nodes) * 100
            lines.append(f"| {level} | {count} | {percentage:.1f}% |")
        
        lines.append("")
        
        # 扇出度分布
        lines.append("## 扇出度分布")
        lines.append("")
        lines.append("| 扇出度 | 节点数 | 说明 |")
        lines.append("|--------|--------|------|")
        
        for fanout in sorted(self.fanout_distribution.keys()):
            count = self.fanout_distribution[fanout]
            desc = "叶子节点" if fanout == 0 else f"{fanout} 个上游"
            lines.append(f"| {fanout} | {count} | {desc} |")
        
        lines.append("")
        
        # 关键路径
        critical_path = self.get_critical_path()
        lines.append("## 关键路径")
        lines.append("")
        lines.append(f"最长路径长度: {len(critical_path)}")
        lines.append("")
        lines.append("路径节点:")
        lines.append("")
        
        for i, process_id in enumerate(critical_path):
            process_name = self.builder.get_process_name(process_id)
            indent = "  " * i
            if i == 0:
                lines.append(f"{indent}└─ **[根]** `{process_id[:8]}...` {process_name}")
            else:
                lines.append(f"{indent}└─ `{process_id[:8]}...` {process_name}")
        
        lines.append("")
        
        # 叶子节点列表
        lines.append("## 叶子节点（前10个）")
        lines.append("")
        lines.append("| 序号 | Process ID | Process Name |")
        lines.append("|------|------------|--------------|")
        
        for i, process_id in enumerate(self.leaf_nodes[:10], 1):
            process_name = self.builder.get_process_name(process_id)
            lines.append(f"| {i} | `{process_id[:8]}...` | {process_name} |")
        
        if len(self.leaf_nodes) > 10:
            lines.append(f"| ... | ... | 还有 {len(self.leaf_nodes) - 10} 个叶子节点 |")
        
        lines.append("")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ 统计报告已生成: {output_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("过程树统计分析")
    print("=" * 60)
    print()
    
    builder = ProcessTreeBuilder()
    
    try:
        # 连接数据库
        builder.connect_db()
        
        # 构建树
        print(f"构建过程树...")
        print(f"根节点: {config.ROOT_PROCESS_ID}")
        print()
        
        root = builder.build_tree_recursive(config.ROOT_PROCESS_ID)
        
        # 统计分析
        print(f"\n执行统计分析...")
        stats = TreeStatistics(builder, root)
        stats.analyze()
        
        # 生成报告
        print(f"\n生成统计报告...")
        stats.generate_report()
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("统计摘要")
        print("=" * 60)
        print(f"总节点数: {len(stats.all_nodes)}")
        print(f"叶子节点数: {len(stats.leaf_nodes)}")
        print(f"最大深度: {stats.get_max_depth()}")
        print(f"平均扇出度: {stats.get_avg_fanout():.2f}")
        print(f"关键路径长度: {len(stats.get_critical_path())}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close_db()


if __name__ == "__main__":
    main()

