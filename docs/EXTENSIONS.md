# 扩展功能说明

本文档介绍 HIQ UPR Process Tree Builder 的扩展功能。

## 功能列表

| 功能 | 脚本 | 说明 |
|------|------|------|
| 📊 统计分析 | `analyze_statistics.py` | 深度统计分析 |
| 🎨 可视化 | `visualize_tree.py` | 生成图形 |
| 📦 批量分析 | `batch_analysis.py` | 批量处理 |
| 🎯 交互菜单 | `menu.py` | 友好的菜单界面 |

---

## 1. 统计分析 (`analyze_statistics.py`)

### 功能

对过程树进行深度统计分析，包括：
- 节点分布
- 层级分布
- 扇出度（fan-out）统计
- 关键路径分析
- 叶子节点列表

### 使用方法

```bash
python analyze_statistics.py
```

### 输出

生成 `statistics_report.md`，包含：

#### 基本统计
- 总节点数
- 叶子节点数
- 非叶子节点数
- 最大深度
- 平均扇出度

#### 层级分布
每个层级的节点数量和百分比

#### 扇出度分布
不同扇出度的节点数量统计

#### 关键路径
从根节点到叶子节点的最长路径

#### 叶子节点列表
所有叶子节点的详细信息

### 示例输出

```markdown
# 过程树统计分析报告

## 基本统计

- **总节点数:** 156
- **叶子节点数:** 89
- **非叶子节点数:** 67
- **最大深度:** 8
- **平均扇出度:** 2.33

## 层级分布

| 层级 | 节点数 | 百分比 |
|------|--------|--------|
| 0 | 1 | 0.6% |
| 1 | 4 | 2.6% |
| 2 | 15 | 9.6% |
| 3 | 32 | 20.5% |
...
```

---

## 2. 可视化 (`visualize_tree.py`)

### 功能

使用 Graphviz 将过程树渲染为图形文件。

### 前置要求

1. **安装 Python 包**
```bash
pip install graphviz
```

2. **安装 Graphviz 系统工具**

- **macOS**:
  ```bash
  brew install graphviz
  ```

- **Ubuntu/Debian**:
  ```bash
  sudo apt-get install graphviz
  ```

- **Windows**:
  下载安装包：https://graphviz.org/download/

### 使用方法

```bash
python visualize_tree.py
```

### 输出格式

自动生成多种格式：
- `process_tree_graph.png` - PNG 图片
- `process_tree_graph.svg` - SVG 矢量图
- `process_tree_graph.pdf` - PDF 文档

### 特点

- **方向**: 从下到上（Bottom to Top）
- **根节点**: 使用红色高亮
- **普通节点**: 蓝色圆角矩形
- **边标签**: 显示 flow ID 和名称

### 示例

```
[Upstream Process 1]
        ↓ (via flow_id_1)
[Upstream Process 2]
        ↓ (via flow_id_2)
    [Root Process] (红色)
```

---

## 3. 批量分析 (`batch_analysis.py`)

### 功能

批量处理多个产品/过程的过程树构建。

### 使用方法

1. **编辑脚本**，添加要分析的根节点：

```python
roots = [
    (flow_id_1, process_id_1, "产品A"),
    (flow_id_2, process_id_2, "产品B"),
    (flow_id_3, process_id_3, "产品C"),
]
```

2. **运行脚本**：

```bash
python batch_analysis.py
```

### 输出

生成 `batch_output/` 目录，包含：

- `产品A_tree.md` - 产品A的过程树
- `产品B_tree.md` - 产品B的过程树
- `产品C_tree.md` - 产品C的过程树
- `batch_summary.md` - 汇总报告

### 汇总报告内容

```markdown
# 批量分析汇总报告

## 执行统计

- ✓ 成功: 3
- ✗ 失败: 0
- 成功率: 100.0%

## 详细结果

| 序号 | 名称 | 节点数 | 深度 | 耗时(秒) | 状态 |
|------|------|--------|------|----------|------|
| 1 | 产品A | 156 | 8 | 2.34 | ✓ |
| 2 | 产品B | 203 | 10 | 3.12 | ✓ |
| 3 | 产品C | 89 | 6 | 1.56 | ✓ |
```

### 应用场景

- 对比不同产品的供应链复杂度
- 批量生成报告
- 定期更新分析
- 版本对比

---

## 4. 交互菜单 (`menu.py`)

### 功能

提供友好的交互式菜单界面，方便选择不同功能。

### 使用方法

```bash
python menu.py
```

### 菜单选项

```
  [1] 🔍 测试数据库连接
  [2] 🌲 构建过程树（生成 Markdown）
  [3] 📊 导出 JSON 格式
  [4] 📈 统计分析
  [5] 🎨 可视化（生成图形）
  [6] 📦 批量分析
  [7] 🚀 快速开始（测试 + 构建）
  [8] 📚 查看文档
  [9] ℹ️  关于
  [0] 🚪 退出
```

### 特点

