# HIQ UPR Process Tree Builder

## 简介

从 PostgreSQL 数据库的 `tb_exchanges` 表中，以指定的产品和 UPR 过程为根节点，递归追溯所有上游生产过程（process），构建完整的"生产过程树（Process Tree）"，并生成 Markdown 格式的树状逻辑图。

这个工具专为 LCA/UPR 建模设计，帮助数据工程师快速理解和可视化产品的完整生产链条。

## 功能特点

### 核心功能
- ✅ **递归追溯**：自动追溯所有上游生产过程，直到叶子节点
- ✅ **循环检测**：智能检测并防止循环依赖
- ✅ **双模式生成**：支持 Skeleton Tree（单边）和 Full LCI Tree（多边）
- ✅ **多种输出**：支持 Markdown 和 JSON 两种格式
- ✅ **关系可视化**：清晰展示 process 和 flow 的关系

### 扩展功能
- 📊 **统计分析**：层级分布、扇出度、关键路径等深度分析
- 🎨 **图形可视化**：使用 Graphviz 生成 PNG/SVG/PDF 图形
- 📦 **批量处理**：支持批量分析多个产品/过程
- 🎯 **交互菜单**：友好的菜单界面，易于使用

### 辅助功能
- ✅ **测试工具**：内置数据库连接和数据验证测试
- ✅ **一键启动**：快速启动脚本，自动化流程
- ✅ **易于扩展**：模块化设计，便于添加新功能

## 数据模型

### 递归规则

1. **树的节点是 process（process_id），不是 flow**
2. **一条边表示**：
   ```
   upstream_process ──(via flow_id)──▶ downstream_process
   ```
3. **对某个 process，查找其所有满足以下条件的 input exchange**：
   - `is_input = true`
   - `provider_id IS NOT NULL`
   - `is_deleted = false`
   - `version = '1.4.0'`
4. **对每一条 input exchange**：
   - `provider_id` 作为上游 process
   - 递归继续向上追溯
5. **停止递归的条件**：
   - 查不到任何满足条件的 input exchange
   - `provider_id` 为空
   - 命中已访问的 process（防止循环）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `src/config.py` 文件，设置数据库连接和根节点信息：

```python
# PostgreSQL Connection
PG_HOST = "101.227.234.12"
PG_PORT = 5432
PG_USER = "root"
PG_PASSWORD = "HiqProdDB@2024"
PG_DATABASE = "hiq_background_db"

# Root node information
ROOT_FLOW_ID = "a588dec8-0e04-3502-95e8-3492dc4f2263"
ROOT_PROCESS_ID = "6c59741f-b87e-40eb-8fa5-f04059fd9fa5"
VERSION = "1.4.0"
```

### 3. 运行程序

**🎯 推荐方式：使用主程序**
```bash
python main.py
```

**🚀 或使用交互菜单**
```bash
python src/menu.py
```

**🔧 或使用 Shell 脚本（Linux/macOS）**
```bash
chmod +x run.sh
./run.sh
```

**📝 或手动运行**
```bash
# 测试连接
python src/test_connection.py

# 构建树（Skeleton 模式）
python src/build_process_tree.py

# 构建树（同时生成 Skeleton 和 Full LCI 两种模式）
python src/build_process_tree.py --both

# 构建主链路（单个 process）
python src/build_main_chain.py

# 批量主链路分析（多个 process）
python batch_main_chain.py

# 同时生成 JSON
python src/export_json.py

# 统计分析
python src/analyze_statistics.py

# 可视化（需要 Graphviz）
python src/visualize_tree.py

# 批量分析
python src/batch_analysis.py
```

## 批量主链路分析 🆕

### 快速使用

1. **编辑 `process_ids.txt`** 添加要分析的 process_id：
```text
6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # Process 1
a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Process 2
```

2. **选择运行模式**：

**生产模式**（从 hiq_background_db 读取）：
```bash
python batch_main_chain.py
```

**建设模式**（从 hiq_editor 读取 tw_exchanges）：
```bash
python batch_main_chain.py --mode editor
```

3. **查看结果**：
- 生产模式：`output/main_chain_[id].txt`
- 建设模式：`output/editor/main_chain_[id].txt`

> 📖 详细使用说明请查看 [BATCH_MAIN_CHAIN_GUIDE.md](BATCH_MAIN_CHAIN_GUIDE.md)

## 项目结构

