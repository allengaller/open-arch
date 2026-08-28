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
| MVP 能力切片 | **架构设计 Copilot** | 其余能力（SOP 执行引擎、客户管理、学习路径）进路线图 |
| 方案立场 | **阿里云优先** | 技能内容以阿里云产品体系与 Well-Architected Framework 为基底 |
| 知识承载 | Markdown 文件 | 能力用 Python 工具类承载，知识内容保持 Markdown 以便阅读与社区贡献（运行时仍 100% AgentScope） |
| MVP 期 UI | AgentScope Studio | 已确认 Studio 是开发向工具（localhost:3000，含聊天界面与 OpenTelemetry 追踪）；产品级专属 UI 进路线图 |

## 3. 总体架构

```
┌────────────────────────────────────────────┐
│        AgentScope Studio（as_studio）       │
│    聊天界面 + OpenTelemetry 追踪 + 评估      │
│    开发向工具，非产品级终端 UI（见路线图）     │
└─────────────┬──────────────────────────────┘
              │  agentscope.init(studio_url=...)
┌─────────────┴──────────────────────────────┐
│         OpenArch Agent 服务（Python）        │
│      agentscope.ReActAgent + Toolkit        │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ 技能加载器 │ │ 架构图工具 │ │ WAF 评审  │ │
│  └───────────┘ └───────────┘ └───────────┘ │
└─────────────┬──────────────────────────────┘
              │  OpenAI 兼容接口
┌─────────────┴──────────────────────────────┐
│        DashScope（Qwen 系列，可换端点）       │
└────────────────────────────────────────────┘
```

组件边界：

- **Studio**：仅作 UI 与观测，不含业务逻辑；通过 `agentscope.init(project="openarch", studio_url=...)` 接入
- **Agent 服务**：`agentscope.ReActAgent` 装配 + 全部业务工具；无独立数据库，会话内存由 AgentScope Memory 承担
- **模型层**：DashScope OpenAI 兼容接口，默认 Qwen 旗舰模型，可通过环境变量换任意 OpenAI 兼容端点

## 4. 仓库结构

```
open-arch/
├── src/openarch/
│   ├── main.py              # 入口：openarch up（起 Studio + Agent）
│   ├── agent.py             # ReActAgent 装配、系统提示词
│   ├── skills_loader.py     # 技能发现/加载/检索
│   └── tools/               # Toolkit 工具（Python 类）
│       ├── skill_tools.py   # list_skills / load_skill / search_skills
│       ├── diagram_tools.py # generate_diagram / export_drawio
│       ├── waf_tools.py     # review_with_waf
│       ├── requirements_tools.py  # structure_requirements
│       └── deliverable_tools.py   # export_deliverable
├── skills/                  # SA 知识资产（Markdown）
│   ├── arch-design/         # 架构设计方法论 SOP
│   ├── aliyun-waf/          # Well-Architected 五支柱检查清单
│   └── sa-playbooks/        # 交付 playbook 与模板
├── tests/
│   ├── unit/                # 工具与技能包格式测试
│   └── e2e/                 # 端到端冒烟（需 API Key）
├── deliverables/            # 运行时输出（gitignore）
├── docker-compose.yml       # agent + studio 两服务
├── pyproject.toml           # uv/pip 安装，console script: openarch
└── README.md
```

## 5. 核心工作流（架构设计 Copilot 主链路）

```
需求澄清 → 方案生成 → 架构图输出 → WAF 评审 → 交付物打包
```

1. **需求澄清**：`structure_requirements` 把对话提炼成结构化需求卡：业务场景、规模/并发、可用性目标、预算区间、合规约束、现有系统。必填项缺失时 Agent 主动追问
2. **方案生成**：Agent 按需 `load_skill("arch-design")` 注入方法论（场景模式识别 → 参考架构选型 → 组件选型），产出方案文档
3. **架构图输出**：`generate_diagram` 产出 Mermaid 代码并做语法校验；`export_drawio` 生成可编辑的 .drawio 文件
4. **WAF 评审**：`review_with_waf` 按阿里云 Well-Architected 五支柱（可靠性、安全性、成本优化、性能效率、运维）清单逐项检查，输出评分表、高风险项、改进建议
5. **交付物打包**：`export_deliverable` 把需求卡 + 方案 + 架构图 + 评审结果组装为一份 Markdown 交付文档，写入 `./deliverables/`

