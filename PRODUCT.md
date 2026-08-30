# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

纯静态 HTML/CSS/JS（用户确认）：零构建、零依赖，GTM 单页放 `GTM/` 目录，可部署到任意静态托管。仓库其余部分为纯 Python（AgentScope 2.0）后端，无前端基建。

## Users

主要用户：开源社区的 Solutions Architect（SA）——负责架构设计与方案交付的技术角色，日常在终端、云控制台与文档之间工作，需要把业务需求快速变成可交付的架构方案与文档。次要受众：技术招聘方/面试官，把本仓库作为候选人的工程能力与方法论证据来评估（GTM 页需双受众兼顾：主体面向社区上手，证据区同时服务面试场景）。

## Product Purpose

OpenArch 是面向 SA 的开源工具箱与职业提升平台：以 SA 最佳实践为核心资产（技能包），提供开箱即用的架构设计 Copilot。MVP 主链路：需求澄清 → 方案生成 → 架构图输出（Mermaid 校验 / drawio 导出）→ 阿里云 WAF 评审 → 交付物打包。运行时 100% AgentScope 2.0（ReActAgent + Toolkit + launch_console），知识以 Markdown 技能包承载，阿里云优先（Well-Architected Framework 为基底），模型可切换任意 OpenAI 兼容端点。

## Positioning

「SA 最佳实践作为可执行的技能资产」：把架构设计方法论（SOP、WAF 五支柱清单、交付 playbook）做成 Agent 按需读取的技能包，配合结构化工具（需求卡 schema、图校验、评分表），每单产出五件套交付物而非聊天记录。通用 AI 助手与云厂商控制台 Copilot 无法照搬：知识可审计、可替换、可版本化，链路全开源、本地可跑、模型可换。

## Operating Context

- 使用场景：SA 日常架构设计与交付物生产；开源社区评估与二次开发；求职作品集展示。
- 入口：`openarch` 命令进入终端聊天（AgentScope launch_console：流式输出、工具调用确认、Ctrl+C 中断）；Docker 交互式运行。
- 配置：`DASHSCOPE_API_KEY`（或 `OPENARCH_BASE_URL` 指向 OpenAI 兼容端点）；交付物落盘 `./deliverables/`。

## Capabilities and Constraints

- MVP 能力：架构设计 Copilot 五步链路；三个技能包（arch-design / aliyun-waf / sa-playbooks）；五个结构化工具（structure_requirements、validate_diagram、export_drawio、review_with_waf、export_deliverable）。
- 技术约束：Python ≥ 3.11；AgentScope 2.0（`Agent`/`Toolkit`/`launch_console` API）；无数据库、无用户系统；MVP UI 为终端聊天。
- 路线图（页面叙事不得当作现有能力）：产品级浏览器 Web UI、客户管理、学习路径/技能树、Runtime 容器化部署、多云知识包（AWS/Azure）。
- Non-Goals：多租户/鉴权、自建持久化、SOP 执行引擎、客户管理、学习路径。

## Brand Commitments

- 名称：OpenArch（仓库 open-arch）。
- 方案立场：阿里云优先；技能内容仅收录公开文档可溯源的内容，不含阿里云内部资料或客户敏感信息。
- 开源姿态：面向开源社区，clone 即用；能力边界说清楚，路线图不冒充现状。

## Evidence on Hand

- 已批准的 MVP 设计规格：`docs/superpowers/specs/2026-08-28-openarch-sa-platform-design.md`（与需求方逐节确认）。
- 实施进行中：`src/openarch/`（环境配置、Mermaid flowchart 校验器等）、`tests/`（git log 可见进度）；实施计划见 `docs/superpowers/plans/2026-08-28-openarch-mvp.md`。
- 无：用户数据、star 数、客户案例、第三方测评、价格、团队背书。页面不得虚构上述证据；示例对话/交付物可自制，但须明确标注为演示。

## Product Principles

1. 资产优先：方法论文档是产品本体，Agent 是执行器。
2. 开箱即用：clone → 配一个 Key → 一条命令进入工作流。
3. 结构化交付：每步产出可校验的工件（需求卡/校验通过的图/五支柱评分表/交付文档），不是聊天记录。
4. 可审计可替换：知识、模型、端点全部可插拔。
