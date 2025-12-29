# UPR 主链路 (Main Chain)

**生成时间**: 2025-12-25 10:21:17

**版本**: 1.4.0

**根节点**:
- Flow ID: `02eef75e-bb2f-4283-95b4-249521aa2c12`
- Process ID: `251da196-55f8-4c57-a783-9888cf33c626`

**规则**: 每个层级选择 exchange value 最大的边作为主要来源

---

## 根节点 (Level 0) 详细信息

**Process**: 线材,不锈钢, 转炉钢

### 输入 (Inputs) - 共 11 项

| Flow Name | Flow ID | Provider ID | Value |
|-----------|---------|-------------|-------|
| 钢坯, 不锈钢 | `debd442b...` | `1324fcd4...` | 1.015269 |
| 电力，中压 | `3fca3a42...` | `9cdeaade...` | 0.420159 |
| 中水 | `7eb14ae3...` | `e35a53cb...` | 0.068001 |
| 除盐水 | `d39a8c04...` | `6904a792...` | 0.032215 |
| hard coal | `0d3eda5a...` | `37a65d8c...` | 0.027391 |
| 压缩空气 | `2a4bb4b8...` | `e3bcd57a...` | 0.022580 |
| hard coal | `0d3eda5a...` | `37a65d8c...` | 0.021074 |
| 蒸汽 | `eda295c6...` | `fa72a322...` | 0.011329 |
| 氮气，钢厂 | `5ff3189c...` | `7e018b31...` | 0.003473 |
| Water, unspecified natural origin | `831f249e...` | `N/A...` | 0.000137 |
| 氧气，钢厂 | `da03f6e9...` | `482d26ed...` | 0.000028 |

### 输出 (Outputs) - 共 11 项

| Flow Name | Flow ID | Value |
|-----------|---------|-------|
| 线材, 不锈钢 | `02eef75e...` | 1.000000 |
| Carbon dioxide, fossil | `349b29d1...` | 0.151112 |
| Carbon dioxide, fossil | `349b29d1...` | 0.137596 |
| Nitrogen oxides | `c1b91234...` | 0.000036 |
| Sulfur oxides | `ba5fc0b6...` | 0.000010 |
| Particulate Matter, > 2.5 um and < 10um | `b967e1bf...` | 0.000003 |
| 生活污水，平均 | `fc2bb0dc...` | -0.000003 |
| waste mineral oil | `1b30b018...` | -0.000004 |
| inert waste, for final disposal | `240c1a3c...` | -0.000652 |
| iron scrap, unsorted | `d7432632...` | -0.017617 |
| 废钢，未分拣 | `9c471daa...` | -0.019412 |

---

## 主链路路径

**Level 0**: Process
- **ID**: `251da196-55f8-4c57-a783-9888cf33c626`
- **Name**: 线材,不锈钢, 转炉钢
- **Via Flow**: 线材, 不锈钢
- **Flow ID**: `02eef75e-bb2f-4283-95b4-249521aa2c12`
- **Value**: 0.000000