```
hiq_upr/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python 依赖
├── main.py                      # 主入口程序
├── run.sh                       # Shell 启动脚本
├── process_ids.txt              # Process ID 列表（批量分析用）
├── batch_main_chain.py          # 批量主链路分析脚本
├── BATCH_MAIN_CHAIN_GUIDE.md    # 批量分析使用指南
│
├── src/                         # 源代码目录
│   ├── config.py                # 配置文件
│   ├── build_process_tree.py   # 构建过程树
│   ├── build_main_chain.py     # 构建主链路
│   ├── export_json.py          # 导出 JSON
│   ├── export_compact.py       # 导出紧凑格式
│   ├── analyze_statistics.py   # 统计分析
│   ├── batch_analysis.py       # 批量分析
│   ├── visualize_tree.py       # 图形可视化
│   ├── menu.py                 # 交互菜单
│   ├── quick_start.py          # 快速启动
│   └── test_connection.py      # 连接测试
│
├── docs/                        # 文档目录
│   ├── guides/                  # 使用指南
│   │   ├── USAGE.md            # 详细使用指南
│   │   ├── PROJECT_STRUCTURE.md # 项目结构说明
│   │   ├── DUAL_MODE_GUIDE.md  # 双模式指南
│   │   ├── COMPACT_FORMAT_GUIDE.md # 紧凑格式指南
│   │   ├── COMPACT_FORMAT_USAGE.md # 紧凑格式使用
│   │   ├── QUICK_REFERENCE.md  # 快速参考
│   │   └── 主链路深度说明.md    # 主链路说明
│   ├── examples/                # 示例输出
│   ├── CHANGELOG_DUAL_MODE.md  # 变更日志
│   ├── EXTENSIONS.md           # 扩展功能
│   ├── COMPARISON_EXAMPLE.md   # 对比示例
│   └── SUMMARY.md              # 总结文档
│
└── output/                      # 输出目录（自动生成）
    ├── process_tree_*.md       # 过程树输出
    ├── process_tree_*.txt      # 紧凑格式输出
    └── *.json                  # JSON 输出
```

## 输出示例

### 单模式输出（默认）
运行 `python src/build_process_tree.py` 会生成：
- `output/process_tree.md` - Skeleton Tree（单连接边）

### 双模式输出
运行 `python src/build_process_tree.py --both` 会生成：
- `output/process_tree_skeleton_[id].md` - Skeleton Tree（单连接边）
- `output/process_tree_full_lci_[id].md` - Full LCI Tree（多连接边）

### 紧凑格式（推荐用于 LLM）
运行 `python src/export_compact.py --both` 会生成：
- `output/process_tree_skeleton_compact_[id].txt` - 紧凑格式，包含完整 ID 和名称
- `output/process_tree_full_lci_compact_[id].txt` - 紧凑格式，包含完整 ID 和名称

### 其他格式
- `output/process_tree.json` - JSON 格式的结构化数据（运行 `python src/export_json.py`）

> 📖 详细了解两种模式的区别，请查看 [docs/guides/DUAL_MODE_GUIDE.md](docs/guides/DUAL_MODE_GUIDE.md)  
> 🤖 LLM 处理请使用紧凑格式，查看 [docs/guides/COMPACT_FORMAT_USAGE.md](docs/guides/COMPACT_FORMAT_USAGE.md)

## 输出格式示例

生成的 Markdown 文件包含以下内容：

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

## 数据库表结构

### tb_exchanges

关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `process_id` | UUID | 当前过程（UPR） |
| `flow_id` | UUID | 过程涉及的 flow |
| `is_input` | Boolean | 是否为输入（true 表示原料/能源） |
| `is_product` | Boolean | 是否为最终产品（reference flow） |
| `provider_id` | UUID | 提供该输入 flow 的上游 process |
| `is_deleted` | Boolean | 逻辑删除标记 |
| `version` | String | 数据版本 |

## 技术实现

- **语言**: Python 3.x
- **数据库驱动**: psycopg2
- **算法**: 深度优先搜索（DFS）
- **数据结构**: 树形结构（自定义 ProcessTreeNode 类）

## 注意事项

1. **循环检测**: 脚本会自动检测循环依赖，避免无限递归
2. **性能**: 对于大规模数据，递归深度可能较大，请注意内存使用
3. **数据版本**: 确保查询的 version 参数与数据库中的版本一致
4. **网络连接**: 确保能够访问目标数据库

## 扩展功能

如果需要扩展功能，可以：

1. 添加更多的过滤条件（如按 location、category 等）
2. 导出为其他格式（JSON、CSV、HTML 等）
3. 可视化图形（使用 graphviz、d3.js 等）
4. 添加缓存机制提升性能
5. 支持批量分析多个根节点

## 文档

- [README.md](README.md) - 本文件，快速入门
- [DUAL_MODE_GUIDE.md](DUAL_MODE_GUIDE.md) - 🆕 双模式生成指南（Skeleton vs Full LCI）
- [USAGE.md](USAGE.md) - 详细使用指南
- [EXTENSIONS.md](EXTENSIONS.md) - 扩展功能说明
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构说明
- [SUMMARY.md](SUMMARY.md) - 项目总结

## 脚本说明

| 脚本 | 功能 | 说明 |
|------|------|------|
| `menu.py` | 🎯 交互菜单 | 推荐使用 |
| `quick_start.py` | 🚀 快速开始 | 一键测试+构建 |
| `build_process_tree.py` | 🌲 构建树 | 生成 Markdown |
| `export_json.py` | 📊 导出JSON | 生成 JSON |
| `test_connection.py` | 🔍 测试连接 | 验证配置 |
| `analyze_statistics.py` | 📈 统计分析 | 深度分析 |
| `visualize_tree.py` | 🎨 可视化 | 生成图形 |
| `batch_analysis.py` | 📦 批量分析 | 批量处理 |

## 技术栈

- **语言**: Python 3.x
- **数据库**: PostgreSQL
- **数据库驱动**: psycopg2
- **算法**: 深度优先搜索（DFS）

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT

