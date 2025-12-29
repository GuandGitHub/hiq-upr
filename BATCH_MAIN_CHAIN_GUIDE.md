# 批量主链路分析使用指南

## 快速开始

### 1. 准备 Process ID 列表

编辑 `process_ids.txt` 文件，添加您要分析的 process_id（每行一个）：

```text
# 示例：添加您的 process_id
6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # Process 1 说明
a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Process 2 说明

# 可以添加更多...
```

**注意事项：**
- 每行一个完整的 UUID（36位，包含4个连字符）
- 支持注释（以 `#` 开头）
- 空行会被自动忽略
- Process ID 后可以添加注释说明

### 2. 选择运行模式

支持两种模式：

#### 🏭 生产模式（默认）
从 `hiq_background_db` 数据库读取数据
```bash
python batch_main_chain.py
# 或明确指定
python batch_main_chain.py --mode production
```
输出到：`output/`

#### 🔧 建设模式
从 `hiq_editor` 数据库读取数据（tw_exchanges, tw_processes）
```bash
python batch_main_chain.py --mode editor
```
输出到：`output/editor/`

### 3. 查看结果

生成的文件保存在相应的输出目录中：
- **生产模式**: `output/main_chain_[process_id前8位].txt`
- **建设模式**: `output/editor/main_chain_[process_id前8位].txt`

## 文件说明

### process_ids.txt
存放要分析的 process_id 列表。格式示例：

```text
# UPR 主链路分析 - Process ID 列表
# 
# 使用说明：
# 1. 每行一个 process_id（完整的 UUID）
# 2. 可以添加注释（以 # 开头）
# 3. 空行会被忽略

# 项目A的主链路分析
6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # 产品A - 生产过程
a1b2c3d4-e5f6-7890-abcd-ef1234567890  # 产品B - 组装过程

# 项目B的主链路分析
b2c3d4e5-f678-9abc-def0-123456789abc  # 原料C - 提取过程
```

### batch_main_chain.py
批量主链路分析脚本，功能：
- 自动读取 `process_ids.txt` 文件
- 为每个 process_id 生成主链路
- 生成 Markdown 和紧凑格式两种输出
- 提供详细的进度和错误报告

## 使用示例

### 示例1：生产模式分析

1. 在 `process_ids.txt` 中添加：
```text
6c59741f-b87e-40eb-8fa5-f04059fd9fa5
```

2. 运行生产模式（默认）：
```bash
python batch_main_chain.py
```

3. 查看结果：
```bash
ls output/main_chain_6c59741f.txt
```

### 示例2：建设模式分析

1. 在 `process_ids.txt` 中添加：
```text
a1b2c3d4-e5f6-7890-abcd-ef1234567890  # 建设中的 Process
```

2. 运行建设模式：
```bash
python batch_main_chain.py --mode editor
```

3. 查看结果：
```bash
ls output/editor/main_chain_a1b2c3d4.txt
```

### 示例3：批量分析多个 Process

1. 在 `process_ids.txt` 中添加多个：
```text
# 生产环境数据
6c59741f-b87e-40eb-8fa5-f04059fd9fa5  # Process 1
a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Process 2
b2c3d4e5-f678-9abc-def0-123456789abc  # Process 3
```

2. 运行批量分析：
```bash
# 生产模式
python batch_main_chain.py

# 或建设模式
python batch_main_chain.py --mode editor
```

3. 查看所有结果：
```bash
# 生产模式输出
ls -lh output/main_chain_*

# 建设模式输出
ls -lh output/editor/main_chain_*
```

### 示例4：自定义输出目录

```bash
python batch_main_chain.py --mode editor --output custom_output
```

## 输出格式

### TXT 格式（紧凑格式）
专为 LLM 优化：
- 简洁的树状结构
- 完整的 UUID（不截断）
- 关键指标（value、GWP、贡献度）
- 易于解析和分析

