# 紧凑格式使用指南（优化版）

## ✨ 新特性

优化后的紧凑格式现在**默认包含名称**，更易于 LLM 理解！

---

## 🚀 快速开始

### 推荐用法（包含名称）

```bash
# 生成两种模式（默认包含名称）
python export_compact.py --both
```

**输出文件：**
- `process_tree_skeleton_compact_a588dec8.txt` (2.9 MB)
- `process_tree_full_lci_compact_a588dec8.txt` (4.2 MB)

---

## 📊 格式说明

### 文件头部（包含完整说明）

```
================================================================================
UPR Process Tree - SKELETON MODE
================================================================================

## Basic Information
Root Product Flow: a588dec8-0e04-3502-95e8-3492dc4f2263
  Name: 乙烯

Root Process: 6c59741f-b87e-40eb-8fa5-f04059fd9fa5
  Name: 乙烯,煤基甲醇制（CMTE）,工业级

Version: 1.4.0
Generated: 2025-12-17 14:07:59

## Format Description
Mode: SKELETON TREE (Single Edge)
  - Each upstream → downstream relationship shows ONE representative flow
  - Format: process_id | process_name << flow_id | flow_name
  - Indentation indicates hierarchy level

Notation:
  | separates ID and name
  << indicates flow connection (upstream provides this flow)
  [CYCLE] marks detected circular dependency

================================================================================
```

---

### Skeleton Tree 格式

```
process_id | process_name << flow_id | flow_name
  upstream_process_id | upstream_process_name << upstream_flow_id | upstream_flow_name
    ...
```

**示例：**
```
6c59741f-b87e-40eb-8fa5-f04059fd9fa5 | 乙烯,煤基甲醇制（CMTE）,工业级
  889505d7-4c52-47ae-88e1-05106d6c9ae0 | 运输,货运,卡车,不指定 << 0f05cd98-33f4-4cc0-94bc-4b462933216e | 运输，货运，卡车，未指定的
    540882cb-f898-474b-8874-a4ead49b2f9f | 柴油,原油精炼 << 7e47d17d-3406-3e96-9655-0449c88b1f6c | 柴油
```

---

### Full LCI Tree 格式

```
process_id | process_name
  << flow_id_1 | flow_name_1
  << flow_id_2 | flow_name_2
  upstream_process_id | upstream_process_name
    << upstream_flow_id_1 | upstream_flow_name_1
    << upstream_flow_id_2 | upstream_flow_name_2
```

**示例：**
```
6c59741f-b87e-40eb-8fa5-f04059fd9fa5 | 乙烯,煤基甲醇制（CMTE）,工业级
  889505d7-4c52-47ae-88e1-05106d6c9ae0 | 运输,货运,卡车,不指定
    << 0f05cd98-33f4-4cc0-94bc-4b462933216e | 运输，货运，卡车，未指定的
    << 78237e07-ecce-464f-9249-16f6d12d7da8 | 运输，货运，卡车，国V
    << 9a1b2c3d-4e5f-6789-0123-456789abcdef | 运输，货运，卡车，国VI
```

---

### 文件尾部（统计信息）

```
================================================================================
## Statistics
================================================================================
Total Processes: 1234
Max Depth: 15
Total Edges: 1234
Total Flows: 3456
Avg Flows per Edge: 2.80
================================================================================
```

---

## 🎯 使用场景

### 场景 1：LLM 分析（推荐）

```bash
python export_compact.py --both
```

**优点：**
- ✅ 包含完整 ID（36位 UUID）
- ✅ 包含中文名称（易于理解）
- ✅ 文件大小适中（2.9-4.2 MB）
- ✅ LLM 可以处理
- ✅ 格式清晰，有完整说明

---

### 场景 2：超紧凑模式（仅 ID）

```bash
python export_compact.py --both --id-only
```

**输出示例：**
```
6c59741f-b87e-40eb-8fa5-f04059fd9fa5
  889505d7-4c52-47ae-88e1-05106d6c9ae0 << 0f05cd98-33f4-4cc0-94bc-4b462933216e
    540882cb-f898-474b-8874-a4ead49b2f9f << 7e47d17d-3406-3e96-9655-0449c88b1f6c
```

