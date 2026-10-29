# 跨云框架映射参考（AWS ↔ 阿里云）

> 客户有多云/选型对比诉求时使用。原则：**框架方法论可平移，产品名要替换**；对齐到"能力"而不是对齐到具体产品。

## 1. 顶层框架对照

| 能力 | AWS | 阿里云 |
|---|---|---|
| 云采用战略框架 | AWS CAF（六维度 × 四阶段） | 阿里云 CAF（上云"四步走"：上云战略/上云准备/应用上云/运营治理；**无六视角结构**，见 `aliyun-caf.md`） |
| 迁移执行项目 | MAP（三阶段资助） | 云迁移中心 CMH / 上云迁移解决方案 + 伙伴服务包 |
| 迁移评估工具 | Migration Evaluator | 云迁移中心 CMH 的评估模块 / TCO 计算器 |
| 架构评审框架 | AWS WAF 六支柱 | 阿里云 Well-Architected 五支柱 |
| 框架产品化评审工具 | AWS Well-Architected Tool（控制台内置） | Well-Architected Tool（自评）+ 云治理中心成熟度检测（免费 260+ 项指标） |
| 场景扩展 | Lenses（Serverless/ML/GenAI/FSI…） | AI 卓越架构（AI Lens）、云网络卓越架构设计指南等行业/场景白皮书 |

## 2. Landing Zone 组件对照

| 治理能力 | AWS | 阿里云 |
|---|---|---|
| 多账号体系 | Organizations（OU + SCP） | 资源目录 RD（资源夹 + 管控策略，SCP 同构） |
| Landing Zone 产品化 | Control Tower（Account Factory、Guardrails） | Landing Zone on Alibaba Cloud / **AI 云治理中心**（蓝图搭建 + 账号工厂 + 防护规则/治理健康检测） |
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
| 卓越运营 | Operational Excellence | **效率**（2023 白皮书称"卓越运营"） |
| 可靠性 | Reliability | **稳定** |
| 安全性 / 成本优化 | Security / Cost Optimization | 安全 / 成本 |
| 性能效率 | Performance Efficiency | **性能**（阿里云无可持续性支柱；AI 场景走 AI 卓越架构 AI Lens） |
| 计费优化三件套 | RI / Savings Plans / Spot | 预留实例券 / 节省计划 / 抢占式实例 |
| 成本分摊 | Cost Allocation Tags / AWS Organizations 账单 | 费用标签 / 财务单元 / 分账账单 |
| 容灾等级 | Backup → Pilot Light → Warm Standby → Multi-site | 备份恢复 → 冷备 → 热备 → 双活/多活 |

## 4. 多云客户的应对话术

1. **"两家框架是不是两套东西？"** —— 能力模型同构（战略框架/治理基线/架构评审三层），差异在产品实现；学一套 CAF+WAF 方法论，多云都能用。
2. **"Landing Zone 能不能两家通用？"** —— 设计资产（账号规划表、CIDR 规划、权限矩阵、合规清单）可复用；IaC 需按 provider 分仓， Terraform 可部分模块化。
3. **"先做哪家？"** —— 回到 CAF 评估：按业务案例、合规属地、现有资产绑定度选主云，另一家做韧性备份或数据合规属地；避免"对等多云"（两套全量治理基线的运维成本通常被低估）。

## 5. GCP Landing Zone 对照（非官方对照，GCP 侧为官方口径）

GCP 官方定义："A landing zone, also called a cloud foundation, is a modular and scalable configuration that enables organizations to adopt Google Cloud."（[Landing zone design](https://docs.cloud.google.com/architecture/landing-zones)）

| GCP 概念 | 阿里云对应 | 差异提示 |
|---|---|---|
| 组织 Organization（根节点，建议单根） | 资源目录管理账号 | GCP 组织是逻辑根；阿里云管理账号是实体账号 |
| 文件夹 Folder | 资源夹（Core/Applications） | 语义基本等价；GCP 官方建议**不要**把公司组织结构映射到资源层次 |
| 项目 Project | 成员账号 | GCP 项目=资源容器+计费单元，隔离弱；阿里云账号隔离更强（独立账务/权限域） |
| Organization Policy 组织政策 | 管控策略 ControlPolicy | 逐级继承、约束语义高度相似 |
| Cloud Identity + IAM | IDaaS/云 SSO + RAM | 均支持企业 IdP（SAML/OIDC） |
| Billing Account 结算账号 | 财务托管主账号/企业账号中心 | 阿里云财务托管粒度更细（信控/发票/代付） |
| Cloud Foundation Fabric / FAST、terraform-example-foundation（0-bootstrap→1-org→2-environments） | AI 云治理中心蓝图、Landing Zone Accelerator（LZA） | 均为官方 IaC 化 LZ 交付 |
| Enterprise foundations blueprint | 《企业多账号统一架构方案》等解决方案库 | 均为官方参考架构+部署物 |

## 6. 专有云（飞天企业版 Apsara Stack）与公共云 LZ 的差异（非官方对照）

- **现名**：官网主推"**飞天企业版**"（Apsara Stack），"与阿里云公共云同根同源，采用同一套技术架构"；2021 年发布 Apsara Stack 2.0（一云多芯、一云多 Region，定位"可自主运营的云"）；2025 年面向海外推出主权云/AI 云/迁移方案（主权云一朵云跨地域管理 20+ region、纳管 20 万+ 服务器）。
- **治理结构（官方口径）**：无"资源目录+多账号"体系——用**飞天统一云管**（统一入口：云产品一体化管控、云资源精细化运营、自动化运维）+ **租户体系**（算力池化划分资源租户，组织/用户跨地域分配；中体彩案例出现"共享服务租户 vs 业务租户"二分）+ **混合云管理平台 2.0**（"一体化管控、智能化运维、精细化运营、个性化扩展"四化管云，支持跨云运营）。官方结构术语中未检索到"管理域（Domain）"。
- 对照表：

| 维度 | 公共云 LZ | 专有云飞天企业版 |
|---|---|---|
| 组织结构 | 资源目录多账号树（Core/Applications） | 资源租户 + 组织/用户，云内多租户隔离 |
| 身份权限 | RAM + 云 SSO + IdP | 云管内置统一账号/权限，对接客户 IdP |
| 策略管控 | 管控策略/配置审计/防护规则 | 云管一体化管控（配额、审批、工单），无公开等价 Control Policy |
| 交付 | 客户自助（蓝图/LZA） | 阿里云交付团队/伙伴交付，版本统一升级 |
| 治理入口 | 各产品控制台 + OpenAPI | 飞天统一云管统一入口 |

## 7. 多云纳管（IDC / 他云）官方口径

阿里云**无公共云侧账单级 CMP 产品**；"纳管"官方口径止于三个层面：
- **网络层**：SAG vCPE（镜像部署在他云 VM/x86，IPsec 隧道入阿里云 POP 点）、CEN 跨境互联；
- **容器层**：ACK One 注册集群/Fleet——"使用 ACK One Fleet 实例管理跨云平台的 Kubernetes 集群，包括公共云 Kubernetes 集群或 IDC 自建 Kubernetes 集群"；
- **数据层**：云备份/混合云容灾（IDC→阿里云），非他云纳管。

跨云 FinOps（他云账单归集）官方无公开产品口径（费用中心/云治理中心均只管阿里云账单）；客户要求账单级多云纳管时走第三方 CMP 伙伴。混合云管理平台 2.0 的"跨云运营"指**阿里系两朵云**（专有云+公共云）。
