# 使用指南

## 快速开始

### 方式 1: 使用 Python 脚本（推荐）

```bash
python3 quick_start.py
```

这个脚本会自动：
1. 检查并安装依赖
2. 测试数据库连接
3. 询问是否继续
4. 构建过程树并生成 Markdown

### 方式 2: 使用 Shell 脚本

```bash
./run.sh
```

### 方式 3: 手动运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 测试数据库连接
python test_connection.py

# 3. 构建过程树
python build_process_tree.py

# 4. （可选）同时生成 Markdown 和 JSON
python export_json.py
```

## 配置说明

编辑 `config.py` 文件，修改以下配置：

```python
# 数据库连接（必填）
PG_HOST = "101.227.234.12"
PG_PORT = 5432
PG_USER = "root"
PG_PASSWORD = "HiqProdDB@2024"
PG_DATABASE = "hiq_background_db"

# 根节点信息（必填）
ROOT_FLOW_ID = "a588dec8-0e04-3502-95e8-3492dc4f2263"
ROOT_PROCESS_ID = "6c59741f-b87e-40eb-8fa5-f04059fd9fa5"

# 数据版本（必填）
VERSION = "1.4.0"
```

## 输出文件

### Markdown 格式 (`process_tree.md`)

树状结构，包含：
- 产品信息
- 根过程信息
- 完整的过程树（带层级缩进）
- 统计信息（总节点数、最大深度）

示例：

```markdown
# UPR Process Tree Analysis

**Generated at:** 2025-12-16 10:30:45
**Version:** 1.4.0

---

## Product (Root Flow)
- **Flow ID:** `a588dec8-0e04-3502-95e8-3492dc4f2263`
- **Flow Name:** Product Name

## Root Process (UPR)
- **Process ID:** `6c59741f-b87e-40eb-8fa5-f04059fd9fa5`
- **Process Name:** Root Process Name

---

## Process Tree Structure

└─ **[6c59741f...]** Root Process Name
    ├─ **[4bea1726...]** Upstream Process 1 ← via `fa34fb13...` (Flow Name 1)
    │   └─ **[xxxxxxxx...]** Upstream Process X ← via `xxxxxxxx...` (Flow Name X)
    ├─ **[8fdb4514...]** Upstream Process 2 ← via `a588dec8...` (Flow Name 2)
    ├─ **[889505d7...]** Upstream Process 3 ← via `0f05cd98...` (Flow Name 3)
    └─ **[46044604...]** Upstream Process 4 ← via `aa50073b...` (Flow Name 4)

---

## Statistics
- **Total Processes:** 15
- **Max Depth:** 3
```

### JSON 格式 (`process_tree.json`)

结构化数据，方便程序处理：

```json
{
  "metadata": {
    "version": "1.4.0",
    "total_processes": 15,
    "max_depth": 3
  },
  "tree": {
    "process_id": "6c59741f-b87e-40eb-8fa5-f04059fd9fa5",
    "process_name": "Root Process Name",
    "level": 0,
    "children": [
      {
        "process_id": "4bea1726-...",
        "process_name": "Upstream Process 1",
        "flow_id": "fa34fb13-...",
        "flow_name": "Flow Name 1",
        "level": 1,
        "children": [],
        "children_count": 0
      }
    ],
    "children_count": 4
  }
}
```

## 脚本说明

### 1. `test_connection.py` - 数据库连接测试

在运行主程序前，先测试：
- 数据库连接是否正常
- 表是否存在
- 根节点数据是否存在
- 查询逻辑是否正确
- 数据统计

运行：
```bash
python test_connection.py
```

### 2. `build_process_tree.py` - 构建过程树（主程序）

核心功能：
- 连接 PostgreSQL 数据库
- 递归追溯上游过程
- 防止循环依赖
- 生成 Markdown 树状图

运行：
```bash
python build_process_tree.py
```

### 3. `export_json.py` - 导出 JSON 格式

同时生成 Markdown 和 JSON 两种格式的输出。

运行：
```bash
python export_json.py
```

### 4. `quick_start.py` - 一键启动

自动化运行所有步骤。

运行：
```bash
python quick_start.py
```

## 常见问题

### Q1: 数据库连接失败

**可能原因：**
- 网络不通
- 防火墙阻止
- 账号密码错误
- 数据库服务未启动

**解决方法：**
```bash
# 测试网络连通性
ping 101.227.234.12

# 测试端口是否开放
nc -zv 101.227.234.12 5432

# 或使用 telnet
telnet 101.227.234.12 5432
```

### Q2: 表不存在

**检查：**
- 表名是否正确：`public.tb_exchanges`
- 数据库是否正确：`hiq_background_db`
- 账号是否有权限访问该表

### Q3: 根节点数据不存在

**检查：**
- `ROOT_PROCESS_ID` 是否正确
- `ROOT_FLOW_ID` 是否正确
- `VERSION` 是否正确（1.4.0）
- 数据是否被标记为 `is_deleted = true`

### Q4: 递归深度过大

如果递归深度超过 Python 默认限制（通常是 1000），可以在脚本开头添加：

```python
import sys
sys.setrecursionlimit(5000)  # 增加递归限制
```

### Q5: 内存不足

对于大规模数据，可以：
1. 限制递归深度
2. 使用迭代而非递归
3. 分批处理

## 扩展功能

### 1. 自定义根节点

修改 `config.py`:

```python
ROOT_FLOW_ID = "你的-flow-id"
ROOT_PROCESS_ID = "你的-process-id"
VERSION = "你的-版本"
```

### 2. 批量分析多个根节点

创建 `batch_analysis.py`:

```python
import config
from build_process_tree import ProcessTreeBuilder

roots = [
    ("flow-id-1", "process-id-1"),
    ("flow-id-2", "process-id-2"),
    ("flow-id-3", "process-id-3"),
]

for i, (flow_id, process_id) in enumerate(roots):
    config.ROOT_FLOW_ID = flow_id
    config.ROOT_PROCESS_ID = process_id
    
    builder = ProcessTreeBuilder()
    builder.connect_db()
    
    root = builder.build_tree_recursive(process_id)
    builder.generate_markdown(root, f"process_tree_{i+1}.md")
    
    builder.close_db()
```

### 3. 导出为其他格式

可以扩展 `export_json.py`，添加：
- CSV 格式
- Excel 格式
- GraphML 格式（用于图可视化工具）
- DOT 格式（用于 Graphviz）

### 4. 可视化

使用 Graphviz 生成图形：

```python
from graphviz import Digraph

def export_graphviz(root, output_file="process_tree.png"):
    dot = Digraph(comment='Process Tree')
    
    def add_nodes(node):
        dot.node(node.process_id[:8], node.process_id[:8])
        for child in node.children:
            dot.node(child.process_id[:8], child.process_id[:8])
            dot.edge(child.process_id[:8], node.process_id[:8], 
                    label=child.flow_id[:8] if child.flow_id else "")
            add_nodes(child)
    
    add_nodes(root)
    dot.render(output_file, format='png', cleanup=True)

# 使用
export_graphviz(root)
```

## 性能优化

### 1. 添加缓存

对于频繁访问的数据，使用缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_process_name(process_id):
    # ...
```

### 2. 批量查询

减少数据库查询次数：

```python
def get_all_exchanges_batch(process_ids):
    query = """
        SELECT * FROM tb_exchanges 
        WHERE process_id = ANY(%s)
    """
    cursor.execute(query, (list(process_ids),))
    return cursor.fetchall()
```

### 3. 使用连接池

对于高并发场景：

```python
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(1, 20, **db_config)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT

