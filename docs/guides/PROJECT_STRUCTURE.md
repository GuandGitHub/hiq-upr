# 项目结构说明

## 文件清单

```
hiq_upr/
├── README.md                   # 项目介绍和快速入门
├── USAGE.md                    # 详细使用指南
├── PROJECT_STRUCTURE.md        # 本文件 - 项目结构说明
├── requirements.txt            # Python 依赖
├── .gitignore                  # Git 忽略文件
│
├── config.py                   # 配置文件（数据库连接、根节点等）
│
├── build_process_tree.py       # 主程序 - 构建过程树
├── export_json.py              # 导出 JSON 格式
├── test_connection.py          # 数据库连接测试
├── quick_start.py              # 一键启动脚本
├── run.sh                      # Shell 启动脚本
│
└── 输出文件（运行后生成）
    ├── process_tree.md         # Markdown 格式的树状图
    └── process_tree.json       # JSON 格式的树状图
```

## 文件说明

### 核心文件

#### 1. `config.py`
**配置文件** - 包含所有可配置参数

```python
# 数据库连接
PG_HOST = "101.227.234.12"
PG_PORT = 5432
...

# 根节点信息
ROOT_FLOW_ID = "..."
ROOT_PROCESS_ID = "..."
VERSION = "1.4.0"
```

**使用场景：**
- 更换数据库连接
- 更换根节点
- 更换数据版本

---

#### 2. `build_process_tree.py`
**主程序** - 核心功能实现

**主要类：**
- `ProcessTreeNode`: 树节点数据结构
- `ProcessTreeBuilder`: 构建过程树的主类

**主要方法：**
- `connect_db()`: 连接数据库
- `get_upstream_exchanges()`: 查询上游 exchanges
- `build_tree_recursive()`: 递归构建树
- `generate_markdown()`: 生成 Markdown 输出
- `run()`: 运行完整流程

**使用场景：**
- 构建单个过程树
- 生成 Markdown 格式输出

**运行：**
```bash
python build_process_tree.py
```

---

#### 3. `export_json.py`
**JSON 导出器** - 支持 JSON 格式输出

**主要类：**
- `JSONExporter`: JSON 导出功能

**使用场景：**
- 需要机器可读的结构化数据
- 需要进一步程序处理
- 需要导入到其他系统

**运行：**
```bash
python export_json.py
```

**输出示例：**
```json
{
  "metadata": {
    "version": "1.4.0",
    "total_processes": 15,
    "max_depth": 3
  },
  "tree": { ... }
}
```

---

#### 4. `test_connection.py`
**测试脚本** - 验证配置和数据

**测试项目：**
1. 数据库连接测试
2. 表存在性检查
3. 根节点数据验证
4. 上游查询逻辑测试
5. 数据统计分析

**使用场景：**
- 首次运行前的验证
- 排查问题
- 了解数据概况

**运行：**
```bash
python test_connection.py
```

---

#### 5. `quick_start.py`
**一键启动** - 自动化运行所有步骤

**执行流程：**
1. 检查并安装依赖
2. 运行数据库测试
3. 询问用户是否继续
4. 构建过程树
5. 显示结果

**使用场景：**
- 快速开始
- 自动化流程
- 新手友好

**运行：**
```bash
python quick_start.py
```

---

#### 6. `run.sh`
**Shell 脚本** - Bash 版本的启动脚本

**功能：**
- 检查 Python 环境
- 安装依赖
- 运行测试和构建

**使用场景：**
- Linux/macOS 环境
- 脚本化部署

**运行：**
```bash
chmod +x run.sh
./run.sh
```

---

### 文档文件

#### 1. `README.md`
项目主文档，包含：
- 项目简介
- 功能特点
- 快速开始
- 数据模型说明
- 基本用法

#### 2. `USAGE.md`
详细使用指南，包含：
- 多种运行方式
- 配置说明
- 输出格式说明
- 常见问题
- 扩展功能
- 性能优化

#### 3. `PROJECT_STRUCTURE.md`
本文件，包含：
- 文件清单
- 文件说明
- 使用场景
- 技术架构

---

### 配置文件

#### 1. `requirements.txt`
Python 依赖清单

```
psycopg2-binary==2.9.9
```

#### 2. `.gitignore`
Git 忽略规则，避免提交：
- Python 缓存文件
- 虚拟环境
- 输出文件
- 敏感配置

---

## 技术架构

### 数据流

```
PostgreSQL (tb_exchanges)
    ↓
[SQL Query] - 查询上游 exchanges
    ↓
[Python - psycopg2] - 数据库连接
    ↓
[ProcessTreeBuilder] - 递归构建树
    ↓
[ProcessTreeNode] - 树形数据结构
    ↓
[Markdown Generator] - 生成树状图
    ↓
process_tree.md
```

### 递归算法

```
function build_tree(process_id):
    if process_id in visited:
        return  # 防止循环
    
    visited.add(process_id)
    node = create_node(process_id)
    
    # 查询所有上游输入
    upstream = query_upstream_exchanges(process_id)
    
    for exchange in upstream:
        provider_id = exchange.provider_id
        child_node = build_tree(provider_id)  # 递归
        node.add_child(child_node)
    
    return node
```

### SQL 查询逻辑

```sql
SELECT 
    process_id,
    flow_id,
    provider_id
FROM tb_exchanges
WHERE process_id = ?
  AND is_input = true
  AND provider_id IS NOT NULL
  AND is_deleted = false
  AND version = '1.4.0'
```

---

## 依赖关系

```
build_process_tree.py
    └── config.py

export_json.py
    ├── config.py
    └── build_process_tree.py

test_connection.py
    └── config.py

quick_start.py
    ├── test_connection.py
    └── build_process_tree.py

run.sh
    ├── test_connection.py
    └── build_process_tree.py
```

---

## 使用流程

### 流程 1: 首次使用

```
1. 配置 config.py
   ↓
2. 运行 python quick_start.py
   ↓
3. 自动测试连接
   ↓
4. 询问是否继续
   ↓
5. 构建过程树
   ↓
6. 生成 process_tree.md
```

### 流程 2: 问题排查

```
1. 运行 python test_connection.py
   ↓
2. 查看哪个测试失败
   ↓
3. 根据错误信息修改配置
   ↓
4. 重新测试
```

### 流程 3: 批量处理

```
1. 准备多个根节点列表
   ↓
2. 循环调用 build_process_tree
   ↓
3. 生成多个输出文件
```

---

## 扩展点

### 1. 添加新的输出格式

在 `export_json.py` 基础上，可以添加：
- CSV 导出器
- Excel 导出器
- GraphML 导出器
- HTML 导出器

### 2. 添加可视化

使用图形库：
- Graphviz
- Plotly
- D3.js
- Cytoscape

### 3. 添加过滤条件

在查询中添加更多条件：
- 按 location 过滤
- 按 category 过滤
- 按日期范围过滤

### 4. 性能优化

- 添加缓存机制
- 使用连接池
- 批量查询
- 并行处理

---

## 最佳实践

### 1. 首次使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 编辑配置
vim config.py

# 3. 测试连接
python test_connection.py

# 4. 构建树
python build_process_tree.py
```

### 2. 日常使用

```bash
# 使用快速启动
python quick_start.py
```

### 3. 调试问题

```bash
# 运行测试脚本查看详细信息
python test_connection.py

# 查看数据库日志
# 检查网络连接
ping 101.227.234.12
nc -zv 101.227.234.12 5432
```

---

## 版本历史

- **v1.0.0** (2025-12-16)
  - 初始版本
  - 支持 Markdown 输出
  - 支持 JSON 输出
  - 添加测试脚本
  - 添加快速启动脚本

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

提交代码前请确保：
1. 代码符合 PEP 8 规范
2. 添加必要的注释
3. 更新相关文档
4. 通过所有测试

---

## License

MIT

