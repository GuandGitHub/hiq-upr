"""
Database configuration for HIQ UPR Process Tree
"""

# ========== 生产模式（默认）==========
# PostgreSQL Connection
PG_HOST = "101.227.234.12"
PG_PORT = 5432
PG_USER = "root"
PG_PASSWORD = "HiqProdDB@2024"
PG_DATABASE = "hiq_background_db"
PG_SCHEMA = "public"
PG_TABLE = "tb_exchanges"

# Query Parameters
VERSION = "1.4.0"

# Root node information
ROOT_FLOW_ID = "02eef75e-bb2f-4283-95b4-249521aa2c12"  # 线材, 不锈钢
ROOT_PROCESS_ID = "251da196-55f8-4c57-a783-9888cf33c626"  # 线材,不锈钢, 转炉钢


# ========== 建设模式配置 ==========
# Editor 模式使用生产数据库的 tb_* 表，但通过 hiq_editor 的 tw_process_data 过滤
EDITOR_DB_NAME = "hiq_background_db"  # exchanges/processes 数据来源
EDITOR_SCHEMA = "public"
EDITOR_EXCHANGES_TABLE = "tb_exchanges"
EDITOR_PROCESSES_TABLE = "tb_processes"
EDITOR_FLOWS_TABLE = "tb_flows"
EDITOR_UNITS_TABLE = "tb_units"

# 用于 category 过滤的数据表（来自 hiq_editor 数据库）
EDITOR_FILTER_DB_NAME = "hiq_editor"
EDITOR_PROCESS_DATA_TABLE = "tw_process_data"

# 物料类型过滤（仅建设模式使用）
# 只查找"原材料和燃料"类型的物料
EDITOR_CATEGORY_FILTER = "15889393230266368"  # 原材料和燃料

