"""
Export Process Tree to JSON format

提供将过程树导出为 JSON 格式的功能，方便进一步分析和可视化
"""

import json
from typing import Dict, Any
from build_process_tree import ProcessTreeBuilder, ProcessTreeNode


class JSONExporter:
    """将过程树导出为 JSON"""
    
    def __init__(self, builder: ProcessTreeBuilder):
        self.builder = builder
    
    def node_to_dict(self, node: ProcessTreeNode) -> Dict[str, Any]:
        """
        将树节点转换为字典
        
        Args:
            node: ProcessTreeNode 对象
        
        Returns:
            字典表示的树节点
        """
        result = {
            "process_id": node.process_id,
            "process_name": self.builder.get_process_name(node.process_id),
            "level": node.level,
        }
        
        if node.flow_id:
            result["flow_id"] = node.flow_id
            result["flow_name"] = self.builder.get_flow_name(node.flow_id)
        
        if node.children:
            result["children"] = [
                self.node_to_dict(child) for child in node.children
            ]
            result["children_count"] = len(node.children)
        else:
            result["children"] = []
            result["children_count"] = 0
        
        return result
    
    def export(self, root: ProcessTreeNode, output_file: str = "process_tree.json"):
        """
        导出为 JSON 文件
        
        Args:
            root: 根节点
            output_file: 输出文件名
        """
        tree_dict = self.node_to_dict(root)
        
        # 添加元数据
        output_data = {
            "metadata": {
                "version": "1.4.0",
                "total_processes": len(self.builder.visited),
                "max_depth": self._get_max_depth(root)
            },
            "tree": tree_dict
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON 文件已生成: {output_file}")
    
    def _get_max_depth(self, node: ProcessTreeNode, current_depth: int = 0) -> int:
        """计算树的最大深度"""
        if not node.children:
            return current_depth
        
        max_child_depth = current_depth
        for child in node.children:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth


def main():
    """主函数：同时生成 Markdown 和 JSON"""
    from build_process_tree import ProcessTreeBuilder
    import config
    
    builder = ProcessTreeBuilder()
    
    try:
        print("=" * 60)
        print("UPR Process Tree Builder (Markdown + JSON)")
        print("=" * 60)
        print()
        
        # 连接数据库
        builder.connect_db()
        
        # 构建树
        print(f"\n开始构建过程树...")
        print(f"根节点: {config.ROOT_PROCESS_ID}")
        print(f"产品 Flow: {config.ROOT_FLOW_ID}")
        print(f"版本: {config.VERSION}")
        print()
        
        root = builder.build_tree_recursive(config.ROOT_PROCESS_ID)
        
        # 生成 Markdown
        print(f"\n生成 Markdown 树状图...")
        builder.generate_markdown(root, "process_tree.md")
        
        # 生成 JSON
        print(f"\n生成 JSON 文件...")
        exporter = JSONExporter(builder)
        exporter.export(root, "process_tree.json")
        
        print("\n" + "=" * 60)
        print("✓ 完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close_db()


if __name__ == "__main__":
    main()

