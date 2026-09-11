# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

后端为纯 Python（AgentScope 2.0）。两条浏览器面：GTM 营销页为零构建单页 HTML/CSS/JS（`GTM/` 目录，任意静态托管可部署）；产品控制台为 React 19 + TypeScript + Vite（`webui/` 目录，`openarch web` 静态托管于 `/`，演示模式无后端自动降级）。

## Users

三类 SA（Solutions Architect，售前全栈架构师）按职业阶段分层：
1. 新手/转行者：没有真实项目经验，需要岗位地图、SOP 与可跑通的示例项目，目标是能入职。
2. 在岗 SA：有大量隐性经验，需要把个人交付习惯梳理成可版本化、可复用的标准流程。
3. 资深 SA：方法论成熟，需要把最佳实践沉淀为可执行、可传承的技能资产。
次要受众：技术招聘方/面试官，把本仓库作为候选人的工程能力与方法论证据来评估（GTM 页双受众兼顾：主体面向三类 SA，证据区同时服务面试场景）。

## Product Purpose

OpenArch 是面向 SA 的开源工具箱与职业提升平台，核心命题是**把售前全栈架构师的工作显性化**：把散落在个人经验里的岗位工作（需求澄清、方案设计、评审、交付、复盘）固化为公开可审计的技能资产与可执行工作流。三类用户各取所需：新手沿地图跑通一遍即可入门入职，在岗 SA 把工作梳理成标准流程，资深 SA 沉淀最佳实践用于传承。首个落地工作单：架构设计 Copilot（需求澄清 → 方案生成 → 架构图输出 → WAF 评审 → 交付物打包）。运行时 100% AgentScope 2.0（ReActAgent + Toolkit + launch_console），知识以 Markdown 技能包承载，阿里云优先（Well-Architected Framework 为基底），模型可切换任意 OpenAI 兼容端点。

## Positioning

「SA 工作显性化系统」：岗位全景按售前生命周期展开（客户洞察 → 需求澄清 → 方案设计 → 评审 → PoC/投标 → 交付 → 复盘），每一段工作对应一个技能包 + 结构化工具 + 可校验工件。当前第一张工作单「架构设计」已闭环，其余环节在路线图。通用 AI 助手与云厂商控制台 Copilot 无法照搬：知识可审计、可替换、可版本化，链路全开源、本地可跑、模型可换；对新手它是入职训练场，对老 SA 它是工作标准化器。

## Operating Context

- 使用场景：新手跟练岗位工作流并产出入职证据；在岗 SA 梳理并标准化自己的交付流程；资深 SA 沉淀/维护技能包；开源社区评估与二次开发；求职作品集展示。
- 入口：`openarch` 命令进入终端聊天（AgentScope launch_console：流式输出、工具调用确认、Ctrl+C 中断）；`openarch web` 启动浏览器控制台（会话 + 交付物 + 知识库视图，`/openarch/skills` 只读端点）；Docker 交互式运行。
- 配置：`DASHSCOPE_API_KEY`（或 `OPENARCH_BASE_URL` 指向 OpenAI 兼容端点）；交付物落盘 `./deliverables/`。

## Capabilities and Constraints

- MVP 能力：第一张工作单「架构设计」五步链路；八个技能包（arch-design / aliyun-waf / sa-playbooks / cloud-frameworks / sa-concepts / cloud-sa-playbook / sa-perspectives / sa-strategy）；五个结构化工具（structure_requirements、validate_diagram、export_drawio、review_with_waf、export_deliverable）；Web 控制台三区布局 + 知识库视图（技能包 Markdown 正文浏览）。
- 技术约束：Python ≥ 3.11；AgentScope 2.0（`Agent`/`Toolkit`/`launch_console` API）；Web 模式使用 SQLite（启动幂等种子，无用户系统）；终端聊天与浏览器控制台双入口。
- 路线图（页面叙事不得当作现有能力）：售前其余工作单闭环（客户洞察 / PoC 验证 / 投标支持 / 交付复盘——获客打法知识已在 cloud-sa-playbook）、学习路径与技能树、Web UI 产品化（多用户与账号体系）、客户管理与交付沉淀、Runtime 容器化多用户部署、多云知识包扩充（AWS/Azure 选型）。
- Non-Goals：多租户/鉴权、自建持久化、SOP 执行引擎（路线图之外不做承诺）。

## Brand Commitments

- 名称：OpenArch（仓库 open-arch）。
- 方案立场：阿里云优先；技能内容仅收录公开文档可溯源的内容，不含阿里云内部资料或客户敏感信息。
- 开源姿态：面向开源社区，clone 即用；能力边界说清楚，路线图不冒充现状。

## Evidence on Hand

- 已批准的 MVP 设计规格：`docs/superpowers/specs/2026-08-28-openarch-sa-platform-design.md`（与需求方逐节确认）。
- 实施进行中：`src/openarch/`（环境配置、Mermaid flowchart 校验器等）、`tests/`（git log 可见进度）；实施计划见 `docs/superpowers/plans/2026-08-28-openarch-mvp.md`。
- 无：用户数据、star 数、客户案例、第三方测评、价格、团队背书。页面不得虚构上述证据；示例对话/交付物可自制，但须明确标注为演示。

## Product Principles

1. 显性化优先：工作先被写成可审计的资产（技能包、模板、清单），才被 Agent 执行；隐性经验不进产品。
2. 开箱即用：clone → 配一个 Key → 一条命令进入工作流。
3. 结构化交付：每步产出可校验的工件（需求卡/校验通过的图/五支柱评分表/交付文档），不是聊天记录。
4. 可审计可替换：知识、模型、端点全部可插拔；新手能读懂，老 SA 能改写。
