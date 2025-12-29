# 快速参考卡片 - 双模式生成

## 🚀 快速开始

```bash
# 默认模式：只生成 Skeleton Tree
python build_process_tree.py

# 双模式：同时生成 Skeleton 和 Full LCI
python build_process_tree.py --both
```

---

## 📊 两种模式对比

| 特性 | Skeleton Tree | Full LCI Tree |
|------|---------------|---------------|
| **边的数量** | 单条（代表性） | 多条（完整） |
| **文件大小** | 小 (~6 MB) | 大 (~15 MB) |
| **生成速度** | 快 (~45秒) | 稍慢 (~52秒) |
| **数据完整性** | 部分 | 完整 |
| **适用场景** | 快速概览 | 详细分析 |

---

## 📁 输出文件

### 默认模式
```
process_tree.md
```

### 双模式
```
process_tree_skeleton_a588dec8.md  ← Skeleton Tree
process_tree_full_lci_a588dec8.md  ← Full LCI Tree
```

---

## 🎯 使用场景

### 使用 Skeleton Tree
- ✅ 快速了解供应链结构
- ✅ 教学演示
- ✅ 初步评估
- ✅ 供应链可视化

### 使用 Full LCI Tree
- ✅ LCA 研究
- ✅ 环境影响评估
- ✅ 合规审计
- ✅ 学术研究

---

## 💡 输出格式示例

### Skeleton Tree
```markdown
└─ **[process_id]** process_name ← via `flow_id` (flow_name)
    └─ **[upstream]** upstream_name ← via `flow` (flow_name)
```

### Full LCI Tree
```markdown
└─ **[process_id]** process_name
    └─ **[upstream]** upstream_name
          → via `flow_1` (flow_name_1)
          → via `flow_2` (flow_name_2)
          → via `flow_3` (flow_name_3)
```

---

## 🔧 配置

编辑 `config.py`:

```python
ROOT_FLOW_ID = "a588dec8-0e04-3502-95e8-3492dc4f2263"
ROOT_PROCESS_ID = "6c59741f-b87e-40eb-8fa5-f04059fd9fa5"
VERSION = "1.4.0"
```

---

## 📚 完整文档

- [DUAL_MODE_GUIDE.md](DUAL_MODE_GUIDE.md) - 详细指南
- [COMPARISON_EXAMPLE.md](COMPARISON_EXAMPLE.md) - 对比示例
- [CHANGELOG_DUAL_MODE.md](CHANGELOG_DUAL_MODE.md) - 更新日志

---

## ⚡ 性能提示

- Skeleton Tree: 更快，推荐日常使用
- Full LCI Tree: 稍慢，用于详细分析
- 使用 `--both` 会运行两次构建

---

## 🎓 最佳实践

1. **首次分析**: 先用 Skeleton 快速了解
2. **详细研究**: 再用 Full LCI 深入分析
3. **定期报告**: 使用 Skeleton 生成概览
4. **学术研究**: 使用 Full LCI 确保完整性

---

**版本**: 1.1.0  
**更新**: 2025-12-16

