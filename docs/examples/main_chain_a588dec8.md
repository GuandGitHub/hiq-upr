# UPR 主链路 (Main Chain)

**生成时间**: 2025-12-24 14:21:30

**版本**: 1.4.0

**根节点**:
- Flow ID: `a588dec8-0e04-3502-95e8-3492dc4f2263`
- Process ID: `6c59741f-b87e-40eb-8fa5-f04059fd9fa5`

**规则**: 每个层级选择 exchange value 最大的边作为主要来源

---

## 根节点 (Level 0) 详细信息

**Process**: 乙烯,煤基甲醇制（CMTE）,工业级

### 输入 (Inputs) - 共 4 项

| Flow Name | Flow ID | Provider ID | Value |
|-----------|---------|-------------|-------|
| 乙烯 | `a588dec8...` | `8fdb4514...` | 1.000000 |
| 运输，货运，火车，未指定的 | `aa50073b...` | `46044604...` | 0.156400 |
| 运输，货运，卡车，未指定的 | `0f05cd98...` | `889505d7...` | 0.149600 |
| 运输，货运，内河，干散货船，未指定的 | `fa34fb13...` | `4bea1726...` | 0.000000 |

### 输出 (Outputs) - 共 1 项

| Flow Name | Flow ID | Value |
|-----------|---------|-------|
| 乙烯 | `a588dec8...` | 1.000000 |

---

## 主链路路径

**Level 0**: Process
- **ID**: `6c59741f-b87e-40eb-8fa5-f04059fd9fa5`
- **Name**: 乙烯,煤基甲醇制（CMTE）,工业级
- **Via Flow**: 乙烯
- **Flow ID**: `a588dec8-0e04-3502-95e8-3492dc4f2263`
- **Value**: 0.000000

↓

  **Level 1**: Process
  - **ID**: `8fdb451474cb4d57a6a0dd5764b9a914`
  - **Name**: 乙烯,煤基甲醇制（CMTE）,工业级
  - **Via Flow**: 乙烯
  - **Flow ID**: `a588dec8-0e04-3502-95e8-3492dc4f2263`
  - **Value**: 1.000000

  ↓

    **Level 2**: Process
    - **ID**: `baf69ffa-4714-3e76-8413-05a2c2d7c82d`
    - **Name**: market for methanol [v3.10.0]
    - **Via Flow**: methanol
    - **Flow ID**: `4a0b47d3-c643-4b67-841b-b5689787f7a1`
    - **Value**: 2.690000

---

## 统计信息

- **链路长度**: 3 个节点
- **最大深度**: 2 层
