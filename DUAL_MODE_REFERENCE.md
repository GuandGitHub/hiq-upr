# 批量主链路分析 - 快速参考

## 两种运行模式

### 🏭 生产模式（默认）
```bash
python batch_main_chain.py
```
- **数据库**: hiq_background_db
- **数据表**: tb_exchanges, tb_processes, tb_flows, tb_units
- **输出**: `output/main_chain_*.txt`

### 🔧 建设模式
```bash
python batch_main_chain.py --mode editor
```
- **数据库**: hiq_editor
- **数据表**: tw_exchanges, tw_processes, tw_flows, tw_units
- **输出**: `output/editor/main_chain_*.txt`

## 配置说明

### config.py 配置项

```python
# 生产模式配置（默认）
PG_DATABASE = "hiq_background_db"
PG_SCHEMA = "public"
PG_TABLE = "tb_exchanges"

# 建设模式配置
EDITOR_DB_NAME = "hiq_editor"
EDITOR_SCHEMA = "public"
EDITOR_EXCHANGES_TABLE = "tw_exchanges"
EDITOR_PROCESSES_TABLE = "tw_processes"
EDITOR_FLOWS_TABLE = "tw_flows"
EDITOR_UNITS_TABLE = "tw_units"
```

## 常用命令

```bash
# 生产模式
python batch_main_chain.py
python batch_main_chain.py --mode production

# 建设模式
python batch_main_chain.py --mode editor
python batch_main_chain.py -m editor

# 自定义输出目录
python batch_main_chain.py --output custom_dir
python batch_main_chain.py -m editor -o custom_dir

# 查看帮助
python batch_main_chain.py --help
```

## 输出目录结构

```
output/
├── main_chain_6c59741f.txt    # 生产模式输出
├── main_chain_a588dec8.txt    # 生产模式输出
└── editor/                     # 建设模式目录
    ├── main_chain_02eef75e.txt
    └── main_chain_251da196.txt
```

## Process IDs 文件格式

### process_ids.txt
```text
# 生产环境的 Process
6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # 示例 Process 1
a588dec8-0e04-3502-95e8-3492dc4f2263  # 示例 Process 2

# 建设环境的 Process（使用 --mode editor）
02eef75e-bb2f-4283-95b4-249521aa2c12  # 编辑中的 Process
251da196-55f8-4c57-a783-9888cf33c626  # 编辑中的 Process
```

## 使用场景

### 场景1：分析生产数据
```bash
# 1. 编辑 process_ids.txt，添加生产环境的 process_id
# 2. 运行生产模式
python batch_main_chain.py

# 3. 查看结果
cat output/main_chain_*.txt
```

### 场景2：分析建设数据
```bash
# 1. 编辑 process_ids.txt，添加建设环境的 process_id
# 2. 运行建设模式
python batch_main_chain.py --mode editor

# 3. 查看结果
cat output/editor/main_chain_*.txt
```

### 场景3：同时分析两种环境
```bash
# 1. 在 process_ids.txt 中添加生产环境 ID
# 2. 运行生产模式
python batch_main_chain.py

# 3. 编辑 process_ids.txt，替换为建设环境 ID
# 4. 运行建设模式
python batch_main_chain.py --mode editor

# 结果分别保存在 output/ 和 output/editor/
```

## 常见问题

### Q: 如何切换模式？
A: 使用 `--mode` 参数：
- `python batch_main_chain.py` - 生产模式（默认）
- `python batch_main_chain.py --mode editor` - 建设模式

### Q: 两种模式的区别？
A: 
- **生产模式**: 从 hiq_background_db 读取正式数据
- **建设模式**: 从 hiq_editor 读取编辑中的数据（tw_ 前缀的表）

### Q: 输出文件保存在哪里？
A:
- 生产模式: `output/main_chain_*.txt`
- 建设模式: `output/editor/main_chain_*.txt`

### Q: 可以同时运行两种模式吗？
A: 可以，输出目录不同，不会互相覆盖。

### Q: 如何清理输出文件？
A:
```bash
# 清理生产模式输出
rm -f output/main_chain_*.txt

# 清理建设模式输出
rm -f output/editor/main_chain_*.txt

# 全部清理
rm -rf output/
```

## 性能提示

- 批量分析时，数据库连接会复用，提高效率
- 大量 process 分析建议分批进行
- 建议定期备份重要的分析结果

## 相关文档

- [BATCH_MAIN_CHAIN_GUIDE.md](BATCH_MAIN_CHAIN_GUIDE.md) - 完整使用指南
- [README.md](README.md) - 项目总体说明
- [docs/guides/](docs/guides/) - 其他使用指南