## 运行模式详解

### 🏭 生产模式 (production)
- **数据源**: `hiq_background_db` 数据库
- **数据表**: `tb_exchanges`, `tb_processes`, `tb_flows`, `tb_units`
- **输出位置**: `output/`
- **使用场景**: 分析生产环境的正式数据
- **命令**: `python batch_main_chain.py` 或 `python batch_main_chain.py --mode production`

### 🔧 建设模式 (editor)
- **数据源**: `hiq_editor` 数据库
- **数据表**: `tw_exchanges`, `tw_processes`, `tw_flows`, `tw_units`
- **输出位置**: `output/editor/`
- **使用场景**: 分析建设中、编辑中的数据
- **命令**: `python batch_main_chain.py --mode editor`

## 高级功能

### 命令行参数

```bash
# 查看帮助
python batch_main_chain.py --help

# 指定运行模式
python batch_main_chain.py --mode production  # 生产模式
python batch_main_chain.py --mode editor      # 建设模式
python batch_main_chain.py -m editor          # 简写

# 自定义输出目录
python batch_main_chain.py --output my_output
python batch_main_chain.py -o my_output
python batch_main_chain.py --mode editor --output custom_editor_output
```

### 单独运行主链路分析

如果只需要分析 config.py 中配置的默认 process：

```bash
python src/build_main_chain.py
```

### 与交互菜单集成

通过主菜单选择"构建主链路"：

```bash
python main.py
# 选择：2) 构建主链路
```

## 常见问题

### Q: 如何知道 process_id 是否有效？
A: 运行后脚本会验证 UUID 格式，无效的 ID 会被跳过并显示警告。

### Q: 分析失败怎么办？
A: 检查：
1. Process ID 是否正确
2. 数据库连接是否正常（运行 `python src/test_connection.py`）
3. Process 在数据库中是否存在

### Q: 如何批量导出到其他格式？
A: 可以使用生成的 Markdown 文件，通过其他工具转换为 PDF、HTML 等格式。

### Q: 分析需要多长时间？
A: 取决于：
- Process 的复杂度（上游层级数量）
- 数据库查询速度
- 一般每个 process 需要几秒到几十秒

## 技巧与最佳实践

1. **分组管理**：使用注释对 process_id 进行分组
   ```text
   # === 项目A ===
   id1...
   id2...
   
   # === 项目B ===
   id3...
   id4...
   ```

2. **增量分析**：已分析的 process_id 可以注释掉
   ```text
   # id1...  # 已完成
   id2...    # 待分析
   ```

3. **备份重要结果**：定期备份 `output/` 目录

4. **并行分析**：对于大量 process，可以分批次在不同终端运行

## 相关命令

```bash
# 生产模式（默认）
python batch_main_chain.py

# 建设模式
python batch_main_chain.py --mode editor

# 查看帮助
python batch_main_chain.py --help

# 测试数据库连接
python src/test_connection.py

# 单个主链路分析（生产模式）
python src/build_main_chain.py

# 查看输出文件
ls -lh output/              # 生产模式输出
ls -lh output/editor/       # 建设模式输出

# 清理输出目录
rm -rf output/main_chain_*
rm -rf output/editor/main_chain_*
```

## 项目结构

```
hiq_upr/
├── process_ids.txt          # Process ID 列表（您需要编辑）
├── batch_main_chain.py      # 批量分析脚本（支持双模式）
├── src/
│   ├── config.py            # 配置文件（包含双模式配置）
│   └── build_main_chain.py  # 主链路构建器（支持双模式）
└── output/                  # 输出目录
    ├── main_chain_*.txt     # 生产模式输出
    └── editor/              # 建设模式输出目录
        └── main_chain_*.txt # 建设模式输出
```

## 支持

如有问题，请查看：
- README.md - 项目总体说明
- docs/guides/ - 详细使用指南
- 运行日志中的错误信息
