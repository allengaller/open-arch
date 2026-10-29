---
name: cloud-frameworks
description: 上云顶层框架深度知识：AWS/阿里云 CAF 云采用框架、阿里云 Landing Zone 治理基线、Well-Architected 卓越架构评审、AI 系列架构方法论（AI CAF/AI LZ/AI Lens）、安全合规体系（等保/密评/数据安全），含跨云与专有云映射，用于上云咨询、顶层设计与治理方案
---

# 云上顶层框架（CAF / Landing Zone / Well-Architected）

客户从"要不要上云"到"每个架构对不对"，三个框架分别回答三层的：

    CAF（为什么 & 怎么组织） → Landing Zone（平台怎么建） → WAF（架构怎么评）

按客户所处阶段选择知识文档：

| 客户阶段 / 诉求 | 用哪份 |
|---|---|
| 上云战略、业务案例、组织与流程准备度评估 | `content/aws-caf.md`（AWS 视角）+ `content/aliyun-caf.md`（阿里云官方四阶段、6 迁移策略与迁移工具生态） |
| 多账号体系、治理基线、网络/权限/合规顶层设计 | `content/aliyun-landing-zone.md` |
| 架构方案评审、Workload 体检、整改计划 | `content/well-architected.md` |
| 客户有多云诉求、问"这和 AWS/控制塔怎么对应"、或涉及专有云（飞天企业版）形态 | `content/cross-cloud-mapping.md` |
| AI 上云、智能体/RAG 架构设计、AI 治理与 AI Landing Zone 方案 | `content/aliyun-ai-arch.md`（AI Lens 逐支柱 BP、决策框架、AI CAF/AI LZ） |
| 金融/政企客户问等保、密评、数据安全、合规资质怎么落 | `content/aliyun-compliance.md`（责任共担、等保分工、合规包全列、云安全中心版本矩阵） |
| 查官方产品事实：LZ 版本（咨询五版本/AI 云治理中心）、蓝图、检测项、白皮书、2024-2026 动态 | `content/aliyun-landing-zone-official.md` |
| 查官方框架事实：五支柱现行命名与设计原则原文、AI 卓越架构（AI Lens）、评估工具、白皮书族谱 | `content/aliyun-waf-official.md` |

工作方式：

1. **上云咨询/顶层设计**：先用 CAF 的四阶段定位客户在哪一步，产出准备度评估与转型路线图；六个维度的差距要落到"谁负责、什么时间、验收标准"。
2. **Landing Zone 方案**：按"账号体系 → 身份权限 → 网络 → 合规安全 → 财务 → 自动化"六要素出设计，必须有账号规划表和网段规划表两张表；交付前用本包 `checklist.yaml`（六要素基线）逐项自查，risk/fail 项写入方案的"关键风险与对策"。
3. **架构评审**：用本包 `content/well-architected.md` 讲方法论；逐项打分评审工具用 `aliyun-waf` 技能的 checklist.yaml，两包配套使用。
4. 所有产出物（评估报告、LZ 设计、评审报告）统一用 `export_deliverable` 打包交付。

深度知识正文见 `content/`，回答客户问题或写方案时直接引用其中的表格与框架，不要凭记忆复述。
