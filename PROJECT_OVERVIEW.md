# HIQ UPR 项目结构概览

## 📁 项目结构

```
hiq_upr/
│
├── 📄 main.py                   # 主入口程序（推荐使用）
├── 📄 run.sh                    # Shell 启动脚本
├── 📄 requirements.txt          # Python 依赖
├── 📄 README.md                 # 项目说明文档
├── 📄 .gitignore                # Git 忽略配置
│
├── 📂 src/                      # 源代码目录
│   ├── config.py                # 配置文件（数据库连接、根节点）
│   ├── menu.py                  # 交互式菜单界面
│   ├── test_connection.py       # 数据库连接测试
│   │
│   ├── build_process_tree.py   # 核心：构建过程树
│   ├── build_main_chain.py     # 构建主链路
│   ├── export_json.py          # 导出 JSON 格式
│   ├── export_compact.py       # 导出紧凑格式（LLM 优化）
│   │
│   ├── analyze_statistics.py   # 统计分析工具
│   ├── batch_analysis.py       # 批量分析工具
│   ├── visualize_tree.py       # 图形可视化工具
│   ├── quick_start.py          # 快速启动脚本
│   └── debug_*.py              # 调试脚本
│
├── 📂 docs/                     # 文档目录
│   ├── 📂 guides/               # 使用指南
│   │   ├── USAGE.md            # 详细使用指南
│   │   ├── PROJECT_STRUCTURE.md # 项目结构说明（旧版）
│   │   ├── DUAL_MODE_GUIDE.md  # 双模式指南
│   │   ├── COMPACT_FORMAT_GUIDE.md # 紧凑格式指南
│   │   ├── COMPACT_FORMAT_USAGE.md # 紧凑格式使用
│   │   ├── QUICK_REFERENCE.md  # 快速参考
│   │   └── 主链路深度说明.md    # 主链路说明
│   │
│   ├── 📂 examples/             # 示例输出文件
│   │   ├── main_chain_*.md     # 主链路示例
│   │   ├── main_chain_*.txt    # 主链路紧凑格式
│   │   ├── process_tree_*.md   # 过程树示例
│   │   └── process_tree_*.txt  # 过程树紧凑格式
│   │
│   ├── CHANGELOG_DUAL_MODE.md  # 变更日志
│   ├── EXTENSIONS.md           # 扩展功能说明
│   ├── COMPARISON_EXAMPLE.md   # 对比示例
│   ├── FINAL_SUMMARY.md        # 最终总结
│   ├── IMPLEMENTATION_SUMMARY.md # 实现总结
│   └── SUMMARY.md              # 项目总结
│
└── 📂 output/                   # 输出目录（自动生成）
    ├── process_tree_*.md       # 过程树输出（Markdown）
    ├── process_tree_*.txt      # 过程树输出（紧凑格式）
    ├── main_chain_*.md         # 主链路输出
    └── *.json                  # JSON 格式输出
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库
编辑 `src/config.py`，设置数据库连接和根节点信息。

### 3. 运行程序

**推荐方式：**
```bash
python main.py
```

**或使用交互菜单：**
```bash
python src/menu.py
```

**或使用 Shell 脚本：**
```bash
./run.sh
```

## 📝 核心功能

### 核心模块
- **build_process_tree.py**: 主程序，构建完整的过程树
- **build_main_chain.py**: 构建主链路分析
- **export_compact.py**: 导出 LLM 优化的紧凑格式

### 辅助工具
- **test_connection.py**: 测试数据库连接
- **analyze_statistics.py**: 统计分析（层级、扇出度等）
- **visualize_tree.py**: 生成图形可视化（需要 Graphviz）
- **batch_analysis.py**: 批量处理多个产品

### 输出格式
1. **Markdown 格式**: 易读的树状结构
2. **JSON 格式**: 结构化数据
3. **紧凑格式**: 专为 LLM 处理优化

### 双模式支持
- **Skeleton Tree**: 单连接边（简化视图）
- **Full LCI Tree**: 多连接边（完整生命周期清单）

## 📚 文档指南

| 文档 | 说明 |
|------|------|
| `README.md` | 项目概述和快速入门 |
| `docs/guides/USAGE.md` | 详细使用说明 |
| `docs/guides/DUAL_MODE_GUIDE.md` | 双模式详解 |
| `docs/guides/COMPACT_FORMAT_USAGE.md` | 紧凑格式使用指南 |
| `docs/guides/QUICK_REFERENCE.md` | 快速参考手册 |

## 🔧 配置说明

所有配置在 `src/config.py` 文件中：

```python
# 数据库连接
PG_HOST = "your_host"
PG_PORT = 5432
PG_USER = "your_user"
PG_PASSWORD = "your_password"
PG_DATABASE = "your_database"

# 根节点信息
ROOT_FLOW_ID = "your_flow_id"
ROOT_PROCESS_ID = "your_process_id"
VERSION = "1.4.0"
```

## 📦 输出文件

所有生成的文件都保存在 `output/` 目录中：
- 过程树（Markdown 和紧凑格式）
- 主链路分析
- JSON 数据
- 统计报告
- 图形可视化（如果启用）

## ⚙️ 高级用法

### 命令行参数
```bash
# 生成双模式（Skeleton + Full LCI）
python src/build_process_tree.py --both

# 紧凑格式（双模式）
python src/export_compact.py --both

# 仅 ID（最小文件）
python src/export_compact.py --id-only
```

### 批量处理
```bash
python src/batch_analysis.py
```

### 图形可视化
```bash
python src/visualize_tree.py
```

## 🎯 最佳实践

1. **首次使用**: 运行 `python main.py` 使用交互式菜单
2. **测试连接**: 先运行 `python src/test_connection.py`
3. **LLM 处理**: 使用紧凑格式 `python src/export_compact.py --both`
4. **大型项目**: 使用 Skeleton 模式以减小文件大小
5. **完整分析**: 使用 Full LCI 模式查看所有依赖关系

## 📊 项目特点

- ✅ 递归追溯所有上游生产过程
- ✅ 循环检测防止无限递归
- ✅ 双模式生成（Skeleton/Full LCI）
- ✅ 多种输出格式（Markdown/JSON/紧凑格式）
- ✅ 统计分析和图形可视化
- ✅ 批量处理支持
- ✅ 模块化设计，易于扩展

## 🤝 贡献

欢迎提出问题和改进建议！

## 📄 许可证

请参考项目许可证文件。
