# 跨云框架映射参考（AWS ↔ 阿里云）

> 客户有多云/选型对比诉求时使用。原则：**框架方法论可平移，产品名要替换**；对齐到"能力"而不是对齐到具体产品。

## 1. 顶层框架对照

| 能力 | AWS | 阿里云 |
|---|---|---|
| 云采用战略框架 | AWS CAF（六维度 × 四阶段） | 阿里云云采用框架 CAF / 企业上云方法论（结构同源：组织、治理、平台、安全、运营 + 业务） |
| 迁移执行项目 | MAP（三阶段资助） | 迁移中心 MC / 上云迁移解决方案 + 伙伴服务包 |
| 迁移评估工具 | Migration Evaluator | 迁移中心 MC 的评估模块 / TCO 计算器 |
| 架构评审框架 | AWS WAF 六支柱 | 阿里云 Well-Architected 五支柱 |
| 框架产品化评审工具 | AWS Well-Architected Tool（控制台内置） | 控制台架构评估 / 伙伴评审服务 |
| 场景扩展 | Lenses（Serverless/ML/GenAI/FSI…） | 白皮书行业与场景篇章 |

## 2. Landing Zone 组件对照

| 治理能力 | AWS | 阿里云 |
|---|---|---|
| 多账号体系 | Organizations（OU + SCP） | 资源目录 RD（资源夹 + 管控策略，SCP 同构） |
| Landing Zone 产品化 | Control Tower（Account Factory、Guardrails） | Landing Zone on Alibaba Cloud / 云治理中心 GCC（基线检查 + 自动化搭建） |
| 集中身份 | IAM Identity Center（SSO） | RAM / IMS 统一身份 + SSO 对接企业 IDP |
| 配置合规 | Config + Config Rules | 配置审计（合规包：等保 2.0、CIS） |
| 操作审计 | CloudTrail | 操作审计 ActionTrail |
| 骨干网络 | Transit Gateway | 云企业网 CEN（转发路由器 TR） |
| 集中日志 | CloudWatch Logs / S3 汇聚账号 | 日志服务 SLS（Log 账号集中投递） |
| 运维编排 | Systems Manager / Step Functions | OOS 运维编排 / 云助手 |
| IaC | CloudFormation / CDK / Terraform | ROS 资源编排 / Terraform（alicloud provider）/ CDK |
| 堡垒与主机安全 | Amazon Systems Manager Session Manager / GuardDuty | 堡垒机 / 云安全中心 |
| 密钥管理 | KMS | 密钥管理服务 KMS |

## 3. 支柱术语对照（写方案时用词一致）

| 概念 | AWS 叫法 | 阿里云叫法 |
|---|---|---|
| 高/中风险项 | HRI / MRI | 风险项（分级：高/中） |
| 卓越运营 | Operational Excellence | 运维 |
| 计费优化三件套 | RI / Savings Plans / Spot | 预留实例券 / 节省计划 / 抢占式实例 |
| 成本分摊 | Cost Allocation Tags / AWS Organizations 账单 | 费用标签 / 财务单元 / 分账账单 |
| 容灾等级 | Backup → Pilot Light → Warm Standby → Multi-site | 备份恢复 → 冷备 → 热备 → 双活/多活 |

## 4. 多云客户的应对话术

1. **"两家框架是不是两套东西？"** —— 能力模型同构（战略框架/治理基线/架构评审三层），差异在产品实现；学一套 CAF+WAF 方法论，多云都能用。
2. **"Landing Zone 能不能两家通用？"** —— 设计资产（账号规划表、CIDR 规划、权限矩阵、合规清单）可复用；IaC 需按 provider 分仓， Terraform 可部分模块化。
3. **"先做哪家？"** —— 回到 CAF 评估：按业务案例、合规属地、现有资产绑定度选主云，另一家做韧性备份或数据合规属地；避免"对等多云"（两套全量治理基线的运维成本通常被低估）。
