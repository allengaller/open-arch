# OpenArch

**把售前全栈架构师（Solutions Architect）的工作显性化**的开源工具箱，基于 [AgentScope](https://github.com/agentscope-ai/agentscope) 构建。

岗位里散落在个人经验中的工作，被写成可审计的技能资产与可执行工作流：新手跟练入职，在岗 SA 梳理标准，资深 SA 沉淀传承。第一张已交付的工作单是**架构设计 Copilot**：

需求澄清 → 方案生成 → Mermaid / draw.io 架构图 → 阿里云 Well-Architected 评审 → Markdown 交付文档

## 📣 项目主页（GTM 营销页）

OpenArch 的对外门面 —— 完整介绍产品定位、三类用户、售前生命周期、第一张工作单的端到端示例、终端实录、路线图与上手命令。

- 本地打开：直接用浏览器打开仓库内的 [`GTM/index.html`](./GTM/index.html)（无依赖，纯静态）
- GitHub Pages（启用 Pages 后）：<https://allengaller.github.io/open-arch/GTM/>
- 设计语言：纸白 + 墨黑 + 朱砂红三色，连续规则线表单拓扑；详见 [DESIGN.md](./DESIGN.md)

> 两条不同的浏览器面：这里的 **GTM 营销页** 是静态定位 deck；下方的 **Web UI** 是 `uv run openarch web` 起的运行时产品控制台。

## 特性

- **架构设计 Copilot（工作单 01）**：结构化需求卡驱动，缺失信息主动追问，产出可编辑的交付物
- **SA 技能库**：`skills/` 下的 SKILL.md 技能包（方法论、架构师概念库、CAF/Landing Zone/WAF 顶层框架、WAF 清单、交付与获客 playbook、协同换位视角、策略制定），由 AgentScope 原生 Skill 机制加载，欢迎贡献
- **全家桶**：AgentScope `Agent` + `Toolkit` + `launch_console`，无数据库、一条命令启动

## 快速开始

    git clone https://github.com/allengaller/open-arch.git && cd open-arch
    uv sync
    cp .env.example .env        # 填入 DASHSCOPE_API_KEY
    uv run openarch

> 若未配置 Key，启动时会打印一行「配置错误：…」提示并以退出码 1 退出——这是预期的启动自检行为，不是 bug。按提示填写 `.env` 后重试即可。

Docker：

    cp .env.example .env
    docker compose run openarch

## Web UI（浏览器）

> 这一节是产品 *运行时* 浏览器界面（Agent 控制台 + 交付物面板），与上方的 **GTM 营销页** 不是同一回事。

    uv run openarch web        # 默认 http://127.0.0.1:8000
    # 或
    uv run openarch web --host 0.0.0.0 --port 9000

首次启动会自动完成初始化（幂等种子）：写入 SQLite（`OPENARCH_DB`）、
注册 OpenArch agent 与模型凭证（密钥只进服务端存储，不回传前端）。

浏览器打开 `http://127.0.0.1:8000`：

- 顶栏：「控制台 / 知识库」视图切换；知识库浏览 `skills/` 全部知识正文（`/openarch/skills` 只读端点）
- 左栏：会话列表 + 新建会话
- 中间：聊天主区，实时流式回复，Mermaid 架构图自动渲染
- 右栏：交付物面板，Markdown 在线预览、draw.io 文件下载

页面间互通：webui 顶栏提供「返回项目主页 → `/gtm/`」（服务端同源挂载仓库 `GTM/` 目录）；[`GTM/index.html`](./GTM/index.html) 的顶栏与 Hero 提供「进入 Web 控制台」回到控制台地址。

前端开发模式：

    cd webui && npm install && npm run dev   # http://localhost:5173，代理 API 到 8000

## 配置

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `DASHSCOPE_API_KEY` | 是* | — | DashScope 凭证（*用 `OPENARCH_BASE_URL` 时可换） |
| `OPENARCH_MODEL` | 否 | `qwen-max` | 模型名 |
| `OPENARCH_BASE_URL` | 否 | — | OpenAI 兼容端点（设置后走该端点而非 DashScope） |
| `OPENARCH_API_KEY` | 条件 | — | OpenAI 兼容端点的凭证（设置了 `OPENARCH_BASE_URL` 时必填） |
| `OPENARCH_WORKSPACE` | 否 | `./deliverables` | 交付物输出目录 |
| `OPENARCH_SKILLS_DIR` | 否 | 仓库根 `skills/` | 技能目录覆盖 |
| `OPENARCH_DB` | 否 | `./data/openarch.db` | Web 模式 SQLite 路径（工作区在其同级 `workspaces/`） |
| `OPENARCH_HOST` | 否 | `127.0.0.1` | Web 监听地址 |
| `OPENARCH_PORT` | 否 | `8000` | Web 监听端口 |

> **Docker 用户注意**：使用 Docker 时请保持 `OPENARCH_DB`、`OPENARCH_WORKSPACE` 未设置（不要在 `.env` 中取消这两行的注释）。镜像内已默认 `OPENARCH_DB=/data/openarch.db`、`OPENARCH_WORKSPACE=/data/deliverables` 并挂载到宿主机 `./data`；若在 `.env` 中显式设置会覆盖镜像默认值，导致 SQLite 与交付物写入容器内错误路径。

## 技能包结构

    skills/<name>/
    ├── SKILL.md      # frontmatter（name/description）+ 工作说明
    ├── content/      # 知识正文
    └── checklist.yaml  # 可选，机读清单（如 aliyun-waf）

新增技能 = 新增一个目录，无需改代码。

## 开发

    uv run pytest -m "not e2e"   # 单元测试
    uv run pytest -m e2e          # 端到端（需真实 Key）
    cd webui && npm test          # 前端单元测试

## 路线图

售前其余工作环节（客户洞察 / PoC 验证 / 投标支持 / 交付复盘）→ 学习路径与技能树 → Web UI 产品化（多用户与账号体系）→ 客户管理与交付沉淀 → Runtime 服务化与多云知识包扩充（AWS / Azure）

## License

Apache-2.0
