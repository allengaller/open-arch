# OpenArch

**面向 Solutions Architect 的开箱即用工具箱与架构设计 Copilot**，基于 [AgentScope](https://github.com/agentscope-ai/agentscope) 构建。

输入业务需求，OpenArch 会走完 SA 的标准交付链路：

需求澄清 → 方案生成 → Mermaid / draw.io 架构图 → 阿里云 Well-Architected 评审 → Markdown 交付文档

## 特性

- **架构设计 Copilot**：结构化需求卡驱动，缺失信息主动追问，产出可编辑的交付物
- **SA 技能库**：`skills/` 下的 SKILL.md 技能包（方法论、WAF 清单、交付 playbook），由 AgentScope 原生 Skill 机制加载，欢迎贡献
- **全家桶**：AgentScope `Agent` + `Toolkit` + `launch_console`，无数据库、一条命令启动

## 快速开始

    git clone https://github.com/<you>/open-arch.git && cd open-arch
    uv sync
    cp .env.example .env        # 填入 DASHSCOPE_API_KEY
    uv run openarch

> 若未配置 Key，启动时会打印一行「配置错误：…」提示并以退出码 1 退出——这是预期的启动自检行为，不是 bug。按提示填写 `.env` 后重试即可。

Docker：

    cp .env.example .env
    docker compose run openarch

## 配置

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `DASHSCOPE_API_KEY` | 是* | — | DashScope 凭证（*用 `OPENARCH_BASE_URL` 时可换） |
| `OPENARCH_MODEL` | 否 | `qwen-max` | 模型名 |
| `OPENARCH_BASE_URL` | 否 | — | OpenAI 兼容端点（需配 `OPENARCH_API_KEY`） |
| `OPENARCH_WORKSPACE` | 否 | `./deliverables` | 交付物输出目录 |
| `OPENARCH_SKILLS_DIR` | 否 | 仓库根 `skills/` | 技能目录覆盖 |

> **Docker 用户注意**：使用 Docker 时请保持 `OPENARCH_WORKSPACE` 未设置（不要在 `.env` 中取消该行注释）。镜像内已默认 `OPENARCH_WORKSPACE=/data/deliverables` 并挂载到宿主机 `./deliverables`；若在 `.env` 中显式设置会覆盖镜像默认值，导致交付物写入容器内错误路径。

## 技能包结构

    skills/<name>/
    ├── SKILL.md      # frontmatter（name/description）+ 工作说明
    ├── content/      # 知识正文
    └── checklist.yaml  # 可选，机读清单（如 aliyun-waf）

新增技能 = 新增一个目录，无需改代码。

## 开发

    uv run pytest -m "not e2e"   # 单元测试
    uv run pytest -m e2e          # 端到端（需真实 Key）

## 路线图

浏览器 Web UI（Agent Service）→ 客户管理 → SA 学习路径/技能树 → 多云知识包

## License

Apache-2.0
