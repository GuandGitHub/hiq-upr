# HIQ UPR Process Tree Builder - 项目总结

## 项目概述

这是一个用于构建 UPR（Unit Process Record）生产过程树的 Python 工具。通过递归追溯 PostgreSQL 数据库中的 `tb_exchanges` 表，从指定的根节点开始，向上游追溯所有生产过程，最终生成完整的过程树可视化。

## 核心功能

1. **数据库连接**：连接到 PostgreSQL 数据库
2. **递归追溯**：从根节点递归查询所有上游 process
3. **循环检测**：防止无限递归
4. **多格式输出**：支持 Markdown 和 JSON 格式
5. **测试验证**：提供完整的测试工具

## 已创建文件

### 1. 核心程序文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `build_process_tree.py` | 主程序 | 构建过程树，生成 Markdown |
| `export_json.py` | JSON 导出器 | 生成 JSON 格式输出 |
| `test_connection.py` | 测试脚本 | 验证数据库连接和数据 |
| `quick_start.py` | 一键启动 | 自动化运行所有步骤 |

### 2. 配置文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `config.py` | 配置文件 | 数据库连接、根节点信息 |
| `requirements.txt` | 依赖清单 | Python 依赖包 |
| `.gitignore` | Git 忽略 | 忽略缓存和输出文件 |

### 3. 脚本文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `run.sh` | Shell 启动脚本 | Linux/macOS 一键启动 |

### 4. 文档文件

| 文件名 | 说明 | 内容 |
|--------|------|------|
| `README.md` | 项目介绍 | 快速入门、功能特点 |
| `USAGE.md` | 使用指南 | 详细用法、常见问题、扩展功能 |
| `PROJECT_STRUCTURE.md` | 项目结构 | 文件说明、技术架构、依赖关系 |
| `SUMMARY.md` | 本文件 | 项目总结、快速参考 |

## 使用方式

### 方式 1: 一键启动（推荐）

```bash
python quick_start.py
```

**流程：**
1. 自动检查并安装依赖
2. 运行数据库测试
3. 询问是否继续
4. 构建过程树
5. 生成输出文件

### 方式 2: Shell 脚本

```bash
chmod +x run.sh
./run.sh
```

### 方式 3: 手动运行

```bash
# 步骤 1: 安装依赖
pip install -r requirements.txt

# 步骤 2: 测试连接
python test_connection.py

# 步骤 3: 构建树（Markdown）
python build_process_tree.py

# 步骤 4: 导出 JSON（可选）
python export_json.py
```

## 配置说明

编辑 `config.py` 文件：

```python
# PostgreSQL 连接（必填）
PG_HOST = "101.227.234.12"
PG_PORT = 5432
PG_USER = "root"
PG_PASSWORD = "HiqProdDB@2024"
PG_DATABASE = "hiq_background_db"
PG_SCHEMA = "public"
PG_TABLE = "tb_exchanges"

# 数据版本（必填）
VERSION = "1.4.0"

# 根节点信息（必填）
ROOT_FLOW_ID = "a588dec8-0e04-3502-95e8-3492dc4f2263"
ROOT_PROCESS_ID = "6c59741f-b87e-40eb-8fa5-f04059fd9fa5"
```

## 输出文件

运行成功后会生成：

### 1. `process_tree.md` - Markdown 格式

```markdown
# UPR Process Tree Analysis

## Product (Root Flow)
- **Flow ID:** `a588dec8-0e04-3502-95e8-3492dc4f2263`

## Root Process (UPR)
- **Process ID:** `6c59741f-b87e-40eb-8fa5-f04059fd9fa5`

## Process Tree Structure

└─ **[6c59741f...]** Root Process
    ├─ **[4bea1726...]** Upstream Process 1 ← via `flow_id_1`
    │   └─ **[xxxxxxxx...]** Upstream Process X
    ├─ **[8fdb4514...]** Upstream Process 2
    └─ **[889505d7...]** Upstream Process 3
```

### 2. `process_tree.json` - JSON 格式

```json
{
  "metadata": {
    "version": "1.4.0",
    "total_processes": 15,
    "max_depth": 3
  },
  "tree": {
    "process_id": "6c59741f-b87e-40eb-8fa5-f04059fd9fa5",
    "children": [ ... ]
  }
}
```

## 技术实现

