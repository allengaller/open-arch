---
name: cloud-frameworks
description: 上云顶层框架深度知识：AWS CAF 云采用框架、阿里云 Landing Zone 治理基线、Well-Architected 卓越架构评审，含跨云映射，用于上云咨询、顶层设计与治理方案
---

# 云上顶层框架（CAF / Landing Zone / Well-Architected）

客户从"要不要上云"到"每个架构对不对"，三个框架分别回答三层的：

    CAF（为什么 & 怎么组织） → Landing Zone（平台怎么建） → WAF（架构怎么评）

按客户所处阶段选择知识文档：

| 客户阶段 / 诉求 | 用哪份 |
|---|---|
| 上云战略、业务案例、组织与流程准备度评估 | `content/aws-caf.md`（CAF 方法论对阿里云同样适用，产品名替换即可） |
| 多账号体系、治理基线、网络/权限/合规顶层设计 | `content/aliyun-landing-zone.md` |
| 架构方案评审、Workload 体检、整改计划 | `content/well-architected.md` |
| 客户有多云诉求或问"这和 AWS/控制塔怎么对应" | `content/cross-cloud-mapping.md` |

工作方式：

1. **上云咨询/顶层设计**：先用 CAF 的四阶段定位客户在哪一步，产出准备度评估与转型路线图；六个维度的差距要落到"谁负责、什么时间、验收标准"。
2. **Landing Zone 方案**：按"账号体系 → 身份权限 → 网络 → 合规安全 → 财务 → 自动化"六要素出设计，必须有账号规划表和网段规划表两张表；交付前用本包 `checklist.yaml`（六要素基线）逐项自查，risk/fail 项写入方案的"关键风险与对策"。
3. **架构评审**：用本包 `well-architected.md` 讲方法论；逐项打分评审工具用 `aliyun-waf` 技能的 checklist.yaml，两包配套使用。
4. 所有产出物（评估报告、LZ 设计、评审报告）统一用 `export_deliverable` 打包交付。

深度知识正文见 `content/`，回答客户问题或写方案时直接引用其中的表格与框架，不要凭记忆复述。
