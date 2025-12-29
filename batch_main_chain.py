#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量主链路分析工具

从 process_ids.txt 文件中读取多个 process_id，
为每个 process 生成主链路分析结果。

支持两种模式：
- production: 生产模式（默认），从 hiq_background_db 读取数据
- editor: 建设模式，从 hiq_editor 读取数据（tw_exchanges, tw_processes）
"""

import os
import sys
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from build_main_chain import MainChainBuilder
import config


def read_process_ids(file_path: str = "process_ids.txt"):
    """
    从文件中读取 process_ids
    
    Args:
        file_path: 包含 process_id 列表的文件路径
    
    Returns:
        list: process_id 列表
    """
    process_ids = []
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        print(f"提示: 请创建 {file_path} 文件并添加 process_id（每行一个）")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 去除空白和注释
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 提取 process_id（去除行内注释）
            process_id = line.split('#')[0].strip()
            
            # 简单验证 UUID 格式
            if len(process_id) == 36 and process_id.count('-') == 4:
                process_ids.append(process_id)
            else:
                print(f"⚠️  跳过无效的 process_id（第 {line_num} 行）: {process_id}")
    
    return process_ids


def analyze_main_chains(process_ids: list, mode: str = "production", output_dir: str = None):
    """
    批量分析主链路
    
    Args:
        process_ids: process_id 列表
        mode: 运行模式 - "production" 或 "editor"
        output_dir: 输出目录（如果为 None 则根据模式自动设置）
    """
    if not process_ids:
        print("❌ 没有可分析的 process_id")
        return
    
    # 根据模式设置输出目录
    if output_dir is None:
        if mode == "editor":
            output_dir = os.path.join("output", "steel")
        else:
            output_dir = "output"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    mode_text = "建设模式 (hiq_editor)" if mode == "editor" else "生产模式 (hiq_background_db)"
    
    print("=" * 80)
    print(f"批量主链路分析 - {mode_text}")
    print("=" * 80)
    print(f"待分析 process 数量: {len(process_ids)}")
    print(f"输出目录: {output_dir}")
    if mode == "editor":
        print(f"数据库: {config.EDITOR_DB_NAME} (exchanges/processes)")
        print(f"过滤数据库: {config.EDITOR_FILTER_DB_NAME} ({config.EDITOR_PROCESS_DATA_TABLE})")
        print(f"表: {config.EDITOR_EXCHANGES_TABLE}, {config.EDITOR_PROCESSES_TABLE}")
        print(f"物料过滤: category_id={config.EDITOR_CATEGORY_FILTER} (原材料和燃料)")
    else:
        print(f"数据库: {config.PG_DATABASE}")
    print(f"版本: {config.VERSION}")
    print("=" * 80)
    print()
    
    results = {
        'success': [],
        'failed': []
    }
    
    # 连接数据库一次，复用连接
    builder = MainChainBuilder(mode=mode)
    builder.connect_db()
    
    try:
        for idx, process_id in enumerate(process_ids, 1):
            print(f"\n{'=' * 80}")
            print(f"[{idx}/{len(process_ids)}] 分析 Process: {process_id}")
            print(f"{'=' * 80}")
            
            try:
                # 重置访问记录（每个 process 独立分析）
                builder.visited.clear()
                
                # 构建主链路
                print(f"开始构建主链路...\n")
                head_node = builder.build_chain_recursive(
                    process_id=process_id,
                    flow_id=None,
                    value=0.0,
                    level=0
                )
                
                # 生成输出文件（仅 TXT 格式）
                process_short = process_id[:8]
                
                # 紧凑 TXT 格式
                txt_file = os.path.join(output_dir, f"main_chain_{process_short}.txt")
                builder.generate_compact_txt(head_node, txt_file)
                
                results['success'].append({
                    'process_id': process_id,
                    'txt': txt_file
                })
                
                print(f"\n✅ 完成!")
                print(f"   - 输出文件: {txt_file}")
                
            except Exception as e:
                print(f"\n❌ 分析失败: {e}")
                import traceback
                traceback.print_exc()
                results['failed'].append({
                    'process_id': process_id,
                    'error': str(e)
                })
    
    finally:
        builder.close_db()
    
    # 打印总结
    print("\n" + "=" * 80)
    print("批量分析完成!")
    print("=" * 80)
    print(f"\n✅ 成功: {len(results['success'])} 个")
    for item in results['success']:
        print(f"   - {item['process_id'][:8]}... → {item['txt']}")
    
    if results['failed']:
        print(f"\n❌ 失败: {len(results['failed'])} 个")
        for item in results['failed']:
            print(f"   - {item['process_id'][:8]}... : {item['error']}")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量主链路分析工具')
    parser.add_argument('--mode', '-m', 
                       choices=['production', 'editor'], 
                       default='production',
                       help='运行模式: production (生产模式，默认) 或 editor (建设模式)')
    parser.add_argument('--output', '-o',
                       help='自定义输出目录（默认: production模式用output/, editor模式用output/battery/）')
    
    args = parser.parse_args()
    
    # 读取 process_ids
    process_ids = read_process_ids("process_ids.txt")
    
    if not process_ids:
        print("\n使用说明:")
        print("1. 编辑 process_ids.txt 文件")
        print("2. 每行添加一个 process_id（完整的 UUID）")
        print("3. 可以添加注释（以 # 开头）")
        print("4. 重新运行此脚本")
        print("\n示例文件内容:")
        print("   6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # Process 1")
        print("   a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Process 2")
        print("\n运行模式:")
        print("   python batch_main_chain.py              # 生产模式（默认）")
        print("   python batch_main_chain.py --mode editor  # 建设模式")
        return
    
    # 执行批量分析
    analyze_main_chains(process_ids, mode=args.mode, output_dir=args.output)


if __name__ == "__main__":
    main()
