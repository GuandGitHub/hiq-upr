"""
批量分析多个根节点

支持批量处理多个产品/过程的过程树构建
"""

import os
from datetime import datetime
from typing import List, Tuple
from build_process_tree import ProcessTreeBuilder
import config


class BatchAnalyzer:
    """批量分析器"""
    
    def __init__(self):
        self.results = []
        self.output_dir = "batch_output"
    
    def setup_output_dir(self):
        """创建输出目录"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ 创建输出目录: {self.output_dir}")
    
    def analyze_single(self, flow_id: str, process_id: str, name: str = None) -> dict:
        """
        分析单个根节点
        
        Args:
            flow_id: 产品 flow ID
            process_id: 根 process ID
            name: 可选的名称标识
        
        Returns:
            分析结果字典
        """
        if name is None:
            name = process_id[:8]
        
        print(f"\n{'='*60}")
        print(f"分析: {name}")
        print(f"{'='*60}")
        print(f"Flow ID:    {flow_id}")
        print(f"Process ID: {process_id}")
        print()
        
        builder = ProcessTreeBuilder()
        
        try:
            # 临时修改 config
            original_flow = config.ROOT_FLOW_ID
            original_process = config.ROOT_PROCESS_ID
            
            config.ROOT_FLOW_ID = flow_id
            config.ROOT_PROCESS_ID = process_id
            
            # 连接数据库
            builder.connect_db()
            
            # 构建树
            start_time = datetime.now()
            root = builder.build_tree_recursive(process_id)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # 生成输出
            output_file = os.path.join(self.output_dir, f"{name}_tree.md")
            builder.generate_markdown(root, output_file)
            
            # 统计信息
            stats = {
                "name": name,
                "flow_id": flow_id,
                "process_id": process_id,
                "total_processes": len(builder.visited),
                "max_depth": builder._get_max_depth(root),
                "duration_seconds": duration,
                "output_file": output_file,
                "success": True,
                "error": None
            }
            
            print(f"✓ 完成")
            print(f"  - 总节点数: {stats['total_processes']}")
            print(f"  - 最大深度: {stats['max_depth']}")
            print(f"  - 耗时: {duration:.2f} 秒")
            print(f"  - 输出: {output_file}")
            
            # 恢复 config
            config.ROOT_FLOW_ID = original_flow
            config.ROOT_PROCESS_ID = original_process
            
            return stats
            
        except Exception as e:
            print(f"✗ 失败: {e}")
            
            stats = {
                "name": name,
                "flow_id": flow_id,
                "process_id": process_id,
                "success": False,
                "error": str(e)
            }
            
            return stats
            
        finally:
            builder.close_db()
    
    def analyze_batch(self, roots: List[Tuple[str, str, str]]):
        """
        批量分析
        
        Args:
            roots: [(flow_id, process_id, name), ...]
        """
        print("=" * 60)
        print("批量过程树分析")
        print("=" * 60)
        print(f"总任务数: {len(roots)}")
        print()
        
        # 创建输出目录
        self.setup_output_dir()
        
        # 逐个分析
        for i, (flow_id, process_id, name) in enumerate(roots, 1):
            print(f"\n[{i}/{len(roots)}]")
            
            result = self.analyze_single(flow_id, process_id, name)
            self.results.append(result)
        
        # 生成汇总报告
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """生成汇总报告"""
        report_file = os.path.join(self.output_dir, "batch_summary.md")
        
        lines = []
        lines.append("# 批量分析汇总报告")
        lines.append("")
        lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**版本:** {config.VERSION}")
        lines.append(f"**总任务数:** {len(self.results)}")
        lines.append("")
        
        # 成功/失败统计
        success_count = sum(1 for r in self.results if r['success'])
        failed_count = len(self.results) - success_count
        
        lines.append("## 执行统计")
        lines.append("")
        lines.append(f"- ✓ 成功: {success_count}")
        lines.append(f"- ✗ 失败: {failed_count}")
        lines.append(f"- 成功率: {success_count/len(self.results)*100:.1f}%")
        lines.append("")
        
        # 详细结果
        lines.append("## 详细结果")
        lines.append("")
        lines.append("| 序号 | 名称 | 节点数 | 深度 | 耗时(秒) | 状态 |")
        lines.append("|------|------|--------|------|----------|------|")
        
        for i, result in enumerate(self.results, 1):
            if result['success']:
                status = "✓"
                nodes = result['total_processes']
                depth = result['max_depth']
                duration = f"{result['duration_seconds']:.2f}"
            else:
                status = "✗"
                nodes = "-"
                depth = "-"
                duration = "-"
            
            lines.append(f"| {i} | {result['name']} | {nodes} | {depth} | {duration} | {status} |")
        
        lines.append("")
        
        # 失败详情
        if failed_count > 0:
            lines.append("## 失败详情")
            lines.append("")
            
            for result in self.results:
                if not result['success']:
                    lines.append(f"### {result['name']}")
                    lines.append("")
                    lines.append(f"- **Flow ID:** `{result['flow_id']}`")
                    lines.append(f"- **Process ID:** `{result['process_id']}`")
                    lines.append(f"- **错误信息:** {result['error']}")
                    lines.append("")
        
        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n✓ 汇总报告已生成: {report_file}")


def main():
    """主函数 - 示例用法"""
    
    # 定义要分析的根节点列表
    # 格式: (flow_id, process_id, name)
    roots = [
        # 示例 1: 使用配置文件中的默认根节点
        (
            config.ROOT_FLOW_ID,
            config.ROOT_PROCESS_ID,
            "default_root"
        ),
        
        # 示例 2: 添加更多根节点（请根据实际数据修改）
        # (
        #     "your-flow-id-2",
        #     "your-process-id-2",
        #     "product_2"
        # ),
        # (
        #     "your-flow-id-3",
        #     "your-process-id-3",
        #     "product_3"
        # ),
    ]
    
    # 创建分析器
    analyzer = BatchAnalyzer()
    
    # 执行批量分析
    analyzer.analyze_batch(roots)
    
    print("\n" + "=" * 60)
    print("✓ 批量分析完成！")
    print("=" * 60)
    print(f"\n输出目录: {analyzer.output_dir}")
    print(f"汇总报告: {analyzer.output_dir}/batch_summary.md")
    print()


if __name__ == "__main__":
    main()

