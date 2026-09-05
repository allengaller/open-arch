---
name: cloud-sa-playbook
description: 云 SA 全工作领域 playbook：获客与线索分配、铁三角协同、需求澄清与方案设计、POC、招投标、迁移上云、存量经营与续费、竞争替换、AI 场景、行业合规、赋能布道与能力成长，以及客户分型与处境、技术场景打法、自身资源边界、内部协同流程，用于 SA 打单、经营策略与售前协同
---

# 云 SA 获客与打单 Playbook（全工作领域）

SA 的核心姿势是"用技术换信任，用方案换订单"。工作领域覆盖一条完整生命周期：**售前拿单 → 售中上云 → 售后经营**，外加四条横向放大线（竞争 / AI / 行业合规 / 赋能与自身成长），以及三个放大维度——**客户侧**（分型与处境）、**场景侧**（技术场景商机）、**自身与内部侧**（资源边界与协同流程）。

    售前：获客 → 需求澄清 → 方案设计 → POC → 招投标 → 讲标签约
    售中：Landing Zone → 迁移上云（6R / 波次 / 割接）
    售后：架构巡检 → FinOps → QBR → 续费保卫 → Upsell
    横向：竞争对标 · AI 场景 · 行业合规 · 出海全球化 · 赋能布道 · 能力成长
    三维：客户分型与处境 · 技术场景商机 · 自身资源与边界 · 内部协同与流程

按当前任务选择知识文档：

| 阶段 | 场景 / 问题 | 用哪份 |
|---|---|---|
| 售前 | 客户从哪来：获客四类渠道、线索路由链路、商机优先级与挑单 | `content/acquisition-channels.md` |
| 售前 | 铁三角分工、五段打单时间线、协同冲突机制 | `content/iron-triangle.md` |
| 售前 | 需求澄清框架、方案文档结构、TCO/ROI 测算、汇报讲标 | `content/requirement-and-solution.md` |
| 售前 | POC 要不要做、立项设计、执行纪律、结果转化 | `content/poc-playbook.md` |
| 售前 | 招投标：标书解读、技术标编写、澄清答疑、讲标答辩 | `content/bidding-support.md` |
| 售中 | 迁移上云：评估、6R 分流、波次规划、割接与回滚 | `content/migration-playbook.md` |
| 售后 | 存量经营：巡检、客户健康分、QBR、续费保卫、Upsell 挖掘 | `content/account-deepening.md` |
| 横向 | 竞争对标、友商客户替换、存量客户防御 | `content/competitive-strategy.md` |
| 横向 | AI/大模型场景：商机分层、方案模式、算力与选型 | `content/ai-solutions.md` |
| 横向 | 赋能伙伴与客户、内容布道、影响力运营 | `content/enablement-influence.md` |
| 横向 | 行业纵深、等保/信创/数据合规 | `content/industry-compliance.md` |
| 横向 | 出海与全球化：数据出境与属地合规、全球架构模式、属地交付 | `content/global-expansion.md` |
| 横向 | SA 能力模型、成长路径、多单并行与效率方法 | `content/capability-model.md` |
| 客户 | 客户分型：互联网/央国企/金融/制造/游戏/初创/外企的识别信号、决策链与打法 | `content/customer-segments.md` |
| 客户 | 十五种非标处境应对：友商存量、预算砍半、决策人更换、内定竞品、事故修复… | `content/customer-situations.md` |
| 场景 | 技术场景商机：大促弹性、数据平台、信创替换、直播、IoT、SaaS 托管、等保整改 | `content/scenario-playbooks.md` |
| 自身 | 自身资源与边界：资源地图、让步换承诺、SA 不承诺清单、留痕自我保护 | `content/self-playbook.md` |
| 内部 | 内部协同与流程：商机纪律、报价审批、POC 立项、交付合同、汇报升级 | `content/internal-process.md` |

工作方式：

1. **先定位阶段，再看维度**：用路线图判断商机处于哪一段选对应文档；同时用三维校准打法——这是哪类客户（customer-segments）、处在什么处境（customer-situations）、什么场景进来的（scenario-playbooks）。相邻阶段的时间线与话术（如铁三角 → 需求 → POC → 招投标）是连续的，按序引用。
2. **跨包协同**：顶层框架深度知识用 `cloud-frameworks` 技能（CAF / Landing Zone / WAF）；交付执行流程用 `sa-playbooks` 技能（上云评估 / 成本优化）；架构评审打分工具用 `aliyun-waf` 技能的 checklist.yaml。本包讲"怎么打"，那三包讲"用什么打"，配套使用。
3. **作战清单**：进入商机启动 / POC / 投标交稿 / 迁移割接 / 续费 90 天五大环节前，用本包 `checklist.yaml` 逐项核对（每项给 done/na 与 evidence），fail 项升级处理后再推进。
4. **引用而非复述**：回答客户/团队问题或写打法文档时，直接引用 content 文档中的表格、框架与话术，不要凭记忆复述；涉及具体产品参数时以官方文档为准。
5. **产出物统一交付**：获客计划、商机作战卡、方案建议书、POC 报告、巡检报告、QBR 材料、竞争对标表，统一用 `export_deliverable` 打包交付。

注：云厂商内部具体分配与考核规则（系统、评分项）不对外公开且随团队/时期变化，本包是公开资料（SA 岗位 JD、阿里云合作伙伴门户权益）+ 云行业通行做法的合成，结构性准确，细节需结合实际校准；涉及招投标法规与行业合规的场景，以最新法规和属地监管要求为准。
