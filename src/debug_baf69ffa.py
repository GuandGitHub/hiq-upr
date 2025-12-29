#!/usr/bin/env python3
"""调试为什么 baf69ffa 节点被标记为叶子节点"""

import psycopg2

def main():
    conn = psycopg2.connect(
        host='rm-cn-4xl3hy9vo000h4o.rwlb.rds.aliyuncs.com',
        port=3433,
        database='hiq_background_db',
        user='readonly',
        password='ro2024!@'
    )
    cur = conn.cursor()
    
    process_id = 'baf69ffa-4714-3e76-8413-05a2c2d7c82d'
    
    # 1. 检查该节点的所有输入边（不限制 value）
    print(f"\n=== 1. Process {process_id[:8]} 的所有输入边 ===")
    cur.execute('''
        SELECT 
            id, provider_id, flow_id, value, is_input, is_deleted
        FROM tb_exchanges
        WHERE process_id = %s
        AND is_input = true
        ORDER BY value DESC NULLS LAST
        LIMIT 20
    ''', (process_id,))
    rows = cur.fetchall()
    print(f"总共找到 {len(rows)} 条输入边")
    for i, r in enumerate(rows, 1):
        print(f"  {i}. provider: {r[1][:8] if r[1] else 'NULL':<8}... | "
              f"flow: {r[2][:8] if r[2] else 'NULL':<8}... | "
              f"value: {r[3] if r[3] is not None else 'NULL':<10} | "
              f"is_deleted: {r[5]}")
    
    # 2. 检查有 provider_id 的输入边
    print(f"\n=== 2. Process {process_id[:8]} 的有效输入边（provider_id 不为空）===")
    cur.execute('''
        SELECT 
            id, provider_id, flow_id, value
        FROM tb_exchanges
        WHERE process_id = %s
        AND is_input = true
        AND provider_id IS NOT NULL
        AND (is_deleted IS NULL OR is_deleted = false)
        ORDER BY value DESC NULLS LAST
        LIMIT 10
    ''', (process_id,))
    rows = cur.fetchall()
    print(f"总共找到 {len(rows)} 条有效输入边")
    for i, r in enumerate(rows, 1):
        print(f"  {i}. provider: {r[1][:8]}... | flow: {r[2][:8]}... | value: {r[3]}")
    
    # 3. 检查该节点在完整树中的位置
    print(f"\n=== 3. 在完整树结构中查找该节点 ===")
    cur.execute('''
        SELECT name, location, description
        FROM tb_processes
        WHERE id = %s
    ''', (process_id,))
    proc = cur.fetchone()
    if proc:
        print(f"  name: {proc[0]}")
        print(f"  location: {proc[1]}")
        print(f"  description: {proc[2] if proc[2] else 'N/A'}")
    
    # 4. 反向查询：谁引用了这个节点作为 provider
    print(f"\n=== 4. 有多少节点将 {process_id[:8]} 作为上游 ===")
    cur.execute('''
        SELECT COUNT(*) 
        FROM tb_exchanges
        WHERE provider_id = %s
        AND is_input = true
    ''', (process_id,))
    count = cur.fetchone()[0]
    print(f"  有 {count} 个节点依赖此节点")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