**文件大小：** ~1-2 MB（最小）

---

### 场景 3：去除名称

```bash
python export_compact.py --both --no-names
```

**说明：** 与 `--id-only` 类似，但保留头部说明

---

## 📈 文件大小对比

| 格式 | 模式 | 文件大小 | 相对大小 | LLM 可读 | 推荐度 |
|------|------|---------|---------|---------|--------|
| Markdown | Skeleton | 6.0 MB | 100% | ❌ | ⭐ |
| Markdown | Full LCI | 10.0 MB | 167% | ❌ | ⭐ |
| Compact (含名称) | Skeleton | 2.9 MB | 48% | ✅ | ⭐⭐⭐⭐⭐ |
| Compact (含名称) | Full LCI | 4.2 MB | 70% | ✅ | ⭐⭐⭐⭐⭐ |
| Compact (仅ID) | Skeleton | 1.0 MB | 17% | ✅ | ⭐⭐⭐ |
| Compact (仅ID) | Full LCI | 2.0 MB | 33% | ✅ | ⭐⭐⭐ |

**推荐：** 使用包含名称的版本（默认），文件大小适中且易于理解。

---

## 🤖 LLM 使用示例

### Prompt 示例 1：结构分析

```
我有一个产品的供应链树（紧凑格式），请帮我分析：

文件格式说明：
- process_id | process_name << flow_id | flow_name
- 缩进表示层级关系
- << 表示通过该 flow 连接

请分析：
1. 总共有多少个节点？
2. 最深的层级是多少？
3. 哪些节点的子节点最多（扇出度最大）？
4. 是否存在循环依赖？

[粘贴文件内容]
```

---

### Prompt 示例 2：关键路径

```
这是一个产品的供应链树，格式为：
process_id | process_name << flow_id | flow_name

请帮我找出：
1. 从根节点到叶子节点的最长路径
2. 该路径涉及哪些关键过程和物料？
3. 路径中的关键节点是什么？

[粘贴文件内容]
```

---

### Prompt 示例 3：物料流分析（Full LCI）

```
这是一个 Full LCI 树，每个 process 下列出了所有 flow：

格式：
process_id | process_name
  << flow_id_1 | flow_name_1
  << flow_id_2 | flow_name_2

请分析：
1. 哪些 process 的输入 flow 最多？
2. 哪些 flow 被多个 process 使用？
3. 能源流和物料流的比例？

[粘贴文件内容]
```

---

## 🔧 命令行选项

```bash
# 默认：包含名称（推荐）
python export_compact.py --both

# 仅 ID（超紧凑）
python export_compact.py --both --id-only

# 去除名称（保留说明）
python export_compact.py --both --no-names

# 只生成 Skeleton
python export_compact.py

# 只生成 Full LCI
python export_compact.py --full-lci  # (需要手动修改代码支持)
```

---

## 💡 符号说明

| 符号 | 含义 | 示例 |
|------|------|------|
| `\|` | 分隔 ID 和名称 | `process_id \| process_name` |
| `<<` | Flow 连接 | `<< flow_id \| flow_name` |
| 缩进 | 层级关系 | `  ` = level 1, `    ` = level 2 |
| `[CYCLE]` | 循环依赖标记 | （未来功能） |

---

## 📊 与 Markdown 格式对比

### Markdown 格式（原始）

```markdown
└─ **[6c59741f...]** 乙烯,煤基甲醇制（CMTE）,工业级
    ├─ **[889505d7...]** 运输,货运,卡车,不指定 ← via `0f05cd98...` (运输，货运，卡车，未指定的)
    └─ **[540882cb...]** 柴油,原油精炼 ← via `7e47d17d...` (柴油)
```

**问题：**
- ❌ ID 截断（只有8位）
- ❌ 大量格式符号
- ❌ 文件太大（6-10 MB）

---

### 紧凑格式（优化版）

