# 阿里云云采用框架（CAF）官方全景

> 全网调研档案（第二轮，采集于 2026-10-28）：补齐本包此前只有 AWS CAF（`aws-caf.md`）的空缺。所有结构类结论（阶段数、策略数）均逐字核实过官方页面，未套用 AWS CAF。引用官方结构时以本篇为准。

## 1. 官方定义与入口

- 门户定义（[open.aliyun.com/caf](https://open.aliyun.com/caf)）："云采用框架（Cloud Adoption Framework，简称 CAF）是经过验证的企业上云的路线指引。框架基于阿里云服务过的大量企业客户经验，总结了企业在上云生命周期可能遇到的挑战，并提供解决策略、最佳实践以及辅助工具等，帮助企业实现上云价值最大化。"
- 帮助文档定义（[help.aliyun.com/zh/caf/](https://help.aliyun.com/zh/caf/)）："为企业上云提供策略和技术的指导原则和最佳实践，帮助企业上好云、用好云、管好云……将企业云采用分为四个阶段。"
- 门户列出的五点价值：正确决策 / 清晰上云路线 / 保障安全合规 / 平稳的云迁移 / 助力业务创新。

## 2. 官方框架结构：上云"四步走"（已核实）

| 阶段 | 官方一句话定位 | 帮助文档章节 |
|---|---|---|
| 1. 上云战略 | 业务迁移上云 / 业务创新上云 | 1.1 企业上云的主要动机；1.2 上云所需的企业组织模型及核心职责 |
| 2. 上云准备 | 基础设施布局和建设（Landing Zone 企业上云治理框架） | 2.1 云上管理和治理框架（什么是云上 Landing Zone） |
| 3. 应用上云 | 确定上云策略、筛选应用、确定优先级 | 3.1 应用上云规划；3.2 应用上云实施 |
| 4. 运营治理 | 风险治理办法 + 阿里云上的治理基线 | 4.1 风险治理方法论；4.2 治理基线（身份权限治理基线） |

帮助文档另有：背景介绍、用好云（卓越架构所在）、典型实践案例、结束语、基本概念。

## 3. 各阶段核心方法论

### 3.1 上云战略：动机四维度 + 两类上云路径

**动机四维度**（[企业上云的主要动机](https://help.aliyun.com/document_detail/300730.html)）：
- **追求新机会（Opportunity）**：并购与出海、进入新业务领域、业务模式转型、规模扩张、上下游协同、缩短 GTM、技术架构升级、提升客户体验
- **防范风险（Risk）**：资产折损、数据资产保护、防泄露、隐私安全、合规、容备级别与业务连续性、IT 供应链风险、降低技术复杂度
- **提升效能（Efficiency）**：研发效率、敏捷开发、降低运维难度、跨部门协同、数字化组织、使用最新 IT 设施
- **控制成本（Cost）**：自建一次性投资、运行/维保/运维成本、闲置成本、故障风险成本、自研长周期高成本、大规模 CAPEX 资金占用

**两类上云路径**（门户原文）：**业务迁移上云**（加速资源交付、降本、用最新技术、提高安全性）与**业务创新上云**（IoT/大数据/业务中台等云上创新能力降低创新门槛）。

### 3.2 上云准备：Landing Zone 顶层设计

门户原文："企业在第一个应用上云前，需要有一整套顶层设计和一系列基础框架，为后续的业务上云扫清障碍。否则，可能会导致后续业务上云面临成本、网络、安全、效率等多方面的问题。"——**Landing Zone 是"上云准备"阶段的核心交付物**（LZ 细节见 `aliyun-landing-zone.md` 与 `aliyun-landing-zone-official.md`）。

### 3.3 应用上云：官方 6 个上云策略 + 实施流程

**6 策略**（[业务调研](https://help.aliyun.com/knowledge_detail/300749.html)，逐字核实）：

| 策略 | 中文 | 要点 |
|---|---|---|
| Retire | 淘汰 | 冗余、不再具备业务价值的系统 |
| Retain | 保留 | 留在原环境不迁移（风险极大/过于老旧/政策因素/耦合紧密） |
| Re-host | 新托管 | 物理机替换为云上虚拟机/裸金属，不改运维方式（稳态 IT、ERP、源码不可控） |
| Replatform | 新平台 | 用托管云服务（PaaS）替换线下自建基础设施 |
| Re-architect | 重构/新架构 | 基于云平台重构为云原生应用（敏态、高并发、容器化） |
| Replace | 替换 | 丢弃现有应用采购同类 SaaS，或云下 license 转阿里云市场 |

⚠️ 勘误：阿里云官方为上述 6 策略（含 Replace），与业界"6R"、AWS 7R 组成不同；CAF 文档无"4R/6R"字样；"感知-评估-搬迁-优化"未见于现行官方页面，不建议引用。

**应用调研 K15 核心特征**（[业务调研](https://help.aliyun.com/knowledge_detail/300749.html)配图已核实）：评估工具采集"非技术属性和技术属性两大类，核心特征 15 个"——①业务关键性 ②应用生命周期阶段 ③部署限制 ④服务水平协议需求 ⑤数据分类 ⑥数据限制 ⑦应用的负载容量 ⑧应用定制化需求 ⑨集成性&独立性 ⑩硬件依赖性 ⑪网络需求 ⑫存储需求 ⑬计算能力需求 ⑭中间件需求 ⑮数据库需求；配图将其归入非技术属性（业务一致性、风险和监管）与技术属性（应用架构、基础设施架构）四类 24 个调研特征。

**实施流程**（[上云迁移实施](https://help.aliyun.com/zh/caf/cloud-migration-implementation)）：以应用为单位推进；实施组织建议分五组——**项目管理办公室（PMO）/实施架构组/应用开发组/运维组/测试组**；输出含全部任务、时间段、各方人员的迁移计划表。上云典型场景按 Re-host（推荐 SMC）/Replatform/Re-architect 展开（[use-cases-of-cloud-migration](http://help.aliyun.com/zh/caf/use-cases-of-cloud-migration)）。

### 3.4 运营治理：风险治理方法论 + 治理基线

风险识别&评估——"输出清晰的风险定义、风险治理策略、治理策略的实施制度，并建立一定的监管流程来监督策略的实施"；示例风险：信息安全、云上数据泄漏、业务连续性。治理基线首篇为《身份权限治理基线》。官方强调"过度治理会限制云上业务的敏捷发展"。

## 4. CAF × Landing Zone × 卓越架构（官方三层关系）

- LZ = CAF 第二阶段"上云准备"的落地框架；
- 卓越架构（五支柱）属于"用好云"阶段的方法论（帮助文档"用好云"栏目）；
- AI CAF 报告页表述："AI 治理与运营……以'安全、稳定、效率、成本、性能'为核心支柱，通过 AI 卓越架构落地治理要求"——**CAF 管采用生命周期，LZ 管落地底座，WAF 管持续架构治理**。

## 5. 迁移方法论与工具生态

**迁移流程官方口径（三个并存版本，均为现行）**：
1. CAF 迁云流程（[迁云概述](https://help.aliyun.com/document_detail/438393.html)）：**现状调研 → 方案设计（云上架构+迁移方案）→ 迁移实施 → 割接实施 → 项目验收**
2. 国际站数据迁移方法论：系统调研 → 上云风险评估 → 方案设计与评审 → 系统改造 → 功能/性能测试 → 系统割接和回滚 → 系统交付与护航
3. 国际站云迁移四步旅程：Assess（咨询/Cloud Migration Hub）→ Plan and Customize（Migration Hub / 云治理中心 / LZ 服务）→ Migrate（SMC、DTS、Data Online Migration、HBR）→ **Manage Resources on the Cloud**（监控资源使用与应用性能、管理运维与权限、支撑后续基础设施部署）

**工具生态**：
- **云迁移中心 CMH（Cloud Migration Hub）**：一站式迁移平台，自动与智能的系统调研、云上规划、迁移管理。⚠️ 勘误：官方名为"云迁移中心 CMH"，**不存在"迁移中心 MC"这一产品名**。
- **服务器迁移中心 SMC**：Re-host 推荐工具，agent 方式 P2C/V2C/C2C，生成 ECS 镜像。
- **闪电立方 Data Transport**：TB～PB 级离线迁移设备。
- **DTS 数据传输服务**：数据库/NoSQL/OLAP 间迁移同步。
- **HBR 混合云备份 / Data Online Migration（OSS 在线迁移）**：Step 3 Migrate 组件。

## 6. AI CAF（概览）

官方定义（[AI CAF 报告页](https://www.aliyun.com/reports/2025-ai-caf)）："AI 云采用框架（AI Cloud Adoption Framework，简称 AI CAF）是一套围绕 AI 战略、AI 准备、AI 应用工程化构建和 AI 治理等方面，指导组织规划、构建和运营 AI 能力的端到端方法论体系，帮助企业从'能用 AI'迈向'用好 AI'"。

- **四阶段**：AI 战略 / AI 准备 / AI 应用工程化构建 / AI 治理——与经典 CAF 四步走一一对应。⚠️ "八大模块"指 AI Landing Zone（AI 准备阶段的内部结构），"五大支柱"指 AI 卓越架构（AI 治理阶段的落地物），均非 AI CAF 顶层结构。
- AI 战略五步法：明确愿景与目标 → 规划路径 → 聚焦场景 → 闭环执行 → 动态迭代。
- AI 系列深度（AI LZ、AI Lens 逐支柱、生成式 AI 指导原则）见本包 `aliyun-ai-arch.md`。

## 7. 常见误区清单（售前防坑）

1. 阿里云 CAF **没有** AWS CAF 式"六大视角"——官方只有四阶段；第三方文章的"七维度→六维度"是 AWS CAF 历史，勿混用。华为云 CAF（六阶段）也是另一家体系。
2. 迁移策略是**官方 6 策略**（Retire/Retain/Re-host/Replatform/Re-architect/Replace），不是 6R/7R。
3. "迁移中心 MC"应为**云迁移中心 CMH**；主机迁移工具是**服务器迁移中心 SMC**。

## 8. 资料索引

| 材料 | URL |
|---|---|
| CAF 门户 | https://open.aliyun.com/caf |
| CAF 帮助文档 | https://help.aliyun.com/zh/caf/ |
| 企业上云的主要动机 | https://help.aliyun.com/document_detail/300730.html |
| 业务调研（6 策略） | https://help.aliyun.com/knowledge_detail/300749.html |
| 上云迁移实施 | https://help.aliyun.com/zh/caf/cloud-migration-implementation |
| 迁云概述 | https://help.aliyun.com/document_detail/438393.html |
| AI CAF 官方报告 | https://www.aliyun.com/reports/2025-ai-caf |
| AI LZ 定义（帮助文档） | https://help.aliyun.com/zh/caf/ai-lz-definition |
