# 阿里云 AI 系列架构方法论专题（AI CAF / AI LZ / AI 卓越架构）

> 全网调研档案（第二轮，采集于 2026-10-28）：AI 系列方法论一揽子深度——AI 卓越架构（AI Lens）逐支柱最佳实践、AI 原生转型与决策框架、生成式 AI 指导原则（联合信通院）、AI Landing Zone、AI CAF 及产品落点。上一轮的 AI Lens 概述在 `aliyun-waf-official.md` §5，本篇是其深化。

## 1. 全景与时间线

| 时间 | 事件 |
|---|---|
| 2024-12-17 | 信通院 GOLF+IT 新治理领导力论坛：阿里云发布全栈 AI 负载高可用架构 |
| 2025-09-15 | 《生成式 AI 卓越架构设计指导原则》电子书上架（[ebook 8470](https://developer.aliyun.com/ebook/8470)） |
| 2025-09-24~26 | 2025 云栖大会：发布《生成式 AI 卓越架构设计指导原则》 |
| 2025-12-16 | 信通院 IT 新治理领导力论坛：发布 **AI Landing Zone 白皮书**、升级 **AI CAF**（通稿 12-19 见报） |
| 2025-12-31 | AI CAF 官方报告页上线（[aliyun.com/reports/2025-ai-caf](https://www.aliyun.com/reports/2025-ai-caf)） |
| 2026-04~05 | AI LZ 定义进入阿里云帮助文档 CAF 体系 |
| 2026-09-20 | 官方文档发布 **AI 卓越架构**（AI Lens）最佳实践 |
| 2026-09-24 | 神州数码通过首批 AI Landing Zone 技术伙伴认证；2026 云栖大会设 AI LZ+AI WAF 论坛 |

演进叙事（发布会口径）："治理挑战 → AI Landing Zone → **AIOps 驱动的智能化运营**"层层递进。（"双轨治理"一词无官方出处，勿引用。）

## 2. AI 卓越架构（AI Lens）逐支柱最佳实践

入口：[AI 时代的卓越架构](https://help.aliyun.com/zh/well-architected/excellent-architecture-in-the-ai-era)。定位原文："并非另起炉灶，而是在五大支柱之上为 AI 工作负载补充一层专项指引……传统支柱关心'资源是否充足、配置是否正确'，AI 视角则要求架构师进一步审视'模型是否可信、推理是否经济、智能体是否可控'。"

### 2.1 安全支柱（12 条 BP，[safety-pillar](https://help.aliyun.com/zh/well-architected/safety-pillar)）

核心观点：AI 攻击面从信息安全升级到"操作安全"（提示词注入可触发实际系统操作）。威胁模型对齐 **OWASP LLM Top 10（2025）与 MITRE ATLAS**。

- **输入输出边界**：BP-SEC-01 输入校验与过滤（Token 上限：对话 2048/文档 8192；正则+语义双检测）；BP-SEC-02 多层内容安全过滤（模型前+后、两套独立模型/规则）；BP-SEC-03 输出溯源校验（引用验证、事实性评分、检索回溯）
- **AI 数据安全**：BP-SEC-04 数据分级与访问边界（四级分级，向量库按级隔离）；BP-SEC-05 共享 AI 服务租户隔离（会话级隔离、高安全租户独占推理实例）；BP-SEC-06 向量库加密与访问控制（AES-256、Collection 级 KMS 密钥）
- **模型与制品安全**：BP-SEC-07 模型 SBOM 来源追溯；BP-SEC-08 CI/CD 制品签名校验（cosign、KMS）；BP-SEC-09 RAM 细粒度模型访问控制（权重下载限角色+审批）
- **智能体安全**：BP-SEC-10 工具最小特权（独立 Service Account、运行时参数校验）；BP-SEC-11 高影响操作审批（资金/删除/权限/外发，超时默认拒绝）；BP-SEC-12 完整审计与行为重放（日志 ≥6 个月）

### 2.2 稳定支柱（12 条 BP，[stabilizing-pillar](https://help.aliyun.com/zh/well-architected/stabilizing-pillar)）

核心观点：AI 系统独特维度是"输出正确有用"——返回 200 但输出无意义即业务失效。

- **推理健壮性**：BP-REL-01 多模型兜底（主→备→缓存三级+熔断器）；BP-REL-02 配额与限流反压（令牌桶、优先级队列、配额预热）；BP-REL-03 跨 AZ 部署与健康检查路由（深度健康检查须验证模型加载而非进程存活）
- **输出质量**：BP-REL-04 结构化输出 Schema 强制校验；BP-REL-05 关键决策自洽性校验（Self-Consistency 多次推理投票）；BP-REL-06 提示词变体重试
- **数据与知识**：BP-REL-07 知识库新鲜度 SLA 监控；BP-REL-08 向量库高可用（多副本跨 AZ+快照）；BP-REL-09 检索失败优雅降级
- **智能体与工作流**：BP-REL-10 任务断点续跑（状态持久化+幂等）；BP-REL-11 外部工具调用熔断；BP-REL-12 智能体 SLO 定义
- 关键 SLI：任务完成率、端到端时延（P50/P90/P99）、**TTFT**、输出质量评分（LLM-as-Judge）；示例 SLO：任务完成率 ≥95%、P90 端到端 ≤30s、质量评分 ≥4.0/5.0

### 2.3 成本支柱（11 条 BP，[cost-pillar](https://help.aliyun.com/zh/well-architected/cost-pillar)）

核心观点："AI 系统的经济性不是事后优化，而是架构设计的第一性约束"；成本重心转向随调用量变动的消费型支出。

- BP-COST-01 按任务复杂度匹配模型规格 / 02 模型路由 / 03 蒸馏与量化降本 / 04 共享 GPU 池统一推理服务 / 05 提示词与输出预算工程化 / 06 上下文缓存与语义缓存分层复用 / 07 批量与异步推理 / 08 承诺用量与资源包 / 09 弹性伸缩按需付费 / 10 训练数据生命周期管理 / 11 向量数据库分层存储
- 关键数值：输入/输出单价比 2.5~4 倍；思考 Token 可占输出近八成且按输出单价计；GFLOP/Token（7B≈14、720B≈144）；GPU 利用率自建约 30% → 池化约 75%；批量推理五折；隐式上下文缓存约为输入价 20%；案例综合节约约 63%

### 2.4 效率支柱（10 条 BP，[efficiency-pillar](https://help.aliyun.com/zh/well-architected/efficiency-pillar)）

核心观点："模型永远'没做完'"，效率=让持续改进以可承受成本、可预测节奏、可规模化方式运转。

- BP-EFF-01 提示词注册中心（版本化+A/B 5%~10% 灰度+自动回滚）/ 02 自动化评估流水线（离线套件+在线采样）/ 03 标准化实验跟踪（MLflow）/ 04 复用共享组件 / 05 LLMOps 流水线 / 06 数据接入与知识库自动刷新 / 07 可观测驱动改进闭环 / **07B AI 专属可观测体系**（语义质量、行为漂移、推理链路、成本效率四信号）/ 08 AI 平台团队与服务目录 / 09 AI 治理 RACI / 10 知识沉淀与组织学习
- 关键指标：反馈闭环目标 24-48 小时；LLMOps 全自动 4-8 小时 vs 人工 3-5 天

### 2.5 性能支柱（10 条 BP，[performance-pillar](https://help.aliyun.com/zh/well-architected/performance-pillar)）

核心观点：推理耗时 2~30 秒成主导，"度量先行、瓶颈驱动"——80% 精力投入贡献最大时延的 20% 环节。

- BP-PERF-01 按参数量选硬件（7B→A10、14B→A30、72B→双 A100 张量并行）/ 02 模型优化技术栈（量化、TensorRT、PagedAttention、投机解码）/ 03 流式响应（SSE，TTFT<200ms 目标）/ 04 请求批处理（动态 5-20ms 窗口、Continuous Batching）/ 05 嵌入流水线优化（100-500 条/批）/ 06 检索参数调优（切片 256-512 Token、重叠 10%-20%、Top-K 10-20 重排取 3-5）/ 07 混合检索与 RRF 分数融合 / 08 全链路 Profile（时延预算机制）/ 09 多层缓存（Prompt/KV→语义→响应三层）/ 10 负载抛弃与优先级队列（P0/P1/P2）
- 关键指标：**TTFT（目标 200ms-2s，超 3s 焦虑）、ITL（<50ms）、吞吐 Token/s/GPU、Goodput、Recall@K、MRR、P50/P95/P99**

## 3. AI 原生转型与 AI 架构决策框架

### 3.1 AI 原生转型（[ai-native-transformation](https://help.aliyun.com/zh/well-architected/ai-native-transformation)）

- **五对张力**：质量与成本（智能路由）、速度与安全（分段/异步审核/信任分级）、自主与受控（分级自主+主动升级人工）、创新与治理（平台化治理，合规下沉为平台级服务）、定制与可维护（优先提示工程与 RAG，必要时才微调）
- **五大设计原则**：①可控自主（护栏+Human-in-the-Loop+权限边界）②全链路可度量（Token 追踪、质量评分、链路追踪）③渐进式授权（**影子模式→灰度（如 5% 流量）→全量**；权限：只读→两周达标得写入→一月稳定得高风险执行）④成本感知（单请求 Token 预算、复杂度路由）⑤合规内建（内容过滤、审计日志、算法备案——备案是"持续性义务"）

### 3.2 AI 架构决策框架（五棵决策树，[decision-framework](https://help.aliyun.com/zh/well-architected/decision-framework-for-ai-architecture)）

1. **模型策略**：API 模型 vs 自托管（PIPL 敏感数据/极致时延/日均调用量阈值）；**提示工程→RAG→微调**渐进路径；模型路由示例（寒暄→Qwen-Flash、普通+RAG→Qwen-Plus、复杂推理→Qwen-Max）
2. **推理架构**：Serverless（波动大、容忍 1-3s 冷启动）/ 专属 GPU（利用率>60%、PAI-EAS）/ 混合；容量规划：日均 <1 万→Serverless，1 万-100 万→找成本临界点，>100 万→专属 GPU，>1000 万→深度优化
3. **AI 数据架构**：纯向量→混合检索（向量+BM25+元数据+Reranker，企业主流）→图增强 RAG；托管知识库（百炼）vs 自建管道（DataWorks）
4. **智能体架构**：单智能体（工具<10）vs 多智能体（主从/流水线/辩论）；工具调用型 vs 工作流驱动型（强合规）vs 自主型（须设终止条件与检查点）
5. **自建、采购与定制**：**PaaS（百炼）为大多数企业推荐起步模式**；TCO 六维度（开发/运维/模型更新/合规/机会/退出成本）；按团队规模：无 AI 团队→百炼低代码；3-10 人→百炼为底座+核心场景 PAI 微调；>10 人→IaaS+PaaS 混合

## 4. 《生成式 AI 卓越架构设计指导原则》（联合信通院）

- 出处：[ebook 8470](https://developer.aliyun.com/ebook/8470)，阿里云+中国信通院，2025-09 上架，约 38 页；2025 云栖大会正式发布。
- 目录：概述 / **安全 / 稳定 / 效率 / 成本 / 性能** / 结束语（⚠️ 该书支柱顺序为"效率在成本前"，与卓越架构官网"安全、稳定、成本、效率、性能"顺序不同）。
- 五支柱 GenAI 专项要点（[官方解读](https://developer.aliyun.com/article/1706331)）：
  - **安全**：数据全生命周期安全；算力与容器安全（多租户隔离、镜像签名、TEE）；**模型供应链安全**（完整性校验、权重加密+哈希/签名、版本追溯）；Responsible AI（去偏、算法备案、《生成式人工智能服务管理暂行办法》合规）
  - **稳定**：弹性调度（多 AZ/地域、异构混部）；模型推理 SLA 与冗余（AI 网关超时重试/Failover/Token 级限流；指标 TTFT、TPS、E2E Latency）；分布式训练容错与**断点续训**（参数/优化器状态/中间结果持久化）
  - **效率**：AI 全生命周期运维闭环；**DevOps+MLOps 一体化**；统一接口与治理（**MCP 协议**整合服务接口、统一鉴权）；自动化合规审计
  - **成本**：GPU 算力成本优化（闲置算力跑容错任务、跨团队共享、上下文缓存）；分层资源管理与计费匹配（稳定任务包周期、实验任务竞价）；可观测工具（GPU 空转识别）；模型复用与量化/蒸馏/剪枝
  - **性能**：高效数据流与存储（近数据计算）；分布式训练优化（梯度压缩、通信合并）；推理优化（KV 缓存、**PD 分离**、动态批处理）；智能调度（算子融合、稀疏激活、专家模型）

## 5. AI Landing Zone（AI LZ）

- 官方定义（[ai-lz-definition](https://help.aliyun.com/zh/caf/ai-lz-definition)）："一种基于云计算最佳实践的标准化、自动化、可治理的企业级 AI 基础设施框架……AI LZ 是在通用 Landing Zone 的基础上补齐 AI 的特有能力，包括安全与合规、AI 成本、训推场景下的可观测等特有能力。"发布：2025-12-19 信通院论坛，白皮书+AI CAF 升级同步。
- **八大模块**：资源规划（账号组织+AI 平台项目空间+资源组/标签规范）、财务管理（AI 资源成本分摊规则）、网络规划（采集→训练→推理全阶段组网）、身份权限（AI 平台权限+**API Key 安全使用规范**）、安全防护（AI 基础设施/模型/应用全方位）、合规审计（满足**等保 3**及行业审计）、运维管理（训推全链路 AI 统一可观测，**借助 MCP 能力实现 AIOps**）、自动化（AI LZ 平台搭建与 MLOps 流水线自动化）。
- **三种 AI 建设范式**：MaaS=百炼（业务用户低门槛）；PaaS=PAI+AI 网关+FC（开发者一站式）；IaaS=ACK+自定义集群（专业团队）。
- 与通用 LZ 的增量（发布会口径）：安全合规治理、AI 成本精细化管理、训推可观测。⚠️ 引用注意：白皮书架构仅以"图三：AI LZ 架构图"呈现，"AI 平台层/Agent 运行时/AI 网关/AI 安全护栏"四层命名**无公开文字出处**（疑为架构图内文），引用时标注"据白皮书架构图，待 PDF 核对"。
- 痛点调研数据（发布会）：仅 14.3% 低成熟度企业采用多可用区架构；77.3% 低成熟度企业数据库允许公网 IP 直接访问；超 60% 企业仍人工创建云资源。
- 案例：全球运动服饰企业（PAI+GPU+通义，云 SSO/操作审计/配置审计）；新势力车企（AI 全栈可观测消除 Agent 黑盒）；消费品巨头 AIOps 运维助手（钉钉机器人为入口）。
- 工程落地：官方开源 **Landing Zone Accelerator（LZA）**（[仓库](https://github.com/aliyun/landing-zone-accelerator-on-alibaba-cloud)、[文档](https://help.aliyun.com/zh/caf/landing-zone-accelerator)）可一次部署统一管理传统云资源与 AI 资源，或独立部署两份（详见 `aliyun-landing-zone-official.md` §14.6）。

## 6. AI CAF 与 AI LZ、AI 卓越架构的关系

- AI CAF 四阶段：**AI 战略 / AI 准备 / AI 应用工程化构建 / AI 治理**（报告页逐字；与经典 CAF 四步走一一对应）。
- **AI LZ = "AI 准备"阶段的落地框架**；AI 治理阶段通过 **AI 卓越架构**（五支柱）落地，评估依托 **AI 云治理中心**（AI 治理成熟度检测 41 项，详见 `aliyun-landing-zone-official.md` §14.10）。
- AI CAF 四大研究亮点：①AI 战略先行（五步法）②AI Landing Zone ③工程化构建（智能体系统架构、核心能力体系、领域适配与数据工程）④AI 治理与运营（五支柱+AI 卓越架构）。

## 7. 产品落点（AI 架构中的官方角色）

| 产品 | 角色 |
|---|---|
| 百炼（Model Studio） | MaaS 范式代表；RAG 端到端管道、提示词管理/A/B、在线评估、知识库、智能体构建 |
| PAI | AI Native 算法工程平台；PAI-EAS 推理+专属资源组、DSW+MLflow、PAIFlow、BladeLLM 加速 |
| 函数计算 FC / AgentRun | Serverless 推理与 Agent 运行时；AgentRun 毫秒级弹性、多语言沙箱、MCP 标准化治理 |
| GPU 云服务器 / 灵骏智算 | 自托管推理与大规模训练算力；灵骏提供大规模 GPU+RDMA |
| OSS / NAS / CPFS | 训练数据/checkpoint 分层存储（高频层 CPFS/极速 NAS，归档层 OSS）；向量库快照目标 |
| **AI 网关** | ⚠️ 名称勘误：官方产品名即"**AI 网关**"（阿里云 API 网关产品线，开源底座 **Higress**）；与 Apache APISIX 无官方归属关系，勿混用 |

## 8. 资料索引

| 材料 | URL |
|---|---|
| AI 卓越架构总览 | https://help.aliyun.com/zh/well-architected/excellent-architecture-in-the-ai-era |
| AI 五支柱（安全/稳定/成本/效率/性能） | https://help.aliyun.com/zh/well-architected/safety-pillar 等同目录 |
| AI 原生转型 / 决策框架 | https://help.aliyun.com/zh/well-architected/ai-native-transformation / decision-framework-for-ai-architecture |
| 生成式 AI 卓越架构设计指导原则 | https://developer.aliyun.com/ebook/8470 （解读 https://developer.aliyun.com/article/1706331 ） |
| AI CAF 官方报告 | https://www.aliyun.com/reports/2025-ai-caf |
| AI LZ 定义 | https://help.aliyun.com/zh/caf/ai-lz-definition |
| LZA 开源仓库 | https://github.com/aliyun/landing-zone-accelerator-on-alibaba-cloud |
| AI 治理检测项（41 项） | https://help.aliyun.com/zh/cgc/user-guide/ai-governance-supported-check-items |
