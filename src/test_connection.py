"""
测试数据库连接和数据查询

在运行主程序之前，使用此脚本验证：
1. 数据库连接是否正常
2. tb_exchanges 表是否存在
3. 根节点数据是否存在
4. 查询逻辑是否正确
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import config


def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试 1: 数据库连接")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 测试查询
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"✓ 数据库连接成功")
        print(f"  PostgreSQL 版本: {result['version']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


def test_table_exists():
    """测试 tb_exchanges 表是否存在"""
    print("\n" + "=" * 60)
    print("测试 2: 检查表是否存在")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 检查表是否存在
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = %s
            );
        """
        cursor.execute(query, (config.PG_SCHEMA, config.PG_TABLE))
        result = cursor.fetchone()
        
        if result['exists']:
            print(f"✓ 表 {config.PG_SCHEMA}.{config.PG_TABLE} 存在")
            
            # 获取表结构
            query = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """
            cursor.execute(query, (config.PG_SCHEMA, config.PG_TABLE))
            columns = cursor.fetchall()
            
            print(f"\n  表结构（共 {len(columns)} 列）:")
            for col in columns[:10]:  # 只显示前10列
                print(f"    - {col['column_name']}: {col['data_type']}")
            if len(columns) > 10:
                print(f"    ... 还有 {len(columns) - 10} 列")
            
            cursor.close()
            conn.close()
            return True
        else:
            print(f"✗ 表 {config.PG_SCHEMA}.{config.PG_TABLE} 不存在")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False


def test_root_node():
    """测试根节点数据是否存在"""
    print("\n" + "=" * 60)
    print("测试 3: 检查根节点数据")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 检查根 process 是否存在
        query = f"""
            SELECT COUNT(*) as count
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE process_id = %s AND version = %s
        """
        cursor.execute(query, (config.ROOT_PROCESS_ID, config.VERSION))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            print(f"✓ 根 process_id 存在: {config.ROOT_PROCESS_ID}")
            print(f"  找到 {result['count']} 条相关记录")
        else:
            print(f"✗ 根 process_id 不存在: {config.ROOT_PROCESS_ID}")
            print(f"  version = {config.VERSION}")
        
        # 检查根 flow 是否存在
        query = f"""
            SELECT COUNT(*) as count
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE flow_id = %s AND version = %s
        """
        cursor.execute(query, (config.ROOT_FLOW_ID, config.VERSION))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            print(f"✓ 根 flow_id 存在: {config.ROOT_FLOW_ID}")
            print(f"  找到 {result['count']} 条相关记录")
        else:
            print(f"✗ 根 flow_id 不存在: {config.ROOT_FLOW_ID}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False


def test_upstream_query():
    """测试上游查询逻辑"""
    print("\n" + "=" * 60)
    print("测试 4: 测试上游查询")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 查询根节点的上游
        query = f"""
            SELECT 
                process_id,
                flow_id,
                provider_id,
                is_input,
                is_product,
                is_deleted
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE process_id = %s
              AND is_input = true
              AND provider_id IS NOT NULL
              AND is_deleted = false
              AND version = %s
            LIMIT 10
        """
        
        cursor.execute(query, (config.ROOT_PROCESS_ID, config.VERSION))
        results = cursor.fetchall()
        
        print(f"\n根节点 {config.ROOT_PROCESS_ID[:8]}... 的上游输入:")
        print(f"找到 {len(results)} 条记录（最多显示 10 条）\n")
        
        if results:
            for i, row in enumerate(results, 1):
                print(f"  [{i}] Provider: {row['provider_id'][:8]}...")
                print(f"      Flow: {row['flow_id'][:8]}...")
                print(f"      is_input: {row['is_input']}, is_product: {row['is_product']}")
                print()
            print("✓ 查询逻辑正确")
        else:
            print("  ⚠ 未找到上游输入（可能是叶子节点）")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_statistics():
    """测试数据统计"""
    print("\n" + "=" * 60)
    print("测试 5: 数据统计")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 总记录数
        query = f"""
            SELECT COUNT(*) as total
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE version = %s AND is_deleted = false
        """
        cursor.execute(query, (config.VERSION,))
        result = cursor.fetchone()
        print(f"  总记录数（version={config.VERSION}）: {result['total']:,}")
        
        # 唯一 process 数
        query = f"""
            SELECT COUNT(DISTINCT process_id) as total
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE version = %s AND is_deleted = false
        """
        cursor.execute(query, (config.VERSION,))
        result = cursor.fetchone()
        print(f"  唯一 process 数: {result['total']:,}")
        
        # 唯一 flow 数
        query = f"""
            SELECT COUNT(DISTINCT flow_id) as total
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE version = %s AND is_deleted = false
        """
        cursor.execute(query, (config.VERSION,))
        result = cursor.fetchone()
        print(f"  唯一 flow 数: {result['total']:,}")
        
        # input 记录数
        query = f"""
            SELECT COUNT(*) as total
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE version = %s AND is_deleted = false AND is_input = true
        """
        cursor.execute(query, (config.VERSION,))
        result = cursor.fetchone()
        print(f"  输入记录数: {result['total']:,}")
        
        # 有 provider 的 input 记录数
        query = f"""
            SELECT COUNT(*) as total
            FROM {config.PG_SCHEMA}.{config.PG_TABLE}
            WHERE version = %s AND is_deleted = false 
              AND is_input = true AND provider_id IS NOT NULL
        """
        cursor.execute(query, (config.VERSION,))
        result = cursor.fetchone()
        print(f"  有 provider 的输入记录数: {result['total']:,}")
        
        print("\n✓ 统计完成")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 统计失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "🔍 HIQ UPR 数据库连接测试")
    print()
    
    results = []
    
    # 运行测试
    results.append(("数据库连接", test_connection()))
    results.append(("表存在性", test_table_exists()))
    results.append(("根节点数据", test_root_node()))
    results.append(("上游查询", test_upstream_query()))
    results.append(("数据统计", test_data_statistics()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！可以运行主程序。")
        print("\n运行命令: python build_process_tree.py")
    else:
        print("\n✗ 部分测试失败，请检查配置和数据。")
    
    print()


if __name__ == "__main__":
    main()

