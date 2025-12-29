#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 tw_* 表结构"""

import sys
sys.path.insert(0, 'src')
import psycopg2
from psycopg2.extras import RealDictCursor
import config

# 连接到 hiq_editor 数据库
conn = psycopg2.connect(
    host=config.PG_HOST,
    port=config.PG_PORT,
    user=config.PG_USER,
    password=config.PG_PASSWORD,
    database=config.EDITOR_DB_NAME
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# 检查多个表
tables = [
    config.EDITOR_EXCHANGES_TABLE,
    config.EDITOR_PROCESSES_TABLE,
    config.EDITOR_FLOWS_TABLE
]

for table_name in tables:
    # 查询表结构
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = %s 
        AND table_name = %s
        ORDER BY ordinal_position
    """, (config.EDITOR_SCHEMA, table_name))
    
    columns = cursor.fetchall()
    print(f"\n{table_name} 表的列:")
    print("=" * 60)
    for col in columns:
        print(f"  {col['column_name']:<30} {col['data_type']}")

cursor.close()
conn.close()
