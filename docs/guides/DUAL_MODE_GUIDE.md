# 双模式生成指南 - Skeleton Tree vs Full LCI Tree

## 📋 概述

本工具现在支持两种过程树生成模式：

1. **Skeleton Tree（骨架树）** - 单连接边模式
2. **Full LCI Tree（完整 LCI 树）** - 多连接边模式

---

## 🎯 两种模式的区别

### Skeleton Tree（单连接边）

**特点：**
- 每个 `upstream → downstream` 关系只保留**一条代表性的 flow**
- 树结构简洁，便于快速理解供应链骨架
- 文件较小，易于浏览

**适用场景：**
- 快速了解产品的主要供应链结构
- 识别关键的上游依赖
- 生成概览性报告

**示例输出：**
```markdown
└─ **[6c59741f...]** 乙烯,煤基甲醇制
    ├─ **[889505d7...]** 运输,货运,卡车 ← via `0f05cd98...` (运输，货运，卡车)
    ├─ **[540882cb...]** 柴油,原油精炼 ← via `7e47d17d...` (柴油)
    └─ **[46044604...]** 甲醇,煤制 ← via `aa50073b...` (甲醇)
```

---

### Full LCI Tree（多连接边）

**特点：**
- 每个 `upstream → downstream` 关系保留**所有 flow**
- 完整展示所有物料、能源流动
- 符合 LCI（Life Cycle Inventory）数据完整性要求

**适用场景：**
- 完整的生命周期清单（LCI）分析
- 详细的物料流分析
- 精确的环境影响评估
- 学术研究和数据审计

**示例输出：**
```markdown
└─ **[6c59741f...]** 乙烯,煤基甲醇制
    ├─ **[889505d7...]** 运输,货运,卡车
    │     → via `0f05cd98...` (运输，货运，卡车)
    │     → via `78237e07...` (运输，货运，卡车，国V)
    ├─ **[540882cb...]** 柴油,原油精炼
    │     → via `7e47d17d...` (柴油)
    │     → via `a1b2c3d4...` (柴油，低硫)
    │     → via `e5f6g7h8...` (柴油，标准)
    └─ **[46044604...]** 甲醇,煤制
          → via `aa50073b...` (甲醇)
          → via `bb60184c...` (甲醇，工业级)
```

---

## 🚀 使用方法

### 方式 1：只生成 Skeleton Tree（默认）

```bash
python build_process_tree.py
```

**输出文件：**
- `process_tree.md`

---

### 方式 2：同时生成两种模式

```bash
python build_process_tree.py --both
```

**输出文件：**
- `process_tree_skeleton_a588dec8.md` - Skeleton Tree
- `process_tree_full_lci_a588dec8.md` - Full LCI Tree

> 注：文件名中的 `a588dec8` 是根节点 flow_id 的前8位

---

## 📊 数据结构对比

### Skeleton Tree 数据结构

```python
class ProcessTreeNode:
    process_id: str          # 过程 ID
    flow_id: str            # 单条代表性 flow
    children: List[Node]    # 子节点列表
```

**边的表示：**
```
(upstream_process_id, downstream_process_id) → one flow_id
```

---

### Full LCI Tree 数据结构

```python
class ProcessTreeNode:
    process_id: str          # 过程 ID
    flows: List[str]        # 所有 flow_id 列表
    children: List[Node]    # 子节点列表
```

**边的表示：**
```
(upstream_process_id, downstream_process_id) → [flow_id_1, flow_id_2, ...]
```

---

## 🔍 技术实现细节

### 递归规则（两种模式完全一致）

```sql
SELECT process_id, flow_id, provider_id
FROM tb_exchanges
WHERE process_id = ?
  AND is_input = true
  AND provider_id IS NOT NULL
  AND is_deleted = false
  AND version = '1.4.0'
```

### 关键区别

#### Skeleton 模式
```python
# 每个 provider 只取第一条 exchange
for exchange in upstream_exchanges:
    upstream_process_id = exchange['provider_id']
    upstream_flow_id = exchange['flow_id']
    
    child = build_tree(upstream_process_id, upstream_flow_id)
    node.add_child(child)
```

#### Full LCI 模式
```python
# 按 provider_id 分组，收集所有 flow
provider_flows = defaultdict(list)
for exchange in upstream_exchanges:
    provider_flows[exchange['provider_id']].append(exchange['flow_id'])

# 每个 provider 创建一个节点，但包含所有 flow
for upstream_process_id, flow_ids in provider_flows.items():
    child = build_tree(upstream_process_id, flow_ids[0])
    for fid in flow_ids:
        child.add_flow(fid)  # 添加所有 flow
    node.add_child(child)
```

