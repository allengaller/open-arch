# OpenArch Design System

## Visual Direction

**Enterprise Console / 企业交付控制台**：OpenArch 的界面像一套企业级架构交付工具 —— 冷纸白底、深墨蓝字、企业蓝强调，克制圆角与细分隔线。信息组织是「控制台 / 解决方案文档」而不是表单审批：顶栏品牌 + 分区导航，Hero 左侧需求陈述、右侧结构化能力面板，板块用细分隔线归纳。

拒绝两个类别默认：评审表式的纸白+朱砂红签批表单（旧方向，已废弃）；暗底霓虹 AI 页。不要回归红色主导，不要把控制台退化成卡片阵。

## Color Tokens

```css
--paper: #f7f8fa;          /* 冷纸白 ground */
--paper-2: #eef1f6;        /* 二级面板/表头 */
--ink: #0f1728;            /* 深墨蓝，正文/标题 */
--ink-70: rgba(15,23,40,.7);   /* 次级正文 */
--ink-55: rgba(15,23,40,.55);  /* 弱说明 */
--ink-40: rgba(15,23,40,.40);  /* 占位/禁用 */
--line: rgba(15,23,40,.12);    /* hairline 分隔 */
--line-strong: rgba(15,23,40,.28); /* 强规则线 */
--accent: #1f4fd8;         /* 企业蓝，主 CTA/焦点/链接 */
--accent-deep: #173db5;    /* hover 加深 */
--accent-soft: #e8edff;    /* 选中/激活底 */
--success: #15803d;
--warning: #b45309;
--danger: #b91c1c;         /* 错误/中断/风险/破坏性（朱砂红语义化收窄） */
--term-bg: #0f1728;        /* 终端/代码暗场（受控唯一暗场） */
--term-bg-2: #16213a;
--term-text: #e8ecf4;
--term-dim: #9aa5b8;
--term-tool-text: #c9d1e0;
--term-ok: #7fd0a0;
--term-warn: #e3b15c;
--term-confirm: #f0937c;
--term-file: #9fc3e8;
--term-dot: rgba(255,255,255,.22);
```

企业蓝只用于主 CTA、焦点环、链接、选中态、运行状态；危险红只用于错误、中断、破坏性操作。终端实录是受控的暗场（唯一）。不得添加渐变、发光、玻璃拟态或蓝紫霓虹。

## Typography

- CJK / UI / Display：`Noto Sans SC`，400 / 500 / 700 / 900。
- Code / Data / Document IDs：`JetBrains Mono`，400 / 500 / 700，启用 tabular numerals。
- H1（营销页 hero）：900，`clamp(40px, 5.5vw, 76px)`，紧行高 1.05。
- Section heading：900，`clamp(26px, 3vw, 44px)`。
- 正文：14–16px，最大约 44em；UI 控件 13–14px。
- 等宽字体只用于命令、编号、测量、状态和数据。

## Layout Grammar

- 页面最大内容宽度 1400px，桌面横向 padding 64px，移动 20px。
- 底色冷纸白；板块之间用 hairline 分隔线（非 2px 墨线），关键区块可用 `--paper-2` 底。
- 重复对象用「规则行 + hover 底色」或「轻卡片」（克制圆角 6px），不堆叠多层卡片。
- 章节与菜单不加装饰性编号 eyebrow；只在内容本身有序时保留序号（工作流 01–05、命令 01–03）。

## Components

### Brand Topbar

两页面共用：左=字标「OpenArch」+ 可选分区导航；右=动作链接（GTM 的「进入 Web 控制台」；webui 的「返回项目主页 → /gtm/」）+ 主按钮。粘性、冷纸白底、底部 hairline。

### Capability Panel（营销页 Hero 右侧）

结构化能力摘要面板（不是评分卡）：三行能力（如 需求澄清 / 架构评审 / 交付打包），每行名称 + 一句说明 + mono 编号；`--paper-2` 底、hairline 分隔、无分数、无红章。

### Buttons

- 主按钮：`--accent` 实底、白字、圆角 6px、无阴影；hover `--accent-deep`。
- 次按钮：白底 1px `--line-strong` 边框；hover 背景 `--paper-2`。
- 危险按钮：仅 `--danger`（中断、删除、清空），不要用于主 CTA。
- 全部有 `:focus-visible` 2px `--accent` 外环（不透明、不渐显）。

### Session / Deliverables（webui）

- 侧栏：冷纸白、右侧 hairline；会话项 hover `--paper-2`，active `--accent-soft` + 左侧 3px `--accent` 条。
- 聊天消息：白底圆角 6px hairline；用户消息 `--accent-soft` 底 + `--accent` 边框。
- 交付物树：文件行 hover `--paper-2`；预览覆盖层白底。
- 状态：运行中绿点 `--success`；流式中 1px 虚线边框；错误条 `--danger` 底 / 白字。

### Terminal Field

全页唯一暗场 `--term-bg`：`--term-text` 正文，工具/确认/警告/文件用低饱和语义色（`--term-tool-text` / `--term-ok` / `--term-warn` / `--term-confirm` / `--term-file`）。必须标注「演示会话」，不得把演示当真实客户证据。

## Iconography

内联 SVG，统一 1.75–2.4 stroke，`round` linecap / linejoin，单色 `--ink`（可换 `--accent` / `--danger` 语境）。禁止 Unicode/emoji 代替产品图标。

## Motion

- 主动效：签到式——能力面板行入场（fade+6px，指数 ease-out 0.5s）；webui 消息渐入 ≤200ms。
- 终端行：按序淡入 + 6px 位移。
- 其余默认静止；不得逐节同款入场、弹跳 easing 或背景粒子。
- `prefers-reduced-motion: reduce` 全部直出终态。

## Responsive Rules

- 960px：营销 hero 单列；导航收窄（隐藏分区链接）；webui 交付物面板折叠/覆盖。
- 600px：命令断行；表格/面板子项 `min-width:0`。
- 移动端横向溢出是阻断问题；新增等宽字符串必须验证 390px 视口。

## Accessibility

- 可见 `:focus-visible`：2px `--accent` 外环，不透明、不渐显。
- 正文对冷纸白 ≥4.5:1；大字 ≥3:1。
- 保留跳到主要内容、语义 section/nav、按钮可访问名称。
- 动效遵循 `prefers-reduced-motion`。
- selection/scrollbar/underline offset 使用本系统色值。

## Content Rules

- 中文为主；AgentScope、WAF、Mermaid、draw.io、工具名保留英文。
- 叙事框架：产品是把售前全栈架构师工作显性化的系统；第一张已交付工作单是架构设计；三类用户（新手入职/在岗标准化/资深传承）都有明确去处。
- 当前能力与路线图必须分区，路线图不能写成现有能力。
- 评分、终端会话等演示数据必须标注。
- 不得虚构客户、stars、性能基准、第三方背书或价格。

## Cross-page Navigation

- GTM 营销页提供「进入 Web 控制台」→ 运行时地址（默认 `http://127.0.0.1:8000`，生产部署替换为实际 URL）。
- webui 顶栏提供「返回项目主页」→ `/gtm/`（同源静态挂载，Python `app.mount("/gtm", StaticFiles(directory=GTM_DIR))`）。
- README 同步说明两个入口。