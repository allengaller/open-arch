# 阿里云 Landing Zone 官方全景参考

> 全网调研档案（采集于 2026-10-28）：以阿里云官方文档/官网为主轴的系统梳理，所有关键事实附来源链接。
> 与 `aliyun-landing-zone.md` 的分工：那份是**售前视角的顶层方法**（怎么讲、怎么交付），本篇是**官方事实底座**（产品叫什么、有哪些版本、蓝图/检测项清单、白皮书索引）——引用产品名称与官方机制时以本篇为准。

## 1. 官方定义与八大领域

- 官方定义："在上云前做好合理的规划可以避免对管理方式的反复重构，加速业务大规模上云。阿里云帮助您先从顶层规划一个完善的企业上云框架，也称为 Landing Zone。"（[Landing Zone 官网](https://www.aliyun.com/landing-zone)）
- 核心理念：**企业上云、治理先行**——上云前顶层规划，避免管理方式反复重构。（[开放平台 Landing Zone](https://open.aliyun.com/landing-zone?type=enterprise)）
- **八大领域**（官网原文，逐项核实）：①资源规划 ②财务管理 ③网络规划 ④身份权限 ⑤安全防护 ⑥运维管理 ⑦合规审计 ⑧自动化。（[官网](https://www.aliyun.com/landing-zone)）
- 官网列示的配套产品：资源管理、配置审计、访问控制 RAM、标签、费用与成本、VPC、云企业网 CEN、SLB、NAT 网关、单点登录 SSO、云防火墙、DDoS 防护、云安全中心、WAF、日志服务 SLS、云监控、ARMS、操作审计、Terraform/Jenkins/GitHub（开源）。
- 方法论三角：CAF 讲"怎么规划上云"，Landing Zone 讲"上云地基"，Well-Architected 讲"用云质量"。LZ 场景方案库现挂载于 CAF 文档域名 `help.aliyun.com/zh/caf/` 下。（[Landing Zone 场景方案](https://help.aliyun.com/knowledge_detail/300734.html)）

## 2. 产品形态全景（重点：不存在"Landing Zone 免费版/企业版"）

**结论：阿里云从未推出名为"Landing Zone 免费版/企业版"的产品。**"版本"只存在于付费咨询服务线；产品化入口一直是免费的云治理中心。

| 形态 | 性质 | 版本/命名 | 入口 |
|---|---|---|---|
| Landing Zone 本体 | 方法论框架，免费 | 无版本 | [官网](https://www.aliyun.com/landing-zone) |
| **AI 云治理中心** | SaaS 治理产品，免费开通（基础治理产品免费） | 无版本区分 | 控制台"Landing Zone 搭建"，蓝图模板；[技术解决方案页（预估 0 元）](https://www.aliyun.com/solution/tech-solution-deploy/2506085) |
| **Landing Zone 咨询服务** | 付费人工服务，按次付费 | SOW 现行 5 版本：轻量版/基础版/标准版/AI 版/实施服务 | [服务内容说明 SOW](https://help.aliyun.com/document_detail/2531626.htm) |
| 国际站服务包（较早期口径） | 付费服务 | 基础版 $70,000 / 标准版 $140,000 / 进阶版 $210,000 / 自定义 | [alibabacloud.com 服务页](https://www.alibabacloud.com/zh/services/alibaba-cloud-landing-zone) |

### 咨询服务五版本能力对照（据 SOW）

| 版本 | 范围要点 |
|---|---|
| 轻量版（约 2 周） | 标准化架构交付，仅多账号体系少量定制；不含个性化网络/安全合规/运维自动化设计 |
| 基础版 | 调研评估 + 资源管理/身份管理/网络规划/安全防护四模块设计 + 技术验证；不含合规审计、财务、运维、IaC |
| 标准版 | 基础版全部 + 合规审计（事前/事中/事后/风险监控）+ 财务管理（托管/分账/预算）+ 运维管理 + IaC 自动化（CI/CD、模板、账号工厂），共八项 |
| AI 版（2025 新增） | 标准 LZ 之上加百炼/PAI 工作空间规划、API Key 与 Agent 全链路身份、训练/推理组网、AI 分账/合规基线/AIOps 智能体设计 |
| 实施服务 | 须与咨询版配合购买，优先 IaC 实施，仅限阿里云侧配置 |

交付物：《轻量版实施手册》《基础版方案》《标准版方案》《企业 AI Landing Zone 咨询服务方案》。（[SOW](https://help.aliyun.com/document_detail/2531626.htm)）

## 3. AI 云治理中心（GCC → AI CGC）

- **已更名/升级**：产品现名 **AI 云治理中心（Agentic Cloud Governance Center）**，定位"面向 Agentic Cloud 时代的统一治理平台"，治理范围从传统云资源扩展到 AI 平台、Agent 运行时、AI 网关、AI 安全护栏。文档域名仍为 `help.aliyun.com/zh/cgc/`。（[文档首页](https://help.aliyun.com/zh/cgc/)）
- 开通地域：中国内地推荐杭州、海外推荐新加坡，开通后不可改；创建服务关联角色 `AliyunServiceRoleForGovernance`。（[技术解决方案页](https://www.aliyun.com/solution/tech-solution/ecflz/2506085)）

### 3.1 五种蓝图（已核实，2026-10）

（[Landing Zone 搭建概述](https://help.aliyun.com/zh/cgc/user-guide/build-a-landing-zone-1)）

| 蓝图 | 内容 |
|---|---|
| 标准蓝图 | 启用资源目录；创建 **Core 与 Applications 资源夹**；创建日志账号、指定财务管理账号；开通云 SSO；启用必要防护规则 |
| 标准蓝图（云企业网络） | 标准蓝图 + 基于 CEN 的 DMZ 网络隔离区，统一流量出入口管控 |
| 云原生蓝图 | 标准蓝图 + 企业级 ACK Pro 集群（负载均衡、多可用区）及管理权限 |
| 金融行业蓝图 | 标准蓝图 + CEN DMZ + 金融行业常见合规包 |
| 医疗及生物行业蓝图 | 标准蓝图 + CEN DMZ + 服务日志投递 + 基于 GxP 欧盟标准的行业合规包 |

### 3.2 搭建项清单

资源规划——创建管理账号（必选）、开通资源目录（必选）、创建资源夹（必选）、创建核心账号（必选：财务/日志/安全/共享服务等）、邀请已有账号（可选，邀请有效期 12 小时）；身份权限——设置云 SSO（推荐，预置常见访问配置）；合规审计——操作审计统一日志投递（推荐）、配置审计统一日志投递（推荐）、启用防护规则（必选）、服务日志统一投递（可选）；财务——设置财务托管关系（推荐）；网络——启用云企业网络（可选）；运维——企业级 ACK 集群（可选）。（[搭建概述](https://help.aliyun.com/zh/cgc/user-guide/build-a-landing-zone-1)、[技术解决方案页](https://www.aliyun.com/solution/tech-solution/ecflz/2506085)）

### 3.3 搭建前账号资格检查

是否已开通资源目录；管理账号下是否部署云资源（建议不部署）；RAM 用户数量（建议 <5）；是否欠费；主账号是否创建 AK（强烈建议不创建）。（[技术解决方案页](https://www.aliyun.com/solution/tech-solution/ecflz/2506085)）

### 3.4 两套检测机制（勿混淆）

1. **Landing Zone 防护规则**（搭建期强制下发，基于配置审计，[文档](https://help.aliyun.com/document_detail/321927.htm)）：
   - Core 文件夹必选——禁止删除存储审计日志的 OSS 存储空间、禁止修改其加密配置、禁止停用配置审计功能；
   - 资源目录全局推荐——云账号不存 AccessKey、所有账号开启 MFA、ECS 数据盘加密、安全组禁止 0.0.0.0/0 开风险端口（22/3389）、安全组入网设置有效、OSS 禁止公共读写、RDS 开 TDE、RDS 使用专有网络等。
2. **治理健康检测（治理成熟度检测）3.0 模型**（运行期，自动检测资源目录成员并出报告，[检测项清单](https://www.alibabacloud.com/help/zh/cgc/user-guide/supported-detections-3-0-model)）：按**安全 / 稳定 / 成本 / 效率 / 性能**五维组织——全量解析为**安全 15 类、稳定 8 类、成本 4 类 20 项、效率 3 类 26 项、性能 3 类 15 项**，页面另附"移除的检测项"附表 30 项（勿与现行项混算）。高频项举例：
   - 安全：主账号 MFA 未开启、多账号身份未用云 SSO 统一、主账号存在 AK、AK 365 天未轮转、Admin 权限身份过多、未使用访问分析器、未用管控策略做多账号边界、日志未中心化、安全组全开放、ECS 绑定公网 IP、NAT/VPC 边界防火墙未全覆盖、OSS 公共读写、RDS TDE 未开、云安全中心仅免费版；
   - 稳定：共享型/停售 ECS、单节点 MongoDB、基础系列 RDS、ACK/RDS 版本过期、产品 7 天内到期未自动续费、约 30 种产品单 AZ 风险、快照备份缺失；
   - 成本：余额预警未开启、按量付费未用节省计划/包年包月、低负载/闲置资源；
   - 效率：打标率 <75%、创建者标签未开启、账号未纳入资源目录、**未设置委派管理员**、调用已废弃 API、自动化比率 <100%；
   - 性能：性能监控、弹性资源利用、CDN/ESA 配置。

## 4. 官方账号体系（已核实：Core + Applications 两资源夹）

- **资源目录 RD**：免费的多级账号与资源关系管理服务；企业管理账号 + 成员 + 资源夹（Folder，可嵌套成树）。（[资源管理](https://intl.aliyun.com/help/zh/resource-management/)）
- **官方现行资源夹结构（全部现行文档一致）**：Root 下 **Core + Applications 两个资源夹**；Core 放管控用途的"核心账号"，Applications 放业务成员；不存在即由 AI 云治理中心自动创建。（[搭建 FAQ](https://help.aliyun.com/zh/cgc/support/faq-about-the-deployment-of-landing-zones)、[资源规划经典指导](https://help.aliyun.com/document_detail/300736.html)）
  - ⚠️ 早期社区材料流传的"Core/Security/Log/Suspended 四资源夹"与官方现行文档不符——日志/安全/财务/共享服务是以**核心账号**身份放 Core 夹，不是独立资源夹；"Suspended 资源夹"在阿里云公开文档未检索到（疑为 AWS Control Tower 旧方案结构的混淆）。
- **核心账号角色**（[企业多账号统一架构方案](https://help.aliyun.com/zh/caf/enterprise-multi-account-unified-architecture-solution)、[Light LZ](https://help.aliyun.com/zh/landing-zone/solution-148)）：管理账号（只做目录/身份/账单/审计策略管控，不部署业务资源，开 MFA）、安全账号（WAF/高防/云防火墙集中布防）、日志账号（全成员 ActionTrail/配置审计/服务日志汇聚到 SLS+OSS）、运维账号（堡垒机、监控平台、CMP/CMDB）、共享服务账号（CEN/TR、DMZ VPC、NAT、共享 VPC）、财务结算账号；业务账号按组织架构/环境放 Applications。存量账号不建议直接当管理账号，应新建空白账号后邀请纳管。
- **委派管理员与可信服务**：可信服务 = 支持与资源目录组合使用的服务；管理账号可将某成员设为该服务的委派管理员，之后在组织范围内做业务管理（云 SSO、云防火墙、云安全中心-威胁分析等）；不设置则须用管理账号操作。（[可信服务概述](https://help.aliyun.com/knowledge_detail/208133.html)、[云 SSO 委派管理员](https://help.aliyun.com/zh/cloudsso/user-guide/manage-cloud-sso-delegated-administrator-account)）

## 5. 身份权限：RAM / 云 SSO / 管控策略

- **云 SSO**：基于资源目录的多账号统一身份管理；一次性配置企业 IdP 与阿里云 SAML 单点登录、统一配置所有用户对 RD 账号的访问配置（Access Configuration）；支持 SCIM 同步 Azure AD/Okta；支持 RAM 用户同步（兜底不支持角色扮演的服务）；**每个企业管理账号仅能创建一个云 SSO 目录**。（[云 SSO 文档](https://help.aliyun.com/zh/cloudsso/)、[多账号身份权限集中管理方案](https://www.aliyun.com/solution/tech-solution/cmomaip/2506076)）
- **Light LZ 的 RAM 设计范式**（[Light LZ](https://help.aliyun.com/zh/landing-zone/solution-148)）：Administrator/Audit/Billing/SecurityAdministrator/Iam 五类角色 + 每账号自动创建 `Emergency`（应急管理员）与 `ProgrammaticUser`（自动化 AK，部署完建议删除）两个 RAM 用户。
- **管控策略 ControlPolicy**（[概述](https://help.aliyun.com/zh/resource-management/resource-directory/user-guide/control-policy-overview)）：
  - 本质：基于资源结构（资源夹/成员）的**权限边界**，只限权不授权；鉴权顺序 = 先管控策略、再账号内 RAM；沿资源目录层级向下继承；开启后默认绑定系统策略 `FullAliyunAccess`（需解绑方能限权）。
  - 限制：每节点最多绑定 10 条；单条策略文档最长 4096 字符（API 口径；方案文档口径 2048）；`EffectScope` 可选 RAM 或 All；并非全部云产品支持。
  - **官方 25 个自定义策略示例**（[示例页](https://www.alibabacloud.com/help/zh/resource-management/resource-directory/user-guide/examples-of-custom-access-control-policies)），典型：禁止购买域名；禁止访问工单系统；禁止访问特定地域 ECS；禁止在非指定 VPC 创建 ECS（`Condition.StringNotLike vpc:VPC`）；禁止创建公网出口资源（`vpc:AllocateEipAddress*`、`vpc:CreateNatGateway`）；禁止访问混合云连接服务（专线/VPN/CEN/SAG 全 Deny）；禁止关停审计（`actiontrail:UpdateTrail/DeleteTrail/StopLogging`）；保护资源目录角色；删除 ECS 必须 MFA（`acs:MFAPresent=false`）；限定资源共享目标/类型；**仅允许从 IPAM 地址池创建 VPC**（`vpc:Ipv4IpamPoolId` 条件键——网段集中治理新能力）。
  - 配套方案：[企业多账号组织全局访问边界控制](https://help.aliyun.com/zh/well-architected/solution-39)、云产品白名单管控（资源管理实践教程）。

## 6. 网络规划

- **官方网络分区模型**（[基于 CEN-TR 实现企业级云上互联](https://help.aliyun.com/zh/caf/uses-cen-instances-and-transit-routers-to-establish-enterprise-grade-network-connections)）：业务生产区、开发测试区、**互联网出口区（DMZ：EIP/NAT/SLB/云防火墙）**、东西向安全区（东西向防火墙、IDS/IPS）、内联运维区（跳板/堡垒机）、外联网区（第三方 IDC 接入）。CEN/TR 实例归属共享服务账号，业务 VPC 归业务账号，TR 跨账号加载。
- TR 同地域互通线速、全球互通时延优于公网、TR+带宽包全球组网；专线 Express Connect 接入 IDC；集团-子公司场景用"数据互通 VPC"跨账号授权再挂集团 CEN。
- **CIDR 官方方法论**（三轮已核实）：官方无统一强制网段表，但 VPC《地址规划》文档给出逐层划分示例——**10.0.0.0/8 按地域（/11）→ 业务线（/15）→ 环境（/17）**；[《跨国企业 LZ 白皮书》](https://developer.aliyun.com/ebook/7950)8.4 网络规划在开发者社区有（1）-（4）四篇连载（2023-05，正文需站内检索）。Light LZ 示例：共享服务 VPC `10.0.0.0/16`（vSwitch 按 AZ /29），生产/测试账号各 1 VPC + 8 vSwitch（双 AZ）+ Public NAT + ALB + EIP；验收含"生产与测试 VPC 互不通、运维 VPC 与业务互通"。（[Light LZ](https://help.aliyun.com/zh/landing-zone/solution-148)、[VPC 地址规划](https://help.aliyun.com/zh/vpc/address-planning)）管控策略可用 IPAM 池强制约束 VPC 网段来源。
- 共享 VPC：通过资源共享把共享服务账号的 vSwitch 共享给业务账号；管控策略可限制共享范围与资源类型。

## 7. 安全合规基线

- **合规包（配置审计）**：Light LZ 推荐启用——等保三级预检、CIS 网络安全框架检查、OSS 合规管理最佳实践、资源空闲检测、资源稳定性最佳实践；支持不合规资源自动修复。（[Light LZ](https://help.aliyun.com/zh/landing-zone/solution-148)）
- **日志留存**：操作审计多账号统一投递（管理账号一次配置全部成员生效），SLS 实时分析 + OSS 长期归档；单账号 ActionTrail 默认仅存 180 天，投递 OSS 满足等保 2.0 与《网络安全法》180 天留存；云防火墙/云安全中心日志 ≥180 天。（[多账号操作日志统一归集与审计](https://help.aliyun.com/zh/landing-zone/solution-37)）
- **安全产品布防**：安全账号集中部署 WAF/高防/云防火墙（NAT 边界 + VPC 边界 + IPS 拦截模式 + 默认拒绝）；主机侧云安全中心（免费版不满足检测要求）；堡垒机多账号统一运维（注意堡垒机 V2/V3.1 已于 2023-09 停止维护）；数据侧 KMS/TDE/脱敏（敏感数据识别用数据安全中心）。Well-Architected 基础架构安全最佳实践明确以 LZ 账号体系为第一层防线。（[最佳实践](https://help.aliyun.com/document_detail/2573784.html)）

## 8. 财务治理

- **两种多账号结算模式**（[多账号企业付款方案](https://help.aliyun.com/document_detail/2929439.html)）：
  - **财务托管**：子账号把资金/发票/账单权限交给财务主账号，统一代付、开票、结算；主账号可将 RI、SCU、节省计划**共享**给子账号抵扣（账单层面共享）；
  - **财务管理**：子账号独立结算，主账号汇总查看。
  - Light LZ 推荐企业管理账号担任财务托管主账号。
- **分账三层**：多账号（账号即分账边界）→ 财务单元（单账号内多级归集）→ 标签（费用标签启用后最多 100 个标签 KEY 可用于分账；标签键 ≤128 字符，不能以 `aliyun`/`acs:` 开头）。（[Light LZ 财务分账](https://help.aliyun.com/zh/landing-zone/solution-148)、[使用标签分账](https://help.aliyun.com/knowledge_detail/183697.html)）
- **强制打标闭环**：开启"创建者标签"自动打标 → 标签策略绑定资源夹 → 配置审计检测未打标资源并预警/自动修复。（[Light LZ](https://help.aliyun.com/zh/landing-zone/solution-148)）

## 9. 自动化与交付

- **账号工厂**：AI 云治理中心内置——配置账号基线（基线项编排组合）→ 用基线创建新账号 → 应用到已有账号/资源夹 → 基线历史。（[功能特性](https://help.aliyun.com/zh/cgc/product-overview/product-function-custom-node-governance-normal)）另有开源版：[基于 GitLab+Terraform 的账号工厂方案](https://help.aliyun.com/zh/caf/implement-an-account-factory-based-on-gitlab)、[多账号解决方案专区](https://open.aliyun.com/multi-account)（含《构建多账号云环境白皮书》）。
- **场景方案库（控制台 + Terraform 双轨）**（[总览](https://help.aliyun.com/knowledge_detail/300734.html)）：资源规划——企业多账号统一架构；财务管理——多账号企业付款；身份权限——基于云 SSO 的多账号单点登录；合规审计——多账号操作日志统一归集、多账号配置统一合规审计；网络规划——基于 CEN-TR 的企业级云上互联；自动化——GitLab 账号工厂。
- **Light LZ 一键部署**（[方案](https://help.aliyun.com/zh/landing-zone/solution-148)）：问卷调研 → 开 GCC → 控制台初始化资源结构/财务/审计投递/标签 → `settings.tfvars` 填账号 UID/资源夹 ID/VPC CIDR → Terraform 自动建账号、VPC/VSwitch/CEN、ECS+ALB、合规规则 → 四项连通性验收。目标 120 分钟级交付。`settings.tfvars` 变量四组（源码需联系阿里云工程师获取）：①账号与资源夹 ID（management/payer/log/shared_service/security_account_id、core/applications_folder_id）②新成员账号命名（ops/daily/prod 前缀+显示名）③身份与治理（cloudsso_directory_name/user、ram_user_initial_pwd、tag_policy、config_compliance_packs）④网络与计算（cen_instance_name、各账号 vpc_config 含 region/vpc_cidr/vswitch、ECS 规格/密码、ALB/监听/服务器组/安全组规则）；注意 TR 须先经 OpenAPI 手动开通，脚本不开通 TR。

## 10. 白皮书与公开材料

| 白皮书 | 时间 | 入口 |
|---|---|---|
| 《构建多账号云环境白皮书》 | 阿里云开放平台 | [open.aliyun.com/multi-account](https://open.aliyun.com/multi-account)（白皮书+视频专区） |
| 《跨国企业上云登陆区（Landing Zone）白皮书》 | 2023-04，与埃森哲联合发布（第八章含最佳实践，8.4 网络规划 4 篇连载） | [发布文](https://developer.aliyun.com/group/openapi/article) |
| 《金融企业上云登陆区（Landing Zone）白皮书》 | 2023-05 | [发布文索引](https://developer.aliyun.com/group/openapi/article) |
| 《MNC 云治理中心 Landing Zone 白皮书》《为金融机构构建安全合规的云治理中心 Landing Zone》 | 国际站可下载 | [云迁移页下载区](https://www.alibabacloud.com/solutions/cloud-migration) |
| **AI Landing Zone（AI LZ）白皮书** + AI CAF 升级 | 2025-12-16 信通院 IT 新治理领导力论坛发布 | [报道](https://www.ciotimes.com/IT/223302.html)、[中国日报](https://cnews.chinadaily.com.cn/a/202512/19/WS69451857a310942cc4997990.html) |
| 《云治理企业成熟度发展 2025 年度报告》 | 2025-12，与埃森哲联合 | [报道](https://m.pedaily.cn/99discoveries/120625) |

AI LZ 要点：AI CAF 四阶段（战略/准备/构建/运营）；"AI 准备"阶段须构建通往生产环境的"数字登陆区"AI LZ——标准化、自动化、可治理的 AI 基础设施平台 + 组织/流程/自动化治理方法；在通用 LZ 上补齐安全合规治理、AI 成本精细化管理、训练/推理可观测；案例：全球运动服饰企业（PAI+GPU+通义模型）、车企。

**客户案例**（[官网](https://www.aliyun.com/landing-zone)，已核实）：巴斯夫、中兴通讯（20+ 分散账号收敛）、小马智行、迪卡侬、中体彩、流利说；另有众安国际、vivo 等散见开放平台页。**生态伙伴**：埃森哲、德勤、凯捷、神州数码、浩鲸、安畅、驻云、青莲网络、飞络、鹿云、Bespin、东软、华讯、冠闵等。

## 11. 与 AWS Control Tower 对照

| 维度 | 阿里云 | AWS |
|---|---|---|
| 组织 | 资源目录 RD（管理账号/成员/资源夹） | Organizations（管理账户/成员账户/OU） |
| 产品化 LZ | **AI 云治理中心**（蓝图搭建+账号工厂+防护规则+健康检测），免费 | Control Tower（Landing Zone/Blueprint/Account Factory/Guardrails） |
| 预置 OU/资源夹 | **Core / Applications 两资源夹**（核心账号放 Core） | Security OU（审计+日志存档账户）、Sandbox、Production OU |
| 权限边界 | 管控策略 ControlPolicy（Deny 为主、向下继承、10 条/节点） | SCP Service Control Policy |
| 集中身份 | 云 SSO（SAML/SCIM、访问配置、RAM 用户同步） | IAM Identity Center |
| 护栏 | 配置审计防护规则 + 合规包 + 治理健康检测 3.0 | Guardrails（proactive/detective）+ Config 规则 |
| 账号工厂 | GCC 账号基线 / GitLab+Terraform 方案 | Account Factory（Service Catalog） |
| 日志归集 | 日志账号 + ActionTrail/配置审计/SLS/OSS | Log Archive Account |

Azure Landing Zone（Policy/Management Group 模型）官方对照材料未检索到，待核实。

## 12. 2024–2026 动态时间线

| 时间 | 动态 |
|---|---|
| 2023-04/05 | 《跨国企业 LZ 白皮书》《金融企业 LZ 白皮书》发布 |
| 2024 | 账号工厂、基线编排、治理成熟度检测陆续成型；检测模型升级 3.0 |
| 2025 | Light Landing Zone 方案上线（solution-148）；咨询服务 SOW 改版五版本（新增 AI 版）；管控策略新增 IPAM 池约束示例 |
| 2025-12 | 云治理中心更名 **AI 云治理中心**（Agentic Cloud Governance Center）；发布 **AI Landing Zone 白皮书**、AI CAF、《云治理企业成熟度 2025 年度报告》 |
| 2025-12（页面更新） | 治理健康检测 3.0 检测项页发布（五维数百项） |

## 13. 官方资料索引

| 标题 | URL |
|---|---|
| Landing Zone 官网（八大领域/案例/伙伴） | https://www.aliyun.com/landing-zone |
| 开放平台 Landing Zone（方案库） | https://open.aliyun.com/landing-zone?type=enterprise |
| AI 云治理中心文档 | https://help.aliyun.com/zh/cgc/ |
| Landing Zone 搭建概述（5 蓝图） | https://help.aliyun.com/zh/cgc/user-guide/build-a-landing-zone-1 |
| 治理健康检测 3.0 检测项 | https://www.alibabacloud.com/help/zh/cgc/user-guide/supported-detections-3-0-model |
| Landing Zone 场景方案总览 | https://help.aliyun.com/knowledge_detail/300734.html |
| 企业多账号统一架构方案 | https://help.aliyun.com/zh/caf/enterprise-multi-account-unified-architecture-solution |
| CEN-TR 企业级云上互联 | https://help.aliyun.com/zh/caf/uses-cen-instances-and-transit-routers-to-establish-enterprise-grade-network-connections |
| Light Landing Zone 方案 | https://help.aliyun.com/zh/landing-zone/solution-148 |
| 多账号操作日志统一归集与审计 | https://help.aliyun.com/zh/landing-zone/solution-37 |
| 管控策略边界控制方案 | https://help.aliyun.com/zh/well-architected/solution-39 |
| LZ 咨询服务 SOW（五版本） | https://help.aliyun.com/document_detail/2531626.htm |
| 管控策略概述 | https://help.aliyun.com/zh/resource-management/resource-directory/user-guide/control-policy-overview |
| 管控策略示例 25 例 | https://www.alibabacloud.com/help/zh/resource-management/resource-directory/user-guide/examples-of-custom-access-control-policies |
| 防护规则 | https://help.aliyun.com/document_detail/321927.htm |
| 云 SSO 文档 | https://help.aliyun.com/zh/cloudsso/ |
| 可信服务概述 | https://help.aliyun.com/knowledge_detail/208133.html |
| 多账号企业付款方案 | https://help.aliyun.com/document_detail/2929439.html |
| 使用标签分账 | https://help.aliyun.com/knowledge_detail/183697.html |
| 多账号解决方案（白皮书+视频） | https://open.aliyun.com/multi-account |
| 在线实操：搭建 LZ（免费） | https://www.aliyun.com/solution/tech-solution-deploy/2506085 |

## 14. 二轮深度补充（2026-10 第二轮调研）

### 14.1 资源目录 RD：配额、邀请、删除（现行版，更新至 2026-09）

| 限制项 | 默认最大值 | 可提升 |
|---|---|---|
| 每账号可创建资源目录 | 1 个（成员账号不能创建 RD） | 否 |
| 资源夹数量 | 100 个（不含 Root） | 是 |
| 资源夹层级深度 | 5 级（不含 Root） | 否 |
| 目录中成员数量 | **50 个** | 是 |
| 每日有效邀请数 | 20 条 | 是 |
| 邀请记录过期 | 14 天 | 否 |
| 自定义管控策略数量 | 1500 个 | 否 |
| 每节点可绑定自定义策略 | 10 个 | 是 |
| 单策略最大长度 | 4096 字符 | 否 |
| 30 天周期可删除资源账号 | 成员<100：10 个；100≤成员≤10000：10%；>10000：1000 个 | 是 |
| 目录联系人 | 10 个 | 否 |

⚠️ 口径冲突：旧版文档写"成员 20 个、单策略 2048 字符"；引用时注明现行版（[使用限制](https://help.aliyun.com/zh/resource-management/product-overview/limits)）。

- **邀请（Handshake）**：填账号 UID 或登录邮箱，可批量；被邀请方在控制台/邮件接受；加入后自动创建 RAM 角色 **ResourceDirectoryAccountAccessRole** 供管理账号统一管理。API 全套：InviteAccountToResourceDirectory / AcceptHandshake / DeclineHandshake / CancelHandshake 等。跨资源目录迁移需原目录开启"允许成员接受外部邀请"（默认关闭），且双方须同属中国站或国际站、企业实名信息一致。
- **删除成员**：先 SetMemberDeletionPermission 开启"成员删除许可"，再 CheckAccountDelete 检查后删除；资源账号 root 登录默认禁用。

### 14.2 云 SSO 深度

- **访问配置**：会话时长 900~43200 秒（默认 3600）；用户门户会话最长 8 小时不可改；实际有效期 = min(访问配置时长， RAM 安全设置 1~24h 默认 6h)。
- **内置访问配置模板 9 个**（AI 云治理中心自动创建）：Administrator / Iam / Billing / AuditAdministrator / LogAdministrator / LogAudit / NetworkAdministrator / SecurityAudit / SecurityAdministrator。
- **SCIM**：云 SSO 支持账户+组同步（RAM 仅账户、用户名转小写）；SCIM 密钥仅显示一次；IDaaS EIAM 应用市场有"阿里云-云SSO"应用一键同步；官方教程覆盖 KeyCloak/Entra ID/Okta。
- **选型边界**：RAM=单账号内身份；云 SSO=基于 RD 的多账号统一身份（访问 RD 账号本质是扮演账号内 RAM 角色）；RAM 角色 SSO=不想云上建用户、按 IdP 组分权限；IDaaS=企业身份中枢（钉钉/企微/飞书/AD/LDAP）向下 SCIM 供给。
- **委派管理员上限**：服务目录 1 个、云防火墙最多 5 个、云安全中心最多 10 个；添加后须回到云 SSO 控制台"启用该委派管理员账号"（两步缺一不可）。

### 14.3 管控策略完整 JSON 样例（官方 25 例精选）

禁止公网出口（EIP/NAT）：
```json
{ "Version": "1", "Statement": [ {
  "Action": ["vpc:AllocateEipAddress","vpc:AllocateEipAddressPro","vpc:AllocateEipSegmentAddress","vpc:CreateNatGateway"],
  "Resource": ["*"], "Effect": "Deny",
  "Condition": { "StringNotLike": { "acs:PrincipalARN": "acs:ram:*:*:role/resourcedirectoryaccountaccessrole" } } } ] }
```
仅允许从 IPAM 地址池创建 VPC（未携带池 ID 即拒绝）：
```json
{ "Statement": [ {
  "Action": ["vpc:CreateVpc","vpc:AssociateVpcCidrBlock"],
  "Resource": "*", "Effect": "Deny",
  "Condition": { "Null": { "vpc:Ipv4IpamPoolId": "true" } } } ], "Version": "1" }
```
删除 ECS 必须 MFA：
```json
{ "Statement": [ { "Action": "ecs:DeleteInstance", "Effect": "Deny", "Resource": "*",
  "Condition": { "Bool": { "acs:MFAPresent": "false" } } } ], "Version": "1" }
```
保护 RD 管理通道：
```json
{ "Version": "1", "Statement": [ { "Effect": "Deny",
  "Action": ["ram:UpdateRole","ram:DeleteRole","ram:AttachPolicyToRole","ram:DetachPolicyFromRole"],
  "Resource": "acs:ram:*:*:role/resourcedirectoryaccountaccessrole" } ] }
```
（来源：[官方示例页](https://help.aliyun.com/zh/resource-management/resource-directory/user-guide/examples-of-custom-access-control-policies)，另含禁改 RAM 用户/组/角色、禁改 SSO 配置、禁关审计投递、限共享目标等 20+ 例。）

### 14.4 网络深度

- **CEN 企业版 TR 计费三项**：连接费（中国内地 0.05 美元/个/小时）+ 流量处理费（0.02 美元/GB，流入 TR）+ 跨地域带宽费（按流量：CDT 结算、内地互通 0.072 美元/GB 只收出向；或带宽包：内地互通 34 美元/Mbps/月）。带宽包可拆分多条跨地域连接，**超限流量直接丢弃**；按流量默认限速内地↔内地 1000Mbps、涉海外 100Mbps。基础版 TR 已于 2022-03-31 停售。
- **云防火墙布防**：互联网边界 / VPC 边界 / NAT 边界 / DNS 防火墙 / IPv6 五类日志；IPS 观察模式 vs 拦截模式（宽松/中等/严格），实践先观察后拦截、常用"中等"；VPC 边界基于 TR 或对等连接引流，自动创建路由表条目（路由学习 15~30 分钟）。
- **PrivateLink（私网连接）**：服务方建终端节点服务（NLB/ALB/GWLB 后端），使用方建接口终端节点（自动 ENI+私有域名）；**跨账号、跨地域**（2026-04 起），支持中国站与国际站账号间私网连接（不支持"中国内地↔内地之外"跨站点）——共享服务发布的第三种收敛路径，替代全网打通。
- **TR 规格（已核实）**：单 TR 集群最大 **400Gbps** 转发性能；单 VPC 连接最大 50Gbps（杭州/上海/北京/深圳/中国香港/新加坡为 50Gbps，其余地域 10Gbps）——出处为[云网络卓越架构设计文档](https://help.aliyun.com/zh/cloud-network-well-architected-design/build-a-cross-region-network-on-the-cloud-with-cen)（CEN 配额页无此数字，引用请指向该文档）。
- **互通验收**：官方无统一验收清单；可用 NIS 的路径分析、CEN/VPC 拓扑（支持多账号模式）做验证。

### 14.5 行业落地（三轮已核实）

- **金融**：《金融企业上云登陆区白皮书》2023-05-18 金融创新峰会发布，阿里云首次金融行业 LZ 白皮书，**共 11 章**（[ebook 7991](https://developer.aliyun.com/ebook/7991)；逐章目录需登录下载 PDF），官方发布文明确**四大建设要点**：资源架构（多账号结构/财务规划/标签/命名规范）、网络规划（网络分区/DMZ/混合组网/同城异地容灾网络）、安全防护（基础安全/身份权限/数据安全）、容灾设计（技术选型/方案设计/参考架构）。等保/密评映射见 `aliyun-compliance.md`。
- **医疗 GxP**：医疗及生物行业蓝图 = 标准蓝图 + CEN DMZ 隔离区 + 服务日志投递 + 医疗生物行业合规包——对应 **GxP 欧盟附录 11 合规包（约 73 条规则**：操作审计全量跟踪、漏洞防护、RDS/OSS/NAS 等备份、传输/静态加密、删除保护、MFA/AK 轮转、数据库与 WAF 审计日志、多可用区）+ 可选中国 GMP 附录《计算机化系统》合规包；另有独立[《GxP Landing Zone 解决方案》](https://help.aliyun.com/zh/landing-zone/solution-155)（2024-03，七模块）。信任中心 GxP 页：完成 NMPA/欧盟 GMP/FDA/CAMP5 评估与 **FDA 21 CFR Part 11** 就绪评估。
- **政务/央国企**：官方无政务专属 LZ 白皮书（已确认）；可引用**信通院牵头、阿里云参编《上云指导：云基础环境框架（Landing Zone）设计与应用》白皮书**（2023-11）与中体彩案例（见 §15.3）作为该场景代表材料。

### 14.6 开源与 IaC 生态（重要新发现）

- **Landing Zone Accelerator（LZA）**：阿里云官方开源（[GitHub](https://github.com/aliyun/landing-zone-accelerator-on-alibaba-cloud)、[文档](https://help.aliyun.com/zh/caf/landing-zone-accelerator)），纯 Terraform；内置 **六大核心模块**搭建代码：资源管理、身份权限、财务管理、网络规划、安全防护、合规审计；工程结构含 account-factory（账号工厂）、guardrails（detective/preventive）、identity/cloudsso、log-archive（actiontrail/config/log-audit）、network（cen/dmz）、security（bastion-host/cloud-firewall/kms/security-center/wafv3）；同时适用于 **Landing Zone 与 AI Landing Zone**（可统一部署或两份独立）。官方明示：LZA 本身不保障合规，默认配置仅为示例。
- **Terraform Registry 模块族**（三轮全量核实）：alibabacloud-automation 组织 landing-zone 系列 **8 个 GitHub 仓库、7 个已发布 Registry**（source 统一 `alibabacloud-automation/landing-zone-*/alicloud`）：log-archive(v3.0.0)、guardrails(v2.0.0)、account-factory-role-based-sso、cloudsso、actiontrail-log-archive、resource-structure（启 RD、建 Core 夹与核心账号）、config-log-archive。
- **ROS 模板库**：官方 ros-templates 仓库（solutions/ 下 20 个目录）**无 Landing Zone 专用模板**——LZ 自动化路径就是 CGC 蓝图（控制台向导）+ Terraform（LZA/模块族）。
- **老仓库** `aliyun/alibabacloud-landing-zone`：未废弃（2026-10 仍在更新），定位为 LZ 场景化**方案物料库**（8 大版块 × "一页方案 PPT + 说明文档 + Terraform 脚本"），并注明持续产品化为云治理中心；工程化落地已由 LZA 接棒。
- **Provider 能力**：`alicloud_resource_manager_control_policy` 资源（v1.120.0 起）可管管控策略。
- AI 云治理中心账号工厂自 2024-08 起支持 Terraform。

### 14.7 出海/跨境

- 国内站与国际站账号相互独立：跨 RD 迁移须同站；PrivateLink 支持两站账号间私网连接但不支持"内地↔内地之外"跨站点；出海企业常见做法是国际站另起一套 LZ。
- 《阿里云出海网络白皮书》（[官方](https://help.aliyun.com/zh/cloud-network-well-architected-design/the-global-expansion-of-enterprises-alibaba-cloud-network-white-paper)）：场景章含 GA 轻装出海、高可用云上数据中心、高速互联、全球化办公接入、私网访问通义大模型；规划章含多 VPC 划分、以 CEN 为核心跨地域 DCI、专线混合云、VPN 远程接入。
- 出海服务叙事把 LZ 作为"上好云"第一步（美妆企业出海先建多账号与权限管控体系）；"LZ+WA 双引擎 30 天海外上线"为宣传口径，数字待核实。

### 14.8 在线实操与案例细节

- **在线实操**：`aliyun.com/solution/tech-solution-deploy/2506085`——50 分钟、预估 0 元、云治理中心标准蓝图三步（创建资源夹→创建核心账号→防护规则）。
- **中兴通讯**（[案例页](https://open.aliyun.com/cases/15)）：资源管理统一管理全公司云账号；存量账号邀请进目录、新增由技术部创建；Root 与成员根账号密码收回统一掌管；从财务汇款角度追溯非统管账号；账号架构=管理账号+核心账号（Logging/Security/Ops/SharedService）。
- ⚠️ 口径修正："中兴通讯 20+ 账号收敛"不准确——官方实名案例页无"20+"表述；"国内某通讯企业 20+ 云账号"是《企业多账号统一架构方案》（solution-12）中的**匿名**样板。售前引用时分开表述。
- 众安国际：业务线隔离+环境隔离的账号与授权体系；vivo：规划-运营-检查-改进四阶段全生命周期管理；巴斯夫详见 §15.3。

### 14.9 Azure Landing Zone 对照（非官方对照，Azure 侧为官方口径）

| Azure LZ 概念 | 阿里云对应 | 差异要点 |
|---|---|---|
| Management Group 层级（8 级） | 资源目录资源夹（5 级、100 个） | 深度与配额不同 |
| Subscription（计费+缩放单位） | 成员账号 | Azure 订阅内还有 RG；阿里云账号即隔离边界 |
| Azure Policy（挂 MG） | 管控策略（绑资源夹/成员） | Azure 有 Audit/DeployIfNotExists 修正类效果；阿里云只做 Allow/Deny |
| Subscription vending | 账号工厂（GCC/LZA/GitLab+Terraform） | 机制对应、名词不同 |
| Connectivity 订阅（Hub-Spoke/vWAN） | 网络/共享服务账号 + CEN-TR + DMZ | 中央防火墙=NVA/Azure Firewall vs 云防火墙+TR |
| Entra ID 租户 | 云 SSO/IDaaS | 阿里云无租户概念 |
| Management 订阅（Log Analytics+Sentinel） | 日志账号（SLS+OSS 集中投递） | 对应 |
| Sandbox/Decommissioned MG | 无内置，自建资源夹 | 阿里云蓝图未内置 |
| Azure LZ Accelerators | CGC 五蓝图 / LZA | 定位相近 |

### 14.10 检测项增量与运行机制

- 3.0 模型页结构确认（三轮已全量解析页面内嵌数据，374 行完整还原）：五支柱=安全/稳定/成本/效率/性能（与卓越架构五支柱对齐）——**安全 15 类、稳定 8 类**（实例规格/稳定版本/到期风险/风险巡检/备份快照/集群架构/限额容量/监控管理）、**成本 4 类 20 项**（成本监控/付费方式优化/应用资源优化/成本策略）、**效率 3 类 26 项**（资源管理/账号体系/资源供给与编排——含 12 个云产品"调用已弃用 API"检测）、**性能 3 类 15 项**（性能监控/利用弹性资源/网络设计）；页面另附"**移除的检测项**"附表 30 项，引用勿与现行项混算。AI 治理成熟度检测（2026-06 起）当前 **41 项**，覆盖安全/稳定/成本/性能（效率待开放），样例"AgentIdentity 工作负载身份未配置用户身份 OIDC 穿透"。
- 运行机制：每天自动检测一次+手动重检；部分检测项支持自定义参数与检测范围；多账号模式下管理账号统一设参全成员生效；API `ListEvaluationMetadata` 暴露检测项元数据与专项 TopicCode（ack/ai/nis）；风险修复支持自动/手工；成熟度报告支持 PDF/Excel 下载与订阅。

### 14.11 成本构成一览

| 能力 | 计费 |
|---|---|
| 资源目录 / AI 云治理中心（搭建、检测、账号工厂、蓝图） | 免费 |
| 配置审计、操作审计、配额中心 | 基础治理产品免费（投递到 SLS/OSS 下游存储费用另计，待核实） |
| 云 SSO | **免费**（官方明文："云 SSO 为免费产品，开通后即可正常使用，不收取任何费用"） |
| CEN/TR | 收费（连接+流量处理+跨地域带宽，见 14.4） |
| 云防火墙 / 堡垒机 / 云安全中心 | 收费。堡垒机：开发者版 180 元/月起、轻量版 700 元/月起（官方明价，扩展资产 150 元/5 资产、并发 50 元/个等），正式类（基础版/企业双擎版/国密版）未公开标价、以控制台报价为准；云安全中心版本矩阵见 `aliyun-compliance.md` §8 |
| LZA 开源 | 免费，仅为开通的云资源付费 |
| LZ 咨询/实施服务 | 收费五版本（见 §2） |

### 14.12 二轮口径修正汇总

1. RD 成员配额现行 50 个（旧版 20）；单策略 4096 字符（2024 文档 2048）——引用注明版本。
2. "中兴 20+ 账号"出自匿名样板，非实名案例。
3. 官方新增开源 LZA——IaC 交付首选起点。

## 15. 三轮深度补充（2026-10 第三轮调研）

### 15.1 节省计划 vs 预留实例券（官方规则页核实）

| 对比项 | 节省计划 Savings Plan | 预留实例券 RI |
|---|---|---|
| 本质 | **金额型**：承诺消费金额换按量折扣，按折扣价抵扣账单 | **规格型**：抵扣按量实例（不含抢占式）账单并可预留资源（按计算力交付，不绑定单台） |
| 适用范围 | ECS 计算型（ECS+ECI）；通用型（+云盘/云盘性能）；数据库通用型（RDS）；另有转发路由器型、万相型、大语言模型推理型等 | 计算资源（vCPU+内存）+镜像（Windows 券含镜像费；Linux 券不可）；不抵扣存储与网络账单 |
| 粒度 | 承诺金额×时长×预付比例决定折扣（全预付>部分>0 预付）；AI 通用型为月承诺 3/6/12/24 个月，最高 5.3 折 | 地域级（跨规格族内抵扣、不预留）/可用区级（同规格、支持资源预留）；支持拆分/合并/改可用区 |
| 退改 | 用户中心口径"不支持退订，到期自动失效"；国际站 2026-04-03 起支持未使用全额退款（国内站是否同步待核实）；支持升级承诺金额 | 五天无理由全额退款（每账号每年 1 次，与包年包月/资源包共享额度） |
| 抵扣优先级 | **RI、资源包 → 节省计划**（RI 第一优先） | 第一优先级 |
| 官方建议 | "建议您使用节省计划，而不是预留实例券。节省计划灵活性更好、折扣更有优势" | 适合：可用区级资源预留、拆分合并弹性、Windows 镜像抵扣 |

**多账号共享**：前提是开通**企业账号中心**或财务托管关系；"主账号可对 RI、SCU、Saving Plan 设置共享，是**账单层面**而非资源层面共享"；节省计划/RI/SCU/优惠券均支持共享给 **100 个账号**；官方最佳实践："建议企业内部使用一个账号集中购买和管理节省计划"，再按测算范围共享给其他账号。

### 15.2 ACK One Fleet：多集群治理与 LZ 的叠加

ACK One（分布式云容器平台）面向混合云、多集群、容灾场景；**Fleet 舰队**提供统一控制面（标准 K8s API），能力含 GitOps 应用分发（托管 ArgoCD）、流量管理（MSE 网关+多集群 Service）、作业分发、全局监控。**跨账号/跨云注册**：官方支持用 Fleet 管理跨阿里云账号的 ACK 集群与 IDC 自建集群（非 ACK 集群经注册集群接入）——LZ 的账号边界不被打破：各成员账号集群注册关联进 Fleet，账号无需合并。售前定位：**LZ 管账号/身份/财务/合规平面，Fleet 管应用分发/流量平面**，叠加即多账号容器治理标准答案。

### 15.3 案例深挖（官方案例页核实）

- **巴斯夫**（[案例](https://open.aliyun.com/cases/14)、[CAF 文档](https://help.aliyun.com/zh/caf/basf-builds-landing-zones-to-accelerate-cloud-transformation)）：全球数字化服务部门（GD）按 CAF 组建 **7 类角色 CCoE**（Project Owner / Cloud Strategy / Cloud Architect / DevOps Architect / Support and Operator / Technical & Business Consultant / Demand & Cost Manager），部署公有云前基于 LZ **八大领域**梳理需求；统一规划账号架构/身份权限/网络规划/安全合规/成本管理五大治理域；自服务平台**"1 Step 4 Clicks, Easy on Cloud"**——全球团队审批后**数小时**交付云环境；GD 用财务中心分析帮业务部门预估季度预算。受访人刘博亚（巴斯夫大中华区 digital service 负责人，2021 云栖分论坛）。
- **迪卡侬**（[案例](https://help.aliyun.com/document_detail/431941.html)）：2021 年初启动 LZ 设计；以 RD 为基础"为每个项目创建独立云账号、按树形结构组织"，管理**近百个项目**；云 SSO 对接总部 IdP（SAML）+强制 MFA；权限模型五档访问配置——`ram-admin`（可授权）/`admin`（无授权能力）/`paasadmin`（RDS/Redis/Kafka 等 PaaS）/`readonly`/`custom`；用 Terraform module 自动化全部身份权限管理；近千名跨部门人员与供应商统一身份，供应商项目内网隔离。
- **小马智行**：中美两地，Robotaxi/Robotruck/数据标注跑阿里云；IaC 三目标"部署可评审、版本化、多环境一致"；因多云战略+混合云现状选 Terraform+Git 版本化，Jsonnet 解决模板复用。
- **流利说**：自动化三维度——"部署自动化、管理自动化、治理自动化"（Terraform 官方文档客户案例）。
- **中体彩**：三阶段演进，第三阶段（2021）"由私有云、公有云、统一云管平台、专用通道组成的混合云"；共享服务租户（共享带宽/NAT/防火墙/DDoS 集中）与业务租户二分（此为专有云租户体系口径，见 `cross-cloud-mapping.md` §6）；RAM 用户组实现租户内基于角色的授权。

### 15.4 LZ/WA 伙伴体系

- **LZ 生态伙伴**：以"Landing Zone 生态合作伙伴授牌认证"+联合解决方案为载体；2021 年首家埃森哲；截至 2023-04 已认证 **11 家伙伴、联合服务 200+ 企业客户**；2022 云栖年度 8 家：埃森哲、德勤、浩鲸、谐云、神州数码、贝斯平、飞络、东软；官网另列凯捷、上海冠闵。配套标准赋能课程体系（市场规模/痛点/方案价值/模块明细/咨询模板/产品实操/实施策略/案例）与伙伴技术赋能训练营（40+ 伙伴 150+ 架构师）。
- **AI LZ 技术伙伴认证**（2026 首批）：伙伴基于客户画像推导需求、形成 AI LZ 方案并通过智能云管理 OpenAgent 完成搭建演示；神州数码首批通过。
- **WA 生态伙伴认证六步**（[门户](https://open.aliyun.com/well-architected)）：提交意向 → 审核 → 线上笔试 → 闭门培训+线下答辩（产品专家面对面）→ 认证授牌（以企业为单位）→ 合作开展；**首批 7 家**（2024-09 云栖"用云实践话题论坛"授予）：埃森哲中国、上海安畅、江苏鼎峯、上海飞络、浩鲸云计算、广州青莲网络、杭州谐云（[官方文章](https://developer.aliyun.com/article/1610661)）；2025 云栖第二批授牌 9 家。设**"领航合作伙伴"**层级（续牌考核优秀者），2025 年度四家：埃森哲、上海安畅、江苏鼎峯、上海飞络。

### 15.5 混合云组网选型（官方三分法 + 冗余组合）

| 方案 | 官方口径 | 适用 |
|---|---|---|
| VPN 网关 | 基于互联网，"延迟和可用性取决于互联网"；主备双机热备 | 中小带宽、快速开通、时延不敏感 |
| 物理专线（高速通道） | "网络质量好，带宽高"；自主接入/一站式接入 | 大带宽、低时延、强合规 |
| 智能接入网关 SAG | "一站式快速上云，互联网就近加密接入"；多分支首选 | 多分支/门店、无专线资源 |

- SAG 形态：SAG-100WM（桌面型 ≤50Mbps）、SAG-1000（机架型 ≤500Mbps，专线/宽带/4G 混合）、vCPE 镜像（他云 VM/x86，可做多云互联）、SAG App（移动办公）；设备先入云连接网 CCN，CCN 绑 CEN 实现跨地域互通。
- 冗余组合：最多 4 条专线 ECMP；专线主备+CEN；SAG 作专线备份；IPsec-VPN+专线主备；跨境带宽由中国联通运营。
- 选型决策点（依官方口径整理）：规模（单 IDC vs 多分支）→ 带宽 → 时延要求 → 交付速度（SAG/VPN 分钟级 vs 专线周级）→ 容灾等级 → 终端类型 → 跨境。

### 15.6 三轮清欠回收（2026-10，18 项待核实的处置结果）

**已查实并回填正文**：金融白皮书 11 章/四大建设要点；GxP 蓝图与 73 条合规包规则、solution-155；政务=信通院参编白皮书+中体彩；ROS 无 LZ 模板；TF 模块族 8 仓库/7 Registry；老仓库未废弃（物料库）；云 SSO 官方明文免费；堡垒机两档明价+三类正式版；3.0 检测项五支柱全量（含"移除项"30）；TR 400Gbps；VPC 地址规划 /11→/15→/17；国际站迁移 Step 4="Manage Resources on the Cloud"；BASF 七角色 CCoE 与"1 Step 4 Clicks"；Light LZ tfvars 四组变量；CAF K15 核心特征；98 vs 100 双口径；WA 首批 7 家名单。

**仍未闭环（留档）**：金融白皮书逐章目录（PDF 需登录）；堡垒机正式类（基础版/企业双擎版/国密版）公开标价；跨国白皮书 8.4 连载正文（站内阅读）；解决方案库差的 2 篇定位（疑为下线或宣传约数）；AI LZ 白皮书"AI 平台层/Agent 运行时/AI 网关/AI 安全护栏"四层命名无公开文字出处（引用须标注"据白皮书架构图，待 PDF 核对"）。