↓

  **Level 1**: Process
  - **ID**: `1324fcd4-719b-431f-a336-e7f9523f3f89`
  - **Name**: 钢坯,转炉,不锈钢
  - **Via Flow**: 钢坯, 不锈钢
  - **Flow ID**: `debd442b-9a58-3002-a734-6efa8780b95e`
  - **Value**: 1.015269

  ↓

    **Level 2**: Process
    - **ID**: `09f480b3-0d5d-4005-9b55-d727f3fce2a4`
    - **Name**: 循环水,钢厂
    - **Via Flow**: 循环水，钢厂
    - **Flow ID**: `2b6741aa-60f5-34b6-8611-92a8dacde283`
    - **Value**: 45.752535

    ↓

      **Level 3**: Process
      - **ID**: `9cdeaade-e4eb-406c-b64a-5d38fb34854f`
      - **Name**: 电力,中压
      - **Via Flow**: 电力，中压
      - **Flow ID**: `3fca3a42-df18-4d82-bd05-4ef9a2563fb3`
      - **Value**: 0.001029

      ↓

        **Level 4**: Process
        - **ID**: `0e06d234-3565-4711-b048-41808564abc8`
        - **Name**: 电力,中压
        - **Via Flow**: 电力，中压
        - **Flow ID**: `3fca3a42-df18-4d82-bd05-4ef9a2563fb3`
        - **Value**: 0.911801

        ↓

          **Level 5**: Process
          - **ID**: `b5621276-ef0a-45e4-9c69-71c5e681b734`
          - **Name**: 电力,中压
          - **Via Flow**: 电力，中压
          - **Flow ID**: `3fca3a42-df18-4d82-bd05-4ef9a2563fb3`
          - **Value**: 1.292056

          ↓

            **Level 6**: Process
            - **ID**: `544cd38c-d1ee-4837-9f1b-96b09ee9bc1b`
            - **Name**: 电力,35 kV
            - **Via Flow**: 电力，35 kV
            - **Flow ID**: `a9e39537-9b60-48de-a1e3-71af56075572`
            - **Value**: 2.652318

            ↓

              **Level 7**: Process
              - **ID**: `9c64dfdc-d98a-4462-be34-407719cfaa1d`
              - **Name**: 电力,可供混合,35 kV
              - **Via Flow**: 电力，35 kV
              - **Flow ID**: `a9e39537-9b60-48de-a1e3-71af56075572`
              - **Value**: 3.600000

              ↓

                **Level 8**: Process
                - **ID**: `78b1bb39-b04e-42b6-a6ff-ec5ce48f3610`
                - **Name**: 电力,110 kV
                - **Via Flow**: 电力，110 kV
                - **Flow ID**: `671532b2-7cf5-4432-9287-16890e7c0f63`
                - **Value**: 3.536108

                ↓

                  **Level 9**: Process
                  - **ID**: `3aea5133-bca0-4192-a5d3-1b2f6f89f31f`
                  - **Name**: 电力,可供混合,110 kV
                  - **Via Flow**: 电力，110 kV
                  - **Flow ID**: `671532b2-7cf5-4432-9287-16890e7c0f63`
                  - **Value**: 3.600000

                  ↓

                    **Level 10**: Process
                    - **ID**: `c68a6bf9-e239-4418-af19-7df02c4d6026`
                    - **Name**: 电力,≥220 kV
                    - **Via Flow**: 电力，≥220 kV
                    - **Flow ID**: `33a486bf-f129-47a9-8958-4f635372a051`
                    - **Value**: 3.323046

                    ↓

                      **Level 11**: Process
                      - **ID**: `2952b2c9-9bfa-4e6c-9edf-da6bd01c50ac`
                      - **Name**: 电力,可供混合,≥220 kV
                      - **Via Flow**: 电力，≥220 kV
                      - **Flow ID**: `33a486bf-f129-47a9-8958-4f635372a051`
                      - **Value**: 3.600000

                      ↓

                        **Level 12**: Process
                        - **ID**: `265fe465-4296-4320-bd00-719a5aba7b51`
                        - **Name**: 电力,自产混合,中高压
                        - **Via Flow**: 电力，中高压
                        - **Flow ID**: `848df11e-a17e-4c09-ad2d-ffce9dd12b8b`
                        - **Value**: 2.622856

                        ↓

                          **Level 13**: Process
                          - **ID**: `17f170cd-f8f1-4f27-af8c-eb3dca8c433a`
                          - **Name**: 电力,燃煤发电
                          - **Via Flow**: 电力，中高压
                          - **Flow ID**: `848df11e-a17e-4c09-ad2d-ffce9dd12b8b`
                          - **Value**: 2.401751

                          ↓

                            **Level 14**: Process
                            - **ID**: `01065eec-78f7-3d4b-a663-c271c7aaf5e1`
                            - **Name**: market for water, completely softened [v3.10.0]
                            - **Via Flow**: water, completely softened
                            - **Flow ID**: `cfc90fee-20f0-451a-8e50-a5bd859d3feb`
                            - **Value**: 1.232212

---

## 统计信息

- **链路长度**: 15 个节点
- **最大深度**: 14 层