---

## 📈 统计信息对比

### Skeleton Tree 统计

```markdown
## Statistics
- **Total Processes:** 1,234
- **Max Depth:** 15
```

### Full LCI Tree 统计

```markdown
## Statistics
- **Total Processes:** 1,234
- **Max Depth:** 15
- **Total Edges:** 2,456
- **Total Flows:** 5,678
- **Avg Flows per Edge:** 2.31
```

---

## 🎨 输出格式示例

### Skeleton Tree 输出格式

```markdown
└─ **[process_id]** process_name ← via `flow_id` (flow_name)
    ├─ **[upstream_1]** upstream_name_1 ← via `flow_1` (flow_name_1)
    └─ **[upstream_2]** upstream_name_2 ← via `flow_2` (flow_name_2)
```

### Full LCI Tree 输出格式

```markdown
└─ **[process_id]** process_name
    ├─ **[upstream_1]** upstream_name_1
    │     → via `flow_1a` (flow_name_1a)
    │     → via `flow_1b` (flow_name_1b)
    │     → via `flow_1c` (flow_name_1c)
    └─ **[upstream_2]** upstream_name_2
          → via `flow_2a` (flow_name_2a)
          → via `flow_2b` (flow_name_2b)
```

---

## 💡 最佳实践

### 1. 选择合适的模式

- **快速分析** → 使用 Skeleton Tree
- **完整 LCI** → 使用 Full LCI Tree
- **对比分析** → 同时生成两个版本

### 2. 文件大小预估

| 模式 | 相对大小 | 典型文件大小 |
|------|---------|-------------|
| Skeleton | 1x | 5-10 MB |
| Full LCI | 2-3x | 15-30 MB |

### 3. 性能考虑

- Skeleton Tree：更快，内存占用小
- Full LCI Tree：稍慢，但仍在可接受范围内
- 两种模式都使用相同的循环检测机制

---

## 🔧 配置选项

在 `config.py` 中配置：

```python
# 根节点信息
ROOT_FLOW_ID = "a588dec8-0e04-3502-95e8-3492dc4f2263"
ROOT_PROCESS_ID = "6c59741f-b87e-40eb-8fa5-f04059fd9fa5"
VERSION = "1.4.0"
```

---

## 📝 命令行参数

```bash
# 只生成 Skeleton Tree
python build_process_tree.py

# 同时生成两种模式
python build_process_tree.py --both
python build_process_tree.py -b

# 使用交互菜单
python menu.py
```

---

## 🎯 应用场景

### Skeleton Tree 适用场景

1. **供应链可视化**
   - 快速识别主要供应商
   - 理解产品结构
   
2. **教学演示**
   - 简化的树结构更易理解
   - 适合课堂展示

3. **初步评估**
   - 快速筛选关键过程
   - 识别热点问题

### Full LCI Tree 适用场景

1. **LCA 研究**
   - 完整的清单数据
   - 精确的环境影响计算

2. **合规审计**
   - 完整的物料追溯
   - 数据完整性验证

3. **详细分析**
   - 多场景对比
   - 敏感性分析

---

## 🔄 迁移指南

如果您之前使用旧版本，现在的变化：

### 向后兼容

✅ **完全兼容** - 默认行为保持不变
- 不带参数运行 → 生成 Skeleton Tree（与之前一致）
- 文件名：`process_tree.md`（与之前一致）

### 新功能

✨ **可选增强** - 需要显式启用
- 使用 `--both` 参数 → 生成两个版本
- 新文件名包含 flow_id 前缀

---

## 📚 相关文档

- [README.md](README.md) - 项目介绍
- [USAGE.md](USAGE.md) - 详细使用指南
- [EXTENSIONS.md](EXTENSIONS.md) - 扩展功能
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构

---

## ❓ 常见问题

### Q1: 两种模式的节点数量是否相同？

**A:** 是的，节点数量（process 数量）完全相同，区别只在于边的表示方式。

### Q2: Full LCI 模式会更慢吗？

**A:** 略慢，但差异不大（通常在 10-20% 范围内），因为主要时间消耗在数据库查询上。

### Q3: 如何选择使用哪种模式？

**A:** 
- 需要快速概览 → Skeleton
- 需要完整数据 → Full LCI
- 不确定 → 使用 `--both` 生成两个版本

### Q4: 文件名中的数字是什么？

**A:** 是根节点 flow_id 的前8位，用于区分不同产品的分析结果。

---

**版本**: 1.1.0  
**更新日期**: 2025-12-16  
**作者**: Data Engineering Team