- 清晰的界面
- 自动清屏
- 错误处理
- 支持 Ctrl+C 中断

---

## 扩展开发指南

### 添加新的导出格式

创建新的导出器类：

```python
class CSVExporter:
    """CSV 导出器"""
    
    def __init__(self, builder: ProcessTreeBuilder):
        self.builder = builder
    
    def export(self, root: ProcessTreeNode, output_file: str):
        """导出为 CSV 格式"""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Process ID', 'Level', 'Children Count'])
            
            def write_node(node):
                writer.writerow([
                    node.process_id,
                    node.level,
                    len(node.children)
                ])
                for child in node.children:
                    write_node(child)
            
            write_node(root)
```

### 添加新的分析功能

继承 `TreeStatistics` 类：

```python
class AdvancedStatistics(TreeStatistics):
    """高级统计分析"""
    
    def calculate_complexity(self) -> float:
        """计算复杂度指标"""
        # 自定义计算逻辑
        return complexity_score
```

### 添加过滤条件

修改查询逻辑：

```python
def get_upstream_exchanges(self, process_id: str, 
                          location: str = None,
                          category: str = None) -> List[Dict]:
    """获取上游 exchanges（带过滤）"""
    
    query = f"""
        SELECT * FROM {config.PG_SCHEMA}.{config.PG_TABLE}
        WHERE process_id = %s
          AND is_input = true
          AND provider_id IS NOT NULL
          AND is_deleted = false
          AND version = %s
    """
    
    params = [process_id, config.VERSION]
    
    if location:
        query += " AND location = %s"
        params.append(location)
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    self.cursor.execute(query, params)
    return self.cursor.fetchall()
```

---

## 性能优化

### 1. 缓存查询结果

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_process_name_cached(self, process_id: str) -> str:
    """缓存版本的 get_process_name"""
    return self.get_process_name(process_id)
```

### 2. 批量查询

```python
def get_all_upstream_batch(self, process_ids: List[str]) -> Dict:
    """批量获取上游 exchanges"""
    query = f"""
        SELECT * FROM {config.PG_SCHEMA}.{config.PG_TABLE}
        WHERE process_id = ANY(%s)
          AND is_input = true
          AND provider_id IS NOT NULL
          AND is_deleted = false
          AND version = %s
    """
    
    self.cursor.execute(query, (list(process_ids), config.VERSION))
    results = self.cursor.fetchall()
    
    # 按 process_id 分组
    grouped = defaultdict(list)
    for row in results:
        grouped[row['process_id']].append(row)
    
    return grouped
```

### 3. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_batch_parallel(self, roots: List[Tuple], max_workers: int = 4):
    """并行批量分析"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(self.analyze_single, flow_id, process_id, name)
            for flow_id, process_id, name in roots
        ]
        
        results = [future.result() for future in futures]
    
    return results
```

---

## 常见问题

### Q1: Graphviz 安装失败

**错误信息**: `ExecutableNotFound: failed to execute ['dot', '-Tpng', ...]`

**解决方法**:
1. 确保安装了 Graphviz 系统工具（不只是 Python 包）
2. 检查 `dot` 命令是否在 PATH 中：
   ```bash
   which dot  # macOS/Linux
   where dot  # Windows
   ```

### Q2: 批量分析内存不足

**解决方法**:
1. 减少并行数量
2. 逐个处理而非批量
3. 限制递归深度

### Q3: 统计分析很慢

**解决方法**:
1. 使用缓存
2. 预加载所有 process/flow 名称
3. 使用索引优化数据库查询

---

## 最佳实践

### 1. 首次使用扩展功能

```bash
# 1. 先测试基本功能
python quick_start.py

# 2. 运行统计分析
python analyze_statistics.py

# 3. 尝试可视化（需要安装 Graphviz）
python visualize_tree.py
```

### 2. 日常使用

```bash
# 使用交互菜单
python menu.py
```

### 3. 生产环境

```bash
# 使用批量分析
python batch_analysis.py

# 定期生成报告
crontab -e
# 添加: 0 2 * * * cd /path/to/hiq_upr && python batch_analysis.py
```

---

## 未来扩展

可以考虑添加的功能：

1. **Web 界面**
   - Flask/Django Web 应用
   - 在线查看过程树
   - 交互式探索

2. **API 服务**
   - RESTful API
   - 支持远程调用
   - 与其他系统集成

3. **实时监控**
   - 监控数据变化
   - 自动触发分析
   - 告警通知

4. **机器学习**
   - 异常检测
   - 模式识别
   - 预测分析

5. **导出更多格式**
   - Excel（带样式）
   - PowerPoint
   - HTML 交互式报告
   - Neo4j 图数据库

---

## 贡献

欢迎提交新的扩展功能！

提交前请确保：
1. 代码符合 PEP 8
2. 添加完整注释
3. 更新相关文档
4. 提供使用示例

---

**版本**: 1.0.0  
**更新日期**: 2025-12-16