### 数据模型

```
Process (process_id)
    ↓ 通过 Exchange
    ├─ input: is_input = true, provider_id → 上游 Process
    └─ output: is_product = true → 产品 (flow_id)
```

### 递归逻辑

```python
def build_tree(process_id):
    # 1. 防止循环
    if process_id in visited:
        return
    
    # 2. 标记已访问
    visited.add(process_id)
    
    # 3. 查询上游
    upstream = query_upstream_exchanges(process_id)
    
    # 4. 递归处理
    for exchange in upstream:
        child = build_tree(exchange.provider_id)
        node.add_child(child)
    
    return node
```

### SQL 查询

```sql
SELECT process_id, flow_id, provider_id
FROM tb_exchanges
WHERE process_id = ?
  AND is_input = true
  AND provider_id IS NOT NULL
  AND is_deleted = false
  AND version = '1.4.0'
```

## 递归规则

根据 LCA/UPR 建模规范：

1. **节点是 process，不是 flow**
2. **边的含义**：`upstream_process ──(via flow)──▶ downstream_process`
3. **查询条件**：
   - `is_input = true`（输入流）
   - `provider_id IS NOT NULL`（有上游）
   - `is_deleted = false`（未删除）
   - `version = '1.4.0'`（指定版本）
4. **停止条件**：
   - 无上游输入
   - 检测到循环

## 测试流程

运行 `python test_connection.py` 会执行以下测试：

1. ✓ 数据库连接测试
2. ✓ 表存在性检查
3. ✓ 根节点数据验证
4. ✓ 上游查询逻辑测试
5. ✓ 数据统计分析

## 常见问题

### Q1: 数据库连接失败

```bash
# 检查网络
ping 101.227.234.12

# 检查端口
nc -zv 101.227.234.12 5432
```

### Q2: 找不到根节点

检查 `config.py` 中的：
- `ROOT_PROCESS_ID`
- `ROOT_FLOW_ID`
- `VERSION`

### Q3: 递归深度过大

在脚本开头添加：
```python
import sys
sys.setrecursionlimit(5000)
```

## 扩展功能

### 1. 批量分析

```python
roots = [
    ("flow_id_1", "process_id_1"),
    ("flow_id_2", "process_id_2"),
]

for flow_id, process_id in roots:
    # 修改 config
    # 运行 builder
    # 生成输出
```

### 2. 可视化

使用 Graphviz 生成图形：

```bash
pip install graphviz
```

### 3. 导出其他格式

- CSV
- Excel
- GraphML
- DOT

## 性能优化建议

1. **添加缓存**：使用 `@lru_cache` 缓存查询结果
2. **批量查询**：减少数据库往返次数
3. **连接池**：使用 `psycopg2.pool`
4. **限制深度**：设置最大递归深度

## 依赖关系图

```
config.py
    ↓
build_process_tree.py
    ↓
├─ test_connection.py
├─ export_json.py
└─ quick_start.py
    ↓
run.sh
```

## 快速参考

| 需求 | 运行命令 |
|------|----------|
| 快速开始 | `python quick_start.py` |
| 测试连接 | `python test_connection.py` |
| 构建树 | `python build_process_tree.py` |
| 导出 JSON | `python export_json.py` |
| Shell 启动 | `./run.sh` |

## 项目特点

✅ **完整性**：从数据验证到输出生成的完整流程
✅ **健壮性**：循环检测、错误处理、测试验证
✅ **易用性**：一键启动、清晰文档、示例丰富
✅ **可扩展**：模块化设计、接口清晰、易于扩展
✅ **专业性**：符合 LCA/UPR 建模规范

## 下一步

1. **首次使用**：
   - 编辑 `config.py`
   - 运行 `python quick_start.py`
   - 查看 `process_tree.md`

2. **深入了解**：
   - 阅读 `USAGE.md`
   - 阅读 `PROJECT_STRUCTURE.md`
   - 尝试扩展功能

3. **生产环境**：
   - 添加日志记录
   - 添加监控告警
   - 优化性能
   - 定期备份

## 联系方式

如有问题或建议，欢迎：
- 提交 Issue
- 提交 Pull Request
- 联系维护者

---

**Version:** 1.0.0  
**Date:** 2025-12-16  
**Author:** Data Engineering Team  
**License:** MIT

