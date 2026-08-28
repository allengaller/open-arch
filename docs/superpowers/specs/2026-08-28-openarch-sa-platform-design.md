# OpenArch — Solutions Architect 开箱即用工具箱与职业提升平台 · MVP 设计

日期：2026-08-28
状态：已与需求方逐节确认

## 1. 背景与定位

OpenArch 是一个面向 Solutions Architect（SA）的开源项目：以 SA 最佳实践为核心资产，提供开箱即用的架构设计 Copilot。它同时服务三种使用场景：

1. **开源项目**：任何 SA（不限于阿里云内部）clone 即用
2. **日常工作**：架构设计、方案输出、交付物生产的效率工具
3. **职业成长**：技能包内含方法论与 SOP，后续扩展学习路径（非 MVP）

## 2. 已确认的关键决策

| 决策点 | 结论 | 备注 |
|---|---|---|
| 目标用户 | 开源社区 SA + 个人效率 + 职业成长 | 不绑定阿里云内部场景 |
| 实现方案 | **B：AgentScope 全家桶** | 运行时 100% AgentScope；否决了 A（Skills-first 外壳）与 C（中台式平台） |
| AgentScope 版本 | **2.0** | 2026-08 现状为 2.0（`Agent`/`Toolkit`/`launch_console` API，与 1.x 不兼容；原 Studio 已被 Console/Agent Service 取代） |
| MVP 能力切片 | **架构设计 Copilot** | 其余能力（SOP 执行引擎、客户管理、学习路径）进路线图 |
| 方案立场 | **阿里云优先** | 技能内容以阿里云产品体系与 Well-Architected Framework 为基底 |
| 知识承载 | Markdown 技能目录（SKILL.md） | 经 `Toolkit(skills_or_loaders=["skills"])` 原生接入，框架自动注册 Skill viewer 供 Agent 按需读取；能力工具用 Python 类（`ToolBase` 子类）实现 |
| MVP 期 UI | **`launch_console` 终端聊天** | 2.0 官方路径（流式输出、工具调用确认、Ctrl+C 中断），零额外基础设施；产品级浏览器 UI 进路线图 |

## 3. 总体架构

```
┌────────────────────────────────────────────┐
│      launch_console 终端聊天（MVP UI）       │
│   流式输出 + 工具调用确认 + Ctrl+C 中断      │
└─────────────┬──────────────────────────────┘
              │  asyncio.run(launch_console(agent))
┌─────────────┴──────────────────────────────┐
│         OpenArch Agent 服务（Python）        │
│      agentscope.agent.Agent + Toolkit       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │skills/技能│ │ 架构图工具 │ │ WAF 评审  │ │
│  │(原生接入) │ │(校验/drawio│ │(清单评分) │ │
│  └───────────┘ └───────────┘ └───────────┘ │
└─────────────┬──────────────────────────────┘
              │  DashScopeChatModel / OpenAI 兼容
┌─────────────┴──────────────────────────────┐
│        DashScope（Qwen 系列，可换端点）       │
└────────────────────────────────────────────┘
```

组件边界：

- **Console**：`agentscope.console.launch_console`，仅作 UI，不含业务逻辑；`openarch` 命令一条命令进入对话
- **Agent 服务**：`agentscope.agent.Agent`（内置 ReAct 循环）+ `Toolkit`（业务工具 + `skills_or_loaders` 原生技能接入）；无数据库，会话内存由框架承担
- **模型层**：默认 `DashScopeChatModel`（`DashScopeCredential`），可切换任意 OpenAI 兼容端点（`OpenAIChatModel`）

## 4. 仓库结构

```
open-arch/
├── src/openarch/
│   ├── main.py              # 入口：openarch（装配 Agent + launch_console）
│   ├── agent.py             # Agent 装配（系统提示词、Toolkit、模型）
│   ├── config.py            # 环境变量读取与校验
│   └── tools/               # 能力工具（ToolBase 子类）
│       ├── mermaid.py       # Mermaid flowchart 解析/校验（纯逻辑）
│       ├── drawio.py        # Mermaid → draw.io XML（纯逻辑）
│       ├── diagram_tools.py # validate_diagram / export_drawio
│       ├── waf_tools.py     # review_with_waf（清单校验 + 评分）
│       ├── requirements_tools.py  # structure_requirements（需求卡 schema）
│       └── deliverable_tools.py   # export_deliverable
├── skills/                  # SA 知识资产（SKILL.md，AgentScope 原生格式）
│   ├── arch-design/         # 架构设计方法论 SOP
│   ├── aliyun-waf/          # Well-Architected 五支柱检查清单
│   └── sa-playbooks/        # 交付 playbook 与模板
├── tests/
│   ├── unit/                # 工具与技能包格式测试
│   └── e2e/                 # 端到端冒烟（需 API Key）
├── deliverables/            # 运行时输出（gitignore）
├── docker-compose.yml
├── pyproject.toml           # uv/pip 安装，Python ≥3.11，console script: openarch
└── README.md
```

## 5. 核心工作流（架构设计 Copilot 主链路）

```
需求澄清 → 方案生成 → 架构图输出 → WAF 评审 → 交付物打包
```

