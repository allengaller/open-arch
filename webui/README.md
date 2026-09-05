# Web UI（OpenArch 控制台）

React 19 + TypeScript + Vite 实现的产品控制台，由后端 `openarch web`（FastAPI / AgentScope Agent Service）静态托管于 `/`。

## 视图

- **控制台**（三区布局）：左栏会话列表、中间聊天主区（流式回复 + Mermaid 架构图渲染）、右栏交付物面板（Markdown 预览 / draw.io 下载）
- **知识库**：浏览仓库 `skills/` 技能包的 Markdown 知识正文，数据来自后端只读端点 `/openarch/skills`（列表）与 `/openarch/skills/{pack}/{path}`（正文，白名单后缀 + 路径穿越防护）
- **演示模式**：后端不可用（如 CDN 静态托管）时自动降级为 `DemoConsole`，展示内置演示会话；知识库入口保留，提示需本地运行 `openarch web`

## 开发

    npm install
    npm run dev        # http://localhost:5173，API 按前缀代理到 127.0.0.1:8000

代理前缀见 `vite.config.ts` 的 `API_PREFIXES`（`/openarch`、`/sessions`、`/chat` 等），新增后端路由若换前缀需同步。

## 构建与测试

    npm run build      # tsc -b + vite build，并把 ../GTM/index.html 复制进 dist/gtm（CDN 托管用）
    npm test           # vitest（lib 纯函数单测）
    npm run lint       # oxlint

## 结构

    src/
    ├── App.tsx            # 启动引导（config/agent/credential）+ 顶栏「控制台/知识库」视图切换
    ├── DemoConsole.tsx    # 无后端降级界面（演示数据）
    ├── KnowledgePane.tsx  # 知识库视图（技能包导航 + Markdown 渲染）
    ├── ChatPane.tsx       # 聊天主区（SSE 流式、工具调用确认、错误重试）
    ├── SessionSidebar.tsx # 会话列表
    ├── DeliverablesPane.tsx # 交付物树 + 预览
    ├── MarkdownView.tsx   # Markdown + Mermaid 渲染（DOMPurify 消毒）
    ├── styles.css         # 设计令牌与布局（对应仓库根 DESIGN.md）
    └── lib/               # api 客户端、SSE、demo 数据、mermaid、tree、knowledge（纯函数，均有单测）