```
6c59741f-b87e-40eb-8fa5-f04059fd9fa5 | 乙烯,煤基甲醇制（CMTE）,工业级
  889505d7-4c52-47ae-88e1-05106d6c9ae0 | 运输,货运,卡车,不指定 << 0f05cd98-33f4-4cc0-94bc-4b462933216e | 运输，货运，卡车，未指定的
  540882cb-f898-474b-8874-a4ead49b2f9f | 柴油,原油精炼 << 7e47d17d-3406-3e96-9655-0449c88b1f6c | 柴油
```

**优点：**
- ✅ 完整 ID（36位）
- ✅ 包含名称
- ✅ 最小格式
- ✅ 文件适中（2.9-4.2 MB）
- ✅ LLM 可处理

---

## 🎓 最佳实践

### 1. 日常使用

```bash
# 推荐：默认模式（包含名称）
python export_compact.py --both
```

**原因：**
- 文件大小适中
- 易于理解
- LLM 可处理

---

### 2. 空间受限

```bash
# 使用仅 ID 模式
python export_compact.py --both --id-only
```

**原因：**
- 文件最小
- 仍包含完整信息

---

### 3. 程序解析

```bash
# 使用仅 ID 模式
python export_compact.py --both --id-only
```

**原因：**
- 格式简单
- 易于解析
- 不需要处理中文

---

## 📝 解析示例

### Python 解析

```python
def parse_compact_tree(filename):
    """解析紧凑格式（包含名称）"""
    tree = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # 跳过注释和空行
            if line.startswith('#') or line.startswith('=') or not line.strip():
                continue
            
            # 计算层级
            level = (len(line) - len(line.lstrip())) // 2
            content = line.strip()
            
            # 解析内容
            if ' << ' in content:
                # 有 flow 连接
                parts = content.split(' << ')
                process_part = parts[0]
                flow_part = parts[1]
                
                # 分离 ID 和名称
                if ' | ' in process_part:
                    process_id, process_name = process_part.split(' | ', 1)
                else:
                    process_id = process_part
                    process_name = ""
                
                if ' | ' in flow_part:
                    flow_id, flow_name = flow_part.split(' | ', 1)
                else:
                    flow_id = flow_part
                    flow_name = ""
                
                node = {
                    'level': level,
                    'process_id': process_id,
                    'process_name': process_name,
                    'flow_id': flow_id,
                    'flow_name': flow_name
                }
            else:
                # 无 flow 连接（根节点或 Full LCI 模式的 process）
                if ' | ' in content:
                    process_id, process_name = content.split(' | ', 1)
                else:
                    process_id = content
                    process_name = ""
                
                node = {
                    'level': level,
                    'process_id': process_id,
                    'process_name': process_name
                }
            
            tree.append(node)
    
    return tree

# 使用
tree = parse_compact_tree('process_tree_skeleton_compact_a588dec8.txt')
print(f"总节点数: {len(tree)}")
print(f"根节点: {tree[0]['process_name']}")
```

---

## ❓ 常见问题

### Q1: 为什么默认包含名称？

**A:** 包含名称后，LLM 更容易理解内容，文件大小仍在可接受范围内（2.9-4.2 MB）。

---

### Q2: 如何选择模式？

**A:**
- **默认模式**（包含名称）→ 推荐，适合大多数场景
- **仅 ID 模式** → 空间受限或程序解析

---

### Q3: LLM 能处理多大的文件？

**A:**
- GPT-4: ~4-5 MB ✅
- Claude: ~5-8 MB ✅
- 紧凑格式（含名称）: 2.9-4.2 MB ✅ 完全可以

---

### Q4: 文件头部的说明会影响 LLM 吗？

**A:** 不会，反而有帮助！头部说明帮助 LLM 理解格式，提高分析准确性。

---

## 🎯 总结

优化后的紧凑格式：

✅ **完整 ID**：36位 UUID  
✅ **包含名称**：默认包含（推荐）  
✅ **详细说明**：文件头部有完整格式说明  
✅ **文件适中**：2.9-4.2 MB（LLM 可处理）  
✅ **易于理解**：清晰的符号和结构  
✅ **统计信息**：文件尾部有完整统计  

---

**版本**: 2.0.0（优化版）  
**更新日期**: 2025-12-17  
**推荐用法**: `python export_compact.py --both`

