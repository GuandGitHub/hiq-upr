"""
Quick Start - 快速开始

一键运行测试和构建过程树
"""

import sys
import subprocess


def run_test():
    """运行数据库连接测试"""
    print("=" * 60)
    print("步骤 1: 测试数据库连接")
    print("=" * 60)
    print()
    
    try:
        import test_connection
        test_connection.main()
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def run_build():
    """运行过程树构建"""
    print("\n" + "=" * 60)
    print("步骤 2: 构建过程树")
    print("=" * 60)
    print()
    
    try:
        import build_process_tree
        build_process_tree.main()
        return True
    except Exception as e:
        print(f"✗ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🚀 HIQ UPR Process Tree Builder - Quick Start")
    print()
    
    # 检查依赖
    try:
        import psycopg2
    except ImportError:
        print("⚠ 依赖未安装，正在安装 psycopg2...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        print("✓ 依赖安装成功")
        print()
    
    # 运行测试
    if not run_test():
        print("\n❌ 测试失败，请检查数据库配置")
        sys.exit(1)
    
    # 询问是否继续
    print("\n" + "=" * 60)
    response = input("是否继续构建过程树？(y/n): ").strip().lower()
    
    if response not in ['y', 'yes', '是']:
        print("已取消")
        sys.exit(0)
    
    # 运行构建
    if run_build():
        print("\n" + "=" * 60)
        print("✓ 完成！")
        print("=" * 60)
        print("\n生成的文件:")
        print("  - process_tree.md")
        print("\n你也可以运行以下命令生成 JSON 格式:")
        print("  python export_json.py")
        print()
    else:
        print("\n❌ 构建失败")
        sys.exit(1)


if __name__ == "__main__":
    main()

