"""
可视化过程树 - 使用 Graphviz 生成图形

将过程树导出为图形格式（PNG, SVG, PDF等）
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("⚠ Graphviz 未安装，请运行: pip install graphviz")

from build_process_tree import ProcessTreeBuilder, ProcessTreeNode
import config


class TreeVisualizer:
    """将过程树可视化为图形"""
    
    def __init__(self, builder: ProcessTreeBuilder):
        self.builder = builder
        self.dot = None
    
    def create_graph(self, root: ProcessTreeNode, graph_name: str = "Process Tree"):
        """
        创建 Graphviz 图形对象
        
        Args:
            root: 根节点
            graph_name: 图形名称
        """
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError("Graphviz 未安装")
        
        # 创建有向图
        self.dot = Digraph(comment=graph_name)
        self.dot.attr(rankdir='BT')  # 从下到上（Bottom to Top）
        self.dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        self.dot.attr('edge', color='gray', arrowhead='vee')
        
        # 添加节点和边
        self._add_node_recursive(root)
        
        return self.dot
    
    def _add_node_recursive(self, node: ProcessTreeNode):
        """
        递归添加节点和边
        
        Args:
            node: 当前节点
        """
        # 获取节点信息
        process_id = node.process_id
        process_name = self.builder.get_process_name(process_id)
        process_short = process_id[:8]
        
        # 添加节点标签
        label = f"{process_short}...\n{process_name}"
        
        # 根节点使用不同颜色
        if node.level == 0:
            self.dot.node(process_id, label, fillcolor='lightcoral')
        else:
            self.dot.node(process_id, label)
        
        # 递归处理子节点
        for child in node.children:
            child_process_id = child.process_id
            
            # 添加子节点
            self._add_node_recursive(child)
            
            # 添加边（从子节点指向当前节点）
            if child.flow_id:
                flow_short = child.flow_id[:8]
                flow_name = self.builder.get_flow_name(child.flow_id)
                edge_label = f"{flow_short}...\n{flow_name}"
            else:
                edge_label = ""
            
            self.dot.edge(child_process_id, process_id, label=edge_label)
    
    def render(self, output_file: str = "process_tree", format: str = "png"):
        """
        渲染图形到文件
        
        Args:
            output_file: 输出文件名（不含扩展名）
            format: 输出格式 (png, svg, pdf, etc.)
        """
        if not self.dot:
            raise ValueError("请先调用 create_graph() 创建图形")
        
        try:
            self.dot.render(output_file, format=format, cleanup=True)
            print(f"✓ 图形已生成: {output_file}.{format}")
        except Exception as e:
            print(f"✗ 渲染失败: {e}")
            print("  提示: 确保已安装 Graphviz 系统工具")
            print("  macOS: brew install graphviz")
            print("  Ubuntu: sudo apt-get install graphviz")
            print("  Windows: https://graphviz.org/download/")


def main():
    """主函数"""
    if not GRAPHVIZ_AVAILABLE:
        print("错误: 请先安装 Graphviz:")
        print("  pip install graphviz")
        return
    
    print("=" * 60)
    print("UPR Process Tree Visualizer")
    print("=" * 60)
    print()
    
    # 构建树
    builder = ProcessTreeBuilder()
    
    try:
        builder.connect_db()
        
        print(f"构建过程树...")
        print(f"根节点: {config.ROOT_PROCESS_ID}")
        print()
        
        root = builder.build_tree_recursive(config.ROOT_PROCESS_ID)
        
        # 可视化
        print(f"\n生成可视化图形...")
        visualizer = TreeVisualizer(builder)
        visualizer.create_graph(root, "UPR Process Tree")
        
        # 生成多种格式
        formats = ['png', 'svg', 'pdf']
        for fmt in formats:
            try:
                visualizer.render("process_tree_graph", format=fmt)
            except Exception as e:
                print(f"⚠ {fmt.upper()} 格式生成失败: {e}")
        
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