## 6. 技能资产规范

每个技能包是一个目录：

```
skills/<skill-name>/
├── SKILL.md        # 必需：frontmatter（name、description、version）+ 使用说明
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

全部工具注册进 `agentscope.tool.Toolkit`，输入输出为结构化 JSON/文件路径，异常以结构化错误返回给 Agent：

| 工具 | 输入 | 输出 |
|---|---|---|
| `list_skills` | — | 技能包清单（名称、描述、版本） |
| `load_skill` | skill_name | 技能正文（注入对话） |
| `search_skills` | query | 相关技能段落 |
| `structure_requirements` | 对话上下文摘要 | 需求卡 JSON（含缺失项列表） |
| `generate_diagram` | 架构描述 | Mermaid 代码 + 校验结果 |
| `export_drawio` | Mermaid 代码 | .drawio 文件路径 |
| `review_with_waf` | 方案文档 | 五支柱评分表 + 风险清单 JSON |
| `export_deliverable` | 会话产物引用 | Markdown 交付文档路径 |

## 8. 配置与部署

环境变量（无数据库，无用户系统）：

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `DASHSCOPE_API_KEY` | 是 | — | 模型访问凭证 |
| `OPENARCH_MODEL` | 否 | Qwen 旗舰模型 | 任意 OpenAI 兼容模型名 |
| `OPENARCH_BASE_URL` | 否 | DashScope 兼容端点 | 换第三方端点用 |
| `OPENARCH_WORKSPACE` | 否 | `./deliverables` | 交付物输出目录 |

启动方式：

```bash
# 本地
uv sync
cp .env.example .env    # 填 DASHSCOPE_API_KEY
openarch up             # 起 Studio(localhost:3000) + Agent 服务

# Docker
cp .env.example .env
docker compose up
```

`openarch up` 负责按序拉起两个进程：`as_studio` 与 Agent 服务（后者依赖前者地址），并在控制台输出访问入口。

## 9. 错误处理

只在系统边界处理，不做防御性兜底：

- **API Key 缺失/无效**：启动即失败，错误信息指明缺失变量与配置位置（README 锚点）
- **Mermaid 校验失败**：`generate_diagram` 返回校验错误，Agent 自动修正重试，上限 2 次，仍失败则将代码块原文交给用户
- **工具异常**：捕获后返回结构化错误（`{"error": ...}`）给 Agent 继续对话，不中断会话

## 10. 测试策略

- **单元测试**（pytest，CI 必跑，无需 API Key）：Mermaid 校验器、Mermaid→drawio 转换、需求卡 schema、WAF 评分逻辑、技能包格式 lint（frontmatter 完整性、必需目录）
- **端到端冒烟**（`pytest -m e2e`，需真实 Key，本地执行）：输入"给一个日均 10 万订单的电商设计架构"，断言产出需求卡、方案、Mermaid、WAF 评分、交付文档五件套
- **Agent 行为质量**：通过 Studio tracing 人工抽查；MVP 不建自动化行为回归

## 11. MVP 后路线图

1. 产品级专属 Web UI（聊天 + 图渲染 + 交付物管理），前端对接 Agent 服务，架构演化吸收方案 C 形态
2. 客户管理模块（客户档案、交付记录沉淀）
3. 学习路径/技能树（SA 能力评估与成长）
4. AgentScope Runtime 容器化部署
5. 多云知识包（AWS/Azure 选型知识）

## 12. 范围外（Non-Goals）

- 多用户/多租户、用户系统、鉴权
- 自建数据库与持久化（会话内存由 AgentScope Memory 承担，交付物落盘文件）
- SOP 执行引擎、客户管理、学习路径的任何实现
- 非 OpenAI 兼容的模型接入层
