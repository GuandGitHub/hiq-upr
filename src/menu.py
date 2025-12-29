"""
交互式菜单 - HIQ UPR Process Tree Builder

提供一个友好的交互式菜单界面，方便选择不同的功能
"""

import sys
import os


def clear_screen():
    """清屏"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """打印标题"""
    print("\n" + "=" * 70)
    print(" " * 15 + "HIQ UPR Process Tree Builder")
    print("=" * 70)
    print()


def print_menu():
    """打印菜单"""
    print("请选择功能：")
    print()
    print("  [1] 🔍 测试数据库连接")
    print("  [2] 🌲 构建过程树（生成 Markdown）")
    print("  [3] 📊 导出 JSON 格式")
    print("  [4] 📈 统计分析")
    print("  [5] 🎨 可视化（生成图形）")
    print("  [6] 📦 批量分析")
    print("  [7] 🚀 快速开始（测试 + 构建）")
    print()
    print("  [8] 📚 查看文档")
    print("  [9] ℹ️  关于")
    print("  [0] 🚪 退出")
    print()


def test_connection():
    """测试数据库连接"""
    print("\n" + "=" * 70)
    print("测试数据库连接")
    print("=" * 70 + "\n")
    
    import test_connection
    test_connection.main()
    
    input("\n按 Enter 键返回菜单...")


def build_tree():
    """构建过程树"""
    print("\n" + "=" * 70)
    print("构建过程树")
    print("=" * 70 + "\n")
    
    import build_process_tree
    build_process_tree.main()
    
    input("\n按 Enter 键返回菜单...")


def export_json():
    """导出 JSON"""
    print("\n" + "=" * 70)
    print("导出 JSON 格式")
    print("=" * 70 + "\n")
    
    import export_json
    export_json.main()
    
    input("\n按 Enter 键返回菜单...")


def analyze_stats():
    """统计分析"""
    print("\n" + "=" * 70)
    print("统计分析")
    print("=" * 70 + "\n")
    
    import analyze_statistics
    analyze_statistics.main()
    
    input("\n按 Enter 键返回菜单...")


def visualize():
    """可视化"""
    print("\n" + "=" * 70)
    print("可视化（生成图形）")
    print("=" * 70 + "\n")
    
    try:
        import visualize_tree
        visualize_tree.main()
    except ImportError as e:
        print("⚠ Graphviz 未安装")
        print("\n安装方法:")
        print("  1. 安装 Python 包: pip install graphviz")
        print("  2. 安装系统工具:")
        print("     - macOS: brew install graphviz")
        print("     - Ubuntu: sudo apt-get install graphviz")
        print("     - Windows: https://graphviz.org/download/")
    
    input("\n按 Enter 键返回菜单...")


def batch_analysis():
    """批量分析"""
    print("\n" + "=" * 70)
    print("批量分析")
    print("=" * 70 + "\n")
    
    print("提示: 请先编辑 batch_analysis.py 文件，添加要分析的根节点列表")
    print()
    
    response = input("是否继续？(y/n): ").strip().lower()
    if response in ['y', 'yes', '是']:
        import batch_analysis
        batch_analysis.main()
    else:
        print("已取消")
    
    input("\n按 Enter 键返回菜单...")


def quick_start():
    """快速开始"""
    print("\n" + "=" * 70)
    print("快速开始")
    print("=" * 70 + "\n")
    
    import quick_start
    quick_start.main()
    
    input("\n按 Enter 键返回菜单...")


def show_docs():
    """显示文档"""
    print("\n" + "=" * 70)
    print("文档")
    print("=" * 70 + "\n")
    
    print("可用文档：")
    print()
    print("  1. README.md - 项目介绍和快速入门")
    print("  2. USAGE.md - 详细使用指南")
    print("  3. PROJECT_STRUCTURE.md - 项目结构说明")
    print("  4. SUMMARY.md - 项目总结")
    print()
    print("请在文件管理器中打开相应的 .md 文件查看")
    
    input("\n按 Enter 键返回菜单...")


def show_about():
    """显示关于信息"""
    print("\n" + "=" * 70)
    print("关于")
    print("=" * 70 + "\n")
    
    print("HIQ UPR Process Tree Builder")
    print()
    print("版本: 1.0.0")
    print("日期: 2025-12-16")
    print()
    print("功能:")
    print("  - 递归追溯上游生产过程")
    print("  - 生成 Markdown/JSON 格式输出")
    print("  - 可视化图形生成")
    print("  - 统计分析")
    print("  - 批量处理")
    print()
    print("技术栈:")
    print("  - Python 3.x")
    print("  - PostgreSQL")
    print("  - psycopg2")
    print()
    print("License: MIT")
    
    input("\n按 Enter 键返回菜单...")


def main():
    """主函数"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("请输入选项 [0-9]: ").strip()
        
        if choice == '0':
            print("\n再见！👋\n")
            sys.exit(0)
        elif choice == '1':
            test_connection()
        elif choice == '2':
            build_tree()
        elif choice == '3':
            export_json()
        elif choice == '4':
            analyze_stats()
        elif choice == '5':
            visualize()
        elif choice == '6':
            batch_analysis()
        elif choice == '7':
            quick_start()
        elif choice == '8':
            show_docs()
        elif choice == '9':
            show_about()
        else:
            print("\n⚠ 无效选项，请重新选择")
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，再见！👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