1. **需求澄清**：`structure_requirements` 把对话提炼成结构化需求卡：业务场景、规模/并发、可用性目标、预算区间、合规约束、现有系统。必填项缺失时 Agent 主动追问
2. **方案生成**：Agent 通过内建 Skill viewer 读取 `arch-design` 技能，按其方法论（场景模式识别 → 参考架构选型 → 组件选型）产出方案文档
3. **架构图输出**：Agent 生成 Mermaid 代码，`validate_diagram` 做语法校验（失败则 Agent 修正重试）；`export_drawio` 生成可编辑的 .drawio 文件
4. **WAF 评审**：`review_with_waf` 接收 Agent 对 `aliyun-waf` 清单的逐项评估，校验覆盖完整性并计算五支柱评分表、高风险项清单
5. **交付物打包**：`export_deliverable` 把需求卡 + 方案 + 架构图 + 评审结果组装为一份 Markdown 交付文档，写入 `./deliverables/`

## 6. 技能资产规范

每个技能包是一个目录：

```
skills/<skill-name>/
├── SKILL.md        # 必需：frontmatter（name、description；version 等扩展字段可选）+ 使用说明
├── content/        # 知识正文（Markdown，可多文件）
└── templates/      # 可选：交付物模板
```

MVP 三个技能包：

| 技能包 | 内容 | 来源原则 |
|---|---|---|
| `arch-design` | 需求分析框架、常见场景模式（Web 应用/数据平台/AI 推理服务等）、选型决策树 | 自研方法论 + 公开最佳实践 |
| `aliyun-waf` | 五支柱检查清单与问卷条目（结构化，供 `review_with_waf` 机读） | 基于阿里云公开 WAF 文档整理 |
| `sa-playbooks` | 上云评估、迁移、成本优化等交付 SOP 与模板 | 通用 SA 交付实践 |

约束：技能内容面向开源社区，不得包含阿里云内部资料或客户敏感信息；`aliyun-waf` 仅收录公开文档可溯源的内容。

## 7. 工具规范

全部能力工具实现为 `agentscope.tool.ToolBase` 子类（`check_permissions` 一律返回 ALLOW），注册进 `Toolkit(tools=[...])`；技能发现/读取由框架原生 Skill 机制承担，不自建。工具输入输出为结构化 JSON/文件路径，异常以结构化错误返回给 Agent：

| 工具 | 输入 | 输出 |
|---|---|---|
| `structure_requirements` | 从对话提炼的需求字段 | 需求卡 JSON（含缺失必填项列表） |
| `validate_diagram` | Mermaid 代码 | 校验结果（通过 / 错误列表） |
| `export_drawio` | Mermaid 代码 + 标题 | .drawio 文件路径 |
| `review_with_waf` | 方案摘要 + 逐项评估结果 | 五支柱评分表 + 风险清单 JSON |
| `export_deliverable` | 需求卡、方案、Mermaid、评审结果 | Markdown 交付文档路径 |

## 8. 配置与部署

环境变量（无数据库，无用户系统）：

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `DASHSCOPE_API_KEY` | 是 | — | 模型访问凭证（未设 `OPENARCH_BASE_URL` 时必填） |
| `OPENARCH_MODEL` | 否 | `qwen-max` | 模型名（DashScope 或 OpenAI 兼容均可） |
| `OPENARCH_BASE_URL` | 否 | — | 设置后改用 OpenAI 兼容端点（`OpenAIChatModel`），需配合 `OPENARCH_API_KEY` |
| `OPENARCH_API_KEY` | 否 | — | OpenAI 兼容端点的凭证 |
| `OPENARCH_WORKSPACE` | 否 | `./deliverables` | 交付物输出目录 |
| `OPENARCH_SKILLS_DIR` | 否 | 仓库根 `skills/` | 技能目录覆盖项 |

启动方式：

```bash
# 本地
uv sync
cp .env.example .env    # 填 DASHSCOPE_API_KEY
openarch                # 进入终端对话（流式输出、工具确认）

# Docker（交互式终端）
cp .env.example .env
docker compose run openarch
```

`openarch` 命令负责：读取并校验环境变量 → 加载技能与工具 → `asyncio.run(launch_console(agent))`。

## 9. 错误处理

只在系统边界处理，不做防御性兜底：

- **API Key 缺失/无效**：启动即失败，错误信息指明缺失变量与配置位置（README 锚点）
- **Mermaid 校验失败**：`validate_diagram` 返回错误列表，Agent 自动修正重试，上限 2 次，仍失败则将代码块原文交给用户
- **工具异常**：捕获后返回结构化错误（`{"error": ...}`）给 Agent 继续对话，不中断会话

## 10. 测试策略

- **单元测试**（pytest，CI 必跑，无需 API Key）：Mermaid 校验器、Mermaid→drawio 转换、需求卡 schema、WAF 评分逻辑、技能包格式 lint（frontmatter 完整性、必需目录）
- **端到端冒烟**（`pytest -m e2e`，需真实 Key，本地执行）：输入"给一个日均 10 万订单的电商设计架构"，断言产出需求卡、方案、Mermaid、WAF 评分、交付文档五件套
- **Agent 行为质量**：Console 会话人工抽查 + Studio 追踪（如可用）；MVP 不建自动化行为回归

## 11. MVP 后路线图

1. 产品级浏览器 Web UI（基于 AgentScope Agent Service + 官方 Web UI 扩展：聊天 + 图渲染 + 交付物管理）
2. 客户管理模块（客户档案、交付记录沉淀）
3. 学习路径/技能树（SA 能力评估与成长）
4. AgentScope Runtime 容器化部署
5. 多云知识包（AWS/Azure 选型知识）

## 12. 范围外（Non-Goals）

- 多用户/多租户、用户系统、鉴权
- 自建数据库与持久化（会话内存由 AgentScope Memory 承担，交付物落盘文件）
- SOP 执行引擎、客户管理、学习路径的任何实现
- 非 OpenAI 兼容的模型接入层
