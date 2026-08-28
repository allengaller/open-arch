# OpenArch MVP 实施计划（AgentScope 2.0 全家桶 + 架构设计 Copilot）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建开源项目 OpenArch MVP：SA 用 `openarch` 一条命令进入终端对话，完成"需求澄清 → 方案生成 → Mermaid/drawio 架构图 → WAF 评审 → 交付物打包"全链路。

**Architecture:** AgentScope 2.0 `Agent`（内置 ReAct 循环）+ `Toolkit`（5 个 `ToolBase` 能力工具 + `skills_or_loaders` 原生技能接入）+ DashScope 模型；UI 为 `launch_console` 终端聊天；无数据库。

**Tech Stack:** Python ≥3.11、agentscope 2.0、pydantic、PyYAML、pytest/pytest-asyncio、uv、Docker（可选）、GitHub Actions。

**规格来源:** `docs/superpowers/specs/2026-08-28-openarch-sa-platform-design.md`（已获批，已同步 2.0）

**API 参考来源**（实现时如遇签名不符，以官方文档为准，调整调用方式但保持测试断言不变）:
- Agent/Toolkit: https://docs.agentscope.io/latest/en/building-blocks/tool/overview
- 自定义工具: https://docs.agentscope.io/latest/en/building-blocks/tool/python-tool
- 技能: https://docs.agentscope.io/latest/en/building-blocks/tool/skill

---

## 任务依赖

```
Task1 脚手架 → Task2 配置 → Task3 mermaid → Task4 drawio → Task5 图工具
                                    ↘ Task6 需求卡 ↘ Task7 WAF ↘ Task8 交付物
Task9 技能内容（依赖 Task1）→ Task10 Agent+入口（依赖 5/6/7/8/9）
→ Task11 Docker+CI → Task12 e2e+README
```

---

### Task 1: 项目脚手架

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/openarch/__init__.py`
- Create: `src/openarch/tools/__init__.py`
- Create: `tests/unit/__init__.py`（空目录占位用 `.gitkeep`，不需要 `__init__.py`）

- [ ] **Step 1: 写 `pyproject.toml`**

```toml
[project]
name = "openarch"
version = "0.1.0"
description = "Out-of-the-box toolbox and copilot platform for Solutions Architects, powered by AgentScope."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "Apache-2.0" }
dependencies = [
    "agentscope>=2.0",
    "pydantic>=2.7",
    "pyyaml>=6.0",
]

[project.scripts]
openarch = "openarch.main:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/openarch"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
markers = [
    "e2e: end-to-end tests requiring a real API key",
]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: 写 `.gitignore`**

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
deliverables/
.pytest_cache/
.ruff_cache/
dist/
uv.lock
```

- [ ] **Step 3: 写 `.env.example`**

```bash
# 必填：DashScope API Key（https://bailian.console.aliyun.com/ 获取）
DASHSCOPE_API_KEY=

# 可选：模型名（默认 qwen-max）
# OPENARCH_MODEL=qwen-max

# 可选：改用任意 OpenAI 兼容端点（设置后走 OpenAIChatModel）
# OPENARCH_BASE_URL=
# OPENARCH_API_KEY=

# 可选：交付物输出目录（默认 ./deliverables）
# OPENARCH_WORKSPACE=./deliverables

# 可选：技能目录覆盖（默认仓库根 skills/）
# OPENARCH_SKILLS_DIR=
```

- [ ] **Step 4: 创建包骨架**

```bash
mkdir -p src/openarch/tools tests/unit tests/e2e skills/arch-design skills/aliyun-waf skills/sa-playbooks deliverables
touch src/openarch/__init__.py src/openarch/tools/__init__.py tests/unit/.gitkeep tests/e2e/.gitkeep
echo "# Runtime outputs" > deliverables/.gitkeep
```

`src/openarch/__init__.py` 内容：

```python
__version__ = "0.1.0"
```

- [ ] **Step 5: 安装依赖并验证 agentscope 2.x**

```bash
uv sync
uv run python -c "import agentscope; print(agentscope.__version__)"
```

Expected: 输出 `2.x.x`。若 PyPI 上没有 ≥2.0 的版本，改用源码安装：

```bash
uv add "agentscope @ git+https://github.com/agentscope-ai/agentscope"
```

- [ ] **Step 6: 提交**

```bash
git add pyproject.toml .gitignore .env.example src/ tests/ skills/ deliverables/ uv.lock
git commit -m "chore: 项目脚手架（uv + agentscope 2.0 + pytest 配置）"
```

---

### Task 2: 配置模块

**Files:**
- Create: `src/openarch/config.py`
- Test: `tests/unit/test_config.py`

- [ ] **Step 1: 写失败测试**

```python
import pytest

from openarch.config import ConfigError, load_settings


def test_defaults_with_dashscope_key():
    s = load_settings(env={"DASHSCOPE_API_KEY": "sk-test"})
    assert s.model == "qwen-max"
    assert s.base_url is None
    assert s.workspace.name == "deliverables"
    assert s.dashscope_api_key == "sk-test"


def test_missing_key_raises_with_guidance():
    with pytest.raises(ConfigError) as exc:
        load_settings(env={})
    assert "DASHSCOPE_API_KEY" in str(exc.value)
    assert "README" in str(exc.value)


def test_base_url_switches_to_openai_compatible():
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": "sk-test",
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": "sk-local",
            "OPENARCH_MODEL": "my-model",
        }
    )
    assert s.base_url == "http://localhost:8000/v1"
    assert s.openai_api_key == "sk-local"
    assert s.model == "my-model"


def test_base_url_without_api_key_raises():
    with pytest.raises(ConfigError) as exc:
        load_settings(
            env={
                "DASHSCOPE_API_KEY": "sk-test",
                "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            }
        )
    assert "OPENARCH_API_KEY" in str(exc.value)


def test_workspace_and_skills_dir_overrides(tmp_path):
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": "sk-test",
            "OPENARCH_WORKSPACE": str(tmp_path / "out"),
            "OPENARCH_SKILLS_DIR": str(tmp_path / "skills"),
        }
    )
    assert s.workspace == tmp_path / "out"
    assert s.skills_dir == tmp_path / "skills"
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'openarch.config'`

- [ ] **Step 3: 实现 `src/openarch/config.py`**

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MODEL = "qwen-max"


class ConfigError(RuntimeError):
    """环境变量配置错误（启动即失败，错误信息直接可操作）。"""


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str | None
    openai_api_key: str | None
    base_url: str | None
    model: str
    workspace: Path
    skills_dir: Path


def load_settings(env: dict[str, str] | None = None) -> Settings:
    e = dict(os.environ) if env is None else env

    base_url = e.get("OPENARCH_BASE_URL") or None
    dashscope_key = e.get("DASHSCOPE_API_KEY") or None
    openai_key = e.get("OPENARCH_API_KEY") or None

    if base_url and not openai_key:
        raise ConfigError(
            "设置了 OPENARCH_BASE_URL 但缺少 OPENARCH_API_KEY。"
            "请在 .env 中填写 OPENARCH_API_KEY（见 README「配置」一节）。"
        )
    if not base_url and not dashscope_key:
        raise ConfigError(
            "缺少 DASHSCOPE_API_KEY。请执行 `cp .env.example .env` 并填写"
            " DASHSCOPE_API_KEY（见 README「配置」一节）。"
        )

    workspace = Path(e.get("OPENARCH_WORKSPACE") or "./deliverables").resolve()
    default_skills = Path(__file__).resolve().parents[2] / "skills"
    skills_dir = Path(e.get("OPENARCH_SKILLS_DIR") or default_skills).resolve()

    return Settings(
        dashscope_api_key=dashscope_key,
        openai_api_key=openai_key,
        base_url=base_url,
        model=e.get("OPENARCH_MODEL") or _DEFAULT_MODEL,
        workspace=workspace,
        skills_dir=skills_dir,
    )
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: 5 passed

- [ ] **Step 5: 提交**

```bash
git add src/openarch/config.py tests/unit/test_config.py
git commit -m "feat: 环境配置模块（缺失 Key 启动即报错并给出指引）"
```

---

### Task 3: Mermaid flowchart 解析与校验（纯逻辑）

**Files:**
- Create: `src/openarch/tools/mermaid.py`
- Test: `tests/unit/test_mermaid.py`

- [ ] **Step 1: 写失败测试**

```python
from openarch.tools.mermaid import validate_mermaid

VALID = """flowchart TD
  web[Web 前端] --> slb[SLB]
  slb --> api{判断}
  api -->|是| db[(数据库)]
  api --> cache(缓存)
"""

def test_valid_diagram_passes():
    r = validate_mermaid(VALID)
    assert r.ok, r.errors

def test_missing_flowchart_header():
    r = validate_mermaid("  web[前端] --> slb[SLB]")
    assert not r.ok
    assert any("flowchart" in e for e in r.errors)

def test_invalid_direction():
    r = validate_mermaid("flowchart XX\n  a --> b")
    assert not r.ok
    assert any("方向" in e for e in r.errors)

def test_node_label_with_bracket_char_is_error():
    r = validate_mermaid("flowchart TD\n  a[x]y] --> b")
    assert not r.ok

def test_empty_diagram_is_error():
    r = validate_mermaid("flowchart TD")
    assert not r.ok
    assert any("节点" in e for e in r.errors)

def test_edge_creates_implicit_node():
    from openarch.tools.mermaid import parse_flowchart
    fc = parse_flowchart("flowchart LR\n  a --> b")
    assert fc.nodes["b"].text == ""
    assert fc.edges[0].src == "a" and fc.edges[0].dst == "b"
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_mermaid.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 `src/openarch/tools/mermaid.py`**

```python
from __future__ import annotations

import re
from dataclasses import dataclass, field

_DIRECTIONS = {"TD", "TB", "LR", "RL", "BT"}

_NODE_RE = re.compile(
    r"^\s*(?P<id>\w+)\s*(?P<shape>\[\((?P<db>[^\]]*)\)\]|\[(?P<rect>[^\]]*)\]"
    r"|\((?P<round>[^)]*)\)|\{(?P<diamond>[^}]*)\})?\s*$"
)
_EDGE_RE = re.compile(
    r"^\s*(?P<src>\w+)\s*(?P<arrow>-{2,3}>|---)\s*(?:\|(?P<label>[^|]*)\|\s*)?"
    r"(?P<dst>\w+)\s*$"
)


@dataclass
class Node:
    id: str
    shape: str  # rect | round | diamond | db | point
    text: str


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""
    directed: bool = True


@dataclass
class Flowchart:
    direction: str = "TD"
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def _node_from_match(m: re.Match) -> Node:
    g = m.groupdict()
    if g["db"] is not None:
        return Node(g["id"], "db", g["db"].strip())
    if g["rect"] is not None:
        return Node(g["id"], "rect", g["rect"].strip())
    if g["round"] is not None:
        return Node(g["id"], "round", g["round"].strip())
    if g["diamond"] is not None:
        return Node(g["id"], "diamond", g["diamond"].strip())
    return Node(g["id"], "point", "")


def parse_flowchart(text: str) -> Flowchart:
    """解析（假设已通过 validate）。边缘引用的未知 id 按隐式节点处理。"""
    fc = Flowchart()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        header = re.match(r"^flowchart\s+(\S+)\s*$", line)
        if header:
            fc.direction = header.group(1)
            continue
        e = _EDGE_RE.match(line)
        if e:
            fc.edges.append(
                Edge(
                    src=e.group("src"),
                    dst=e.group("dst"),
                    label=(e.group("label") or "").strip(),
                    directed=e.group("arrow").endswith(">"),
                )
            )
            for nid in (e.group("src"), e.group("dst")):
                fc.nodes.setdefault(nid, Node(nid, "point", ""))
            continue
        n = _NODE_RE.match(line)
        if n:
            node = _node_from_match(n)
            fc.nodes[node.id] = node
    return fc


def validate_mermaid(text: str) -> ValidationResult:
    errors: list[str] = []
    lines = text.splitlines()
    header_idx = next(
        (i for i, l in enumerate(lines) if l.strip().startswith("flowchart")), None
    )
    if header_idx is None:
        errors.append("第 1 行附近：缺少 `flowchart <方向>` 头，例如 `flowchart TD`")
        direction = None
    else:
        m = re.match(r"^flowchart\s+(\S+)\s*$", lines[header_idx].strip())
        if not m or m.group(1) not in _DIRECTIONS:
            errors.append(
                f"第 {header_idx + 1} 行：`flowchart` 方向必须是 {'/'.join(sorted(_DIRECTIONS))}"
            )
        direction = m.group(1) if m else None

    saw_node_or_edge = False
    for i, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("%%") or i - 1 == header_idx:
            continue
        if _EDGE_RE.match(line) or _NODE_RE.match(line):
            saw_node_or_edge = True
            continue
        errors.append(f"第 {i} 行：无法识别的语法 `{line}`")
    if not saw_node_or_edge:
        errors.append("图中没有任何节点或连线（`a[标签] --> b[标签]`）")
    return ValidationResult(ok=not errors, errors=errors)
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_mermaid.py -v`
Expected: 6 passed

- [ ] **Step 5: 提交**

```bash
git add src/openarch/tools/mermaid.py tests/unit/test_mermaid.py
git commit -m "feat: Mermaid flowchart 解析与校验器"
```

---

### Task 4: Mermaid → draw.io XML 转换（纯逻辑）

**Files:**
- Create: `src/openarch/tools/drawio.py`
- Test: `tests/unit/test_drawio.py`

- [ ] **Step 1: 写失败测试**

```python
from openarch.tools.drawio import flowchart_to_drawio
from openarch.tools.mermaid import parse_flowchart

MERMAID = "flowchart TD\n  web[Web 前端] --> slb[SLB]\n  slb --> db[(数据库)]\n"

def test_xml_contains_vertices_and_edges():
    xml = flowchart_to_drawio(parse_flowchart(MERMAID), title="电商架构")
    assert "<mxGraphModel" in xml and "</mxGraphModel>" in xml
    assert xml.count('vertex="1"') == 3
    assert xml.count('edge="1"') == 2

def test_labels_and_title_escaped():
    xml = flowchart_to_drawio(
        parse_flowchart("flowchart TD\n  a[A&B] --> b"), title="T<1>"
    )
    assert "A&amp;B" in xml
    assert "T&lt;1&gt;" in xml

def test_edge_labels_present():
    xml = flowchart_to_drawio(
        parse_flowchart("flowchart TD\n  a -->|主库| b"), title="t"
    )
    assert "主库" in xml
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_drawio.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 `src/openarch/tools/drawio.py`**

```python
from __future__ import annotations

import html
from xml.sax.saxutils import escape

from openarch.tools.mermaid import Flowchart, Node

_W, _H, _DX, _DY = 160, 48, 240, 110

_SHAPE_STYLE = {
    "rect": "rounded=1;whiteSpace=wrap;html=1;",
    "round": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;",
    "diamond": "rhombus;whiteSpace=wrap;html=1;",
    "db": "shape=cylinder3;whiteSpace=wrap;html=1;",
    "point": "ellipse;whiteSpace=wrap;html=1;",
}


def _escape(text: str) -> str:
    return escape(html.unescape(text))


def _layout(fc: Flowchart) -> tuple[dict[str, tuple[int, int]], list[list[str]]]:
    """按拓扑层级网格布局：返回 id→(x, y) 与分层列表。"""
    children: dict[str, list[str]] = {nid: [] for nid in fc.nodes}
    indegree = {nid: 0 for nid in fc.nodes}
    for e in fc.edges:
        if e.dst not in children[e.src]:
            children[e.src].append(e.dst)
            indegree[e.dst] += 1
    level = {nid: 0 for nid in fc.nodes if indegree[nid] == 0}
    frontier = list(level)
    while frontier:
        nxt = []
        for nid in frontier:
            for c in children[nid]:
                level[c] = max(level.get(c, 0), level[nid] + 1)
                nxt.append(c)
        frontier = [n for n in nxt if n in level]
    rows: list[list[str]] = []
    for nid, lv in sorted(level.items(), key=lambda kv: (kv[1], kv[0])):
        while len(rows) <= lv:
            rows.append([])
        rows[lv].append(nid)
    pos: dict[str, tuple[int, int]] = {}
    for r, row in enumerate(rows):
        for c, nid in enumerate(row):
            pos[nid] = (c * _DX, r * _DY)
    return pos, rows


def flowchart_to_drawio(fc: Flowchart, title: str) -> str:
    pos, rows = _layout(fc)
    cells: list[str] = []
    for node in fc.nodes.values():
        x, y = pos[node.id]
        label = _escape(node.text or node.id)
        cells.append(
            f'<mxCell id="{_escape(node.id)}" value="{label}" '
            f'style="{_SHAPE_STYLE[node.shape]}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{_W}" height="{_H}" as="geometry"/>'
            f"</mxCell>"
        )
    for i, e in enumerate(fc.edges, start=1):
        style = "edgeStyle=orthogonalEdgeStyle;html=1;"
        if not e.directed:
            style += "endArrow=none;"
        value = f' value="{_escape(e.label)}"' if e.label else ""
        cells.append(
            f'<mxCell id="e{i}"{value} style="{style}" edge="1" parent="1" '
            f'source="{_escape(e.src)}" target="{_escape(e.dst)}">'
            f"<mxGeometry relative=\"1\" as=\"geometry\"/></mxCell>"
        )
    body = "\n      ".join(cells)
    return (
        '<mxfile host="openarch">\n'
        f'  <diagram id="openarch" name="{_escape(title)}">\n'
        "    <mxGraphModel dx=\"800\" dy=\"600\" grid=\"1\" gridSize=\"10\" "
        "page=\"1\" pageWidth=\"1169\" pageHeight=\"826\" math=\"0\" shadow=\"0\">\n"
        "      <root>\n"
        '        <mxCell id="0"/>\n'
        '        <mxCell id="1" parent="0"/>\n'
        f"        {body}\n"
        "      </root>\n"
        "    </mxGraphModel>\n"
        "  </diagram>\n"
        "</mxfile>\n"
    )
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_drawio.py -v`
Expected: 3 passed

- [ ] **Step 5: 提交**

```bash
git add src/openarch/tools/drawio.py tests/unit/test_drawio.py
git commit -m "feat: Mermaid 到 draw.io XML 转换（分层布局 + XML 转义）"
```

---

### Task 5: 架构图工具（ToolBase 子类）

**Files:**
- Create: `src/openarch/tools/diagram_tools.py`
- Create: `src/openarch/tools/base.py`（公共 ALLOW 权限基类）
- Test: `tests/unit/test_diagram_tools.py`

- [ ] **Step 1: 写公共基类 `src/openarch/tools/base.py`**

```python
from agentscope.permission import (
    PermissionContext,
    PermissionDecision,
    PermissionBehavior,
)
from agentscope.tool import ToolBase


class OpenArchTool(ToolBase):
    """OpenArch 能力工具基类：权限一律 ALLOW（MVP 本地单用户场景）。"""

    async def check_permissions(
        self, tool_input: dict, context: PermissionContext
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW, message="OpenArch local tool"
        )
```

- [ ] **Step 2: 写失败测试 `tests/unit/test_diagram_tools.py`**

```python
import json

from openarch.tools.diagram_tools import ExportDrawioTool, ValidateDiagramTool

VALID = "flowchart TD\n  web[Web 前端] --> slb[SLB]\n"
INVALID = "web -->\n"


async def test_validate_ok():
    tool = ValidateDiagramTool()
    out = json.loads((await tool(mermaid_code=VALID)).content[0].text)
    assert out["ok"] is True and out["errors"] == []


async def test_validate_errors():
    tool = ValidateDiagramTool()
    out = json.loads((await tool(mermaid_code=INVALID)).content[0].text)
    assert out["ok"] is False and out["errors"]


async def test_export_drawio_writes_file(tmp_path):
    tool = ExportDrawioTool(workspace=tmp_path)
    out = json.loads(
        (await tool(mermaid_code=VALID, title="电商架构")).content[0].text
    )
    path = tmp_path / "diagrams" / out["file"]
    assert path.exists()
    assert "<mxGraphModel" in path.read_text(encoding="utf-8")
```

- [ ] **Step 3: 运行确认失败**

Run: `uv run pytest tests/unit/test_diagram_tools.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: 实现 `src/openarch/tools/diagram_tools.py`**

```python
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from agentscope.message import TextBlock
from agentscope.tool import ToolChunk

from openarch.tools.base import OpenArchTool
from openarch.tools.drawio import flowchart_to_drawio
from openarch.tools.mermaid import parse_flowchart, validate_mermaid


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip()).strip("-")
    return (slug or "diagram")[:40]


class ValidateDiagramTool(OpenArchTool):
    name = "validate_diagram"
    description = (
        "校验 Mermaid flowchart 代码语法。返回 {ok, errors}。"
        "生成架构图后必须先调用本工具，校验通过才能展示或导出。"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "mermaid_code": {
                "type": "string",
                "description": "以 `flowchart TD` 开头的完整 Mermaid 代码",
            }
        },
        "required": ["mermaid_code"],
    }
    is_concurrency_safe = True
    is_read_only = True

    async def call(self, mermaid_code: str) -> ToolChunk:
        r = validate_mermaid(mermaid_code)
        return ToolChunk(
            content=[TextBlock(text=json.dumps({"ok": r.ok, "errors": r.errors}, ensure_ascii=False))]
        )


class ExportDrawioTool(OpenArchTool):
    name = "export_drawio"
    description = (
        "将已通过 validate_diagram 校验的 Mermaid flowchart 转为可编辑的 "
        "draw.io 文件，返回文件路径。"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "mermaid_code": {"type": "string", "description": "完整的 Mermaid 代码"},
            "title": {"type": "string", "description": "图标题，用作文件名"},
        },
        "required": ["mermaid_code", "title"],
    }
    is_concurrency_safe = True
    is_read_only = False

    def __init__(self, workspace: Path):
        self._workspace = workspace

    async def call(self, mermaid_code: str, title: str) -> ToolChunk:
        r = validate_mermaid(mermaid_code)
        if not r.ok:
            return ToolChunk(
                content=[TextBlock(text=json.dumps({"error": r.errors}, ensure_ascii=False))]
            )
        out_dir = self._workspace / "diagrams"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = out_dir / f"{ts}-{_slugify(title)}.drawio"
        path.write_text(
            flowchart_to_drawio(parse_flowchart(mermaid_code), title),
            encoding="utf-8",
        )
        return ToolChunk(content=[TextBlock(text=json.dumps({"file": path.name}, ensure_ascii=False))])
```

- [ ] **Step 5: 运行确认通过**

Run: `uv run pytest tests/unit/test_diagram_tools.py -v`
Expected: 3 passed

- [ ] **Step 6: 提交**

```bash
git add src/openarch/tools/base.py src/openarch/tools/diagram_tools.py tests/unit/test_diagram_tools.py
git commit -m "feat: validate_diagram 与 export_drawio 工具"
```

---

### Task 6: 需求结构化工具

**Files:**
- Create: `src/openarch/tools/requirements_tools.py`
- Test: `tests/unit/test_requirements_tools.py`

- [ ] **Step 1: 写失败测试**

```python
import json

from openarch.tools.requirements_tools import StructureRequirementsTool

OPTIONAL = ["scale", "availability_target", "budget_range", "compliance", "existing_systems"]


async def test_full_card_has_no_missing():
    tool = StructureRequirementsTool()
    out = json.loads(
        (
            await tool(
                business_scenario="电商网站",
                scale="日均 10 万订单",
                availability_target="99.95%",
                budget_range="月 2 万元以内",
                compliance="需支持等保三级",
                existing_systems="单体 PHP 应用",
            )
        ).content[0].text
    )
    assert out["card"]["business_scenario"] == "电商网站"
    assert out["missing_fields"] == []


async def test_partial_card_lists_missing():
    tool = StructureRequirementsTool()
    out = json.loads((await tool(business_scenario="数据平台")).content[0].text)
    assert out["missing_fields"] == OPTIONAL
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_requirements_tools.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 `src/openarch/tools/requirements_tools.py`**

```python
from __future__ import annotations

import json

from agentscope.message import TextBlock
from agentscope.tool import ToolChunk
from pydantic import BaseModel, Field

from openarch.tools.base import OpenArchTool


class RequirementsCard(BaseModel):
    business_scenario: str = Field(description="业务场景（必填）")
    scale: str | None = Field(default=None, description="规模/并发/数据量")
    availability_target: str | None = Field(default=None, description="可用性目标")
    budget_range: str | None = Field(default=None, description="预算区间")
    compliance: str | None = Field(default=None, description="合规约束")
    existing_systems: str | None = Field(default=None, description="现有系统")

    def missing_fields(self) -> list[str]:
        return [f for f in ("scale", "availability_target", "budget_range", "compliance", "existing_systems") if getattr(self, f) is None]


class StructureRequirementsTool(OpenArchTool):
    name = "structure_requirements"
    description = (
        "把从对话中提炼的需求整理为结构化需求卡。business_scenario 必填；"
        "其余字段未从用户处获得时不要编造，留空并用 missing_fields 主动追问。"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "business_scenario": {"type": "string"},
            "scale": {"type": ["string", "null"]},
            "availability_target": {"type": ["string", "null"]},
            "budget_range": {"type": ["string", "null"]},
            "compliance": {"type": ["string", "null"]},
            "existing_systems": {"type": ["string", "null"]},
        },
        "required": ["business_scenario"],
    }
    is_concurrency_safe = True
    is_read_only = True

    async def call(
        self,
        business_scenario: str,
        scale: str | None = None,
        availability_target: str | None = None,
        budget_range: str | None = None,
        compliance: str | None = None,
        existing_systems: str | None = None,
    ) -> ToolChunk:
        card = RequirementsCard(
            business_scenario=business_scenario,
            scale=scale,
            availability_target=availability_target,
            budget_range=budget_range,
            compliance=compliance,
            existing_systems=existing_systems,
        )
        return ToolChunk(
            content=[
                TextBlock(
                    text=json.dumps(
                        {"card": card.model_dump(), "missing_fields": card.missing_fields()},
                        ensure_ascii=False,
                    )
                )
            ]
        )
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_requirements_tools.py -v`
Expected: 2 passed

- [ ] **Step 5: 提交**

```bash
git add src/openarch/tools/requirements_tools.py tests/unit/test_requirements_tools.py
git commit -m "feat: 结构化需求卡工具"
```

---

### Task 7: WAF 评审工具（清单 + 评分）

**Files:**
- Create: `skills/aliyun-waf/checklist.yaml`
- Create: `src/openarch/tools/waf_tools.py`
- Test: `tests/unit/test_waf_tools.py`

- [ ] **Step 1: 写 `skills/aliyun-waf/checklist.yaml`**（内容基于阿里云公开 Well-Architected Framework 文档整理，仅收录公开可溯源条目）

```yaml
# 阿里云 Well-Architected Framework 五支柱检查清单（公开文档整理，MVP 精简版）
pillars:
  可靠性:
    - {id: REL-01, description: 关键应用跨可用区部署，无单可用区故障风险}
    - {id: REL-02, description: 无状态组件前端配置负载均衡并配置健康检查}
    - {id: REL-03, description: 数据层有主备/多副本机制，RPO/RTO 目标明确}
    - {id: REL-04, description: 有经过演练的备份与恢复方案（定期快照/克隆）}
    - {id: REL-05, description: 依赖服务故障有降级与熔断策略}
  安全性:
    - {id: SEC-01, description: 使用 RAM/STS 最小权限访问控制，无长期明文 AK}
    - {id: SEC-02, description: 入口流量有 WAF/DDoS 防护，安全组最小开放}
    - {id: SEC-03, description: 传输与存储数据加密（TLS、KMS、云盘加密）}
    - {id: SEC-04, description: 有操作审计与日志留存（ActionTrail/日志服务）}
    - {id: SEC-05, description: 补丁与镜像漏洞有定期扫描修复机制}
  成本优化:
    - {id: COST-01, description: 实例规格与业务负载匹配，避免长期超配}
    - {id: COST-02, description: 稳态负载使用包年包月/节省计划，弹性部分按量}
    - {id: COST-03, description: 存储分层（热/冷数据分级，生命周期规则）}
    - {id: COST-04, description: 有成本可见性（费用标签、预算告警）}
    - {id: COST-05, description: 评估 Serverless/弹性伸缩削峰填谷的机会}
  性能效率:
    - {id: PERF-01, description: 有容量评估依据（QPS/带宽/存储增长模型）}
    - {id: PERF-02, description: 使用缓存/CDN 承接热点读流量}
    - {id: PERF-03, description: 数据库读写分离/分库分表方案与数据量匹配}
    - {id: PERF-04, description: 异步化与削峰（消息队列）设计}
    - {id: PERF-05, description: 全链路压测或基准测试计划}
  运维:
    - {id: OPS-01, description: 基础设施即代码（IaC），环境可重建}
    - {id: OPS-02, description: CI/CD 流水线含自动化测试与灰度发布}
    - {id: OPS-03, description: 统一可观测（指标/日志/链路追踪）与告警分级}
    - {id: OPS-04, description: 有值班与应急响应流程（on-call/升级路径）}
    - {id: OPS-05, description: 定期故障复盘并沉淀 runbook}
```

- [ ] **Step 2: 写失败测试**

```python
import json
from pathlib import Path

from openarch.tools.waf_tools import ReviewWithWafTool, load_checklist

CHECKLIST = Path(__file__).parents[2] / "skills" / "aliyun-waf" / "checklist.yaml"


def test_load_checklist():
    checklist = load_checklist(CHECKLIST)
    assert set(checklist) == {"可靠性", "安全性", "成本优化", "性能效率", "运维"}
    assert checklist["可靠性"][0]["id"] == "REL-01"


def _all_findings() -> list[dict]:
    findings = [
        {"item_id": "REL-01", "status": "pass", "evidence": "双可用区 ECS"},
        {"item_id": "REL-02", "status": "risk", "evidence": "SLB 未配健康检查"},
        {"item_id": "REL-03", "status": "fail", "evidence": "单实例 RDS"},
        {"item_id": "REL-04", "status": "pass", "evidence": "每日快照"},
        {"item_id": "REL-05", "status": "pass", "evidence": "哨兵+熔断"},
    ]
    for prefix in ("SEC", "COST", "PERF", "OPS"):
        for n in range(1, 6):
            findings.append({"item_id": f"{prefix}-{n:02d}", "status": "pass", "evidence": "有"})
    return findings


async def test_review_scores_and_risks():
    tool = ReviewWithWafTool(checklist_path=CHECKLIST)
    out = json.loads(
        (
            await tool(architecture_summary="电商双 11 架构", findings=_all_findings())
        ).content[0].text
    )
    assert out["pillar_scores"]["可靠性"]["score"] == 0.9  # (4 + 0.5) / 5
    assert out["pillar_scores"]["可靠性"]["total"] == 5
    assert {"item_id": "REL-03", "status": "fail"} <= out["high_risks"][0]
    assert {"item_id": "REL-02", "status": "risk"} <= out["high_risks"][1]


async def test_unknown_and_missing_items_rejected():
    tool = ReviewWithWafTool(checklist_path=CHECKLIST)
    out = json.loads(
        (
            await tool(
                architecture_summary="x",
                findings=[{"item_id": "XXX-99", "status": "pass", "evidence": "e"}],
            )
        ).content[0].text
    )
    assert "error" in out
```

- [ ] **Step 3: 运行确认失败**

Run: `uv run pytest tests/unit/test_waf_tools.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: 实现 `src/openarch/tools/waf_tools.py`**

```python
from __future__ import annotations

import json
from pathlib import Path

import yaml
from agentscope.message import TextBlock
from agentscope.tool import ToolChunk

from openarch.tools.base import OpenArchTool

_VALID_STATUS = {"pass", "risk", "fail"}
_WEIGHT = {"pass": 1.0, "risk": 0.5, "fail": 0.0}


def load_checklist(path: Path) -> dict[str, list[dict]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {p: list(items) for p, items in data["pillars"].items()}


class ReviewWithWafTool(OpenArchTool):
    name = "review_with_waf"
    description = (
        "对架构方案做阿里云 Well-Architected 五支柱评审。先用 Skill viewer 读取 "
        "aliyun-waf 技能并逐项评估，再调用本工具提交 findings（每项：item_id、"
        "status=pass|risk|fail、evidence、recommendation 可选）。工具校验覆盖完整性"
        "并计算评分表与高风险清单。"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "architecture_summary": {
                "type": "string",
                "description": "一句话架构概述",
            },
            "findings": {
                "type": "array",
                "description": "逐项评估结果，必须覆盖清单全部条目且不重复",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["pass", "risk", "fail"]},
                        "evidence": {"type": "string"},
                        "recommendation": {"type": "string"},
                    },
                    "required": ["item_id", "status", "evidence"],
                },
            },
        },
        "required": ["architecture_summary", "findings"],
    }
    is_concurrency_safe = True
    is_read_only = True

    def __init__(self, checklist_path: Path):
        self._checklist = load_checklist(checklist_path)

    async def call(self, architecture_summary: str, findings: list[dict]) -> ToolChunk:
        all_ids = {it["id"]: p for p, items in self._checklist.items() for it in items}
        errors: list[str] = []
        seen: set[str] = set()
        for f in findings:
            fid = f.get("item_id")
            if fid not in all_ids:
                errors.append(f"未知条目 {fid}")
            elif fid in seen:
                errors.append(f"条目重复 {fid}")
            if f.get("status") not in _VALID_STATUS:
                errors.append(f"{fid} 的 status 必须是 pass/risk/fail")
            seen.add(fid)
        missing = [i for i in all_ids if i not in seen]
        if errors or missing:
            return ToolChunk(
                content=[
                    TextBlock(
                        text=json.dumps(
                            {"error": errors + ([f"缺少条目: {missing}"] if missing else [])},
                            ensure_ascii=False,
                        )
                    )
                ]
            )

        pillar_scores: dict[str, dict] = {}
        high_risks: list[dict] = []
        by_id = {f["item_id"]: f for f in findings}
        for pillar, items in self._checklist.items():
            total = len(items)
            weight = sum(_WEIGHT[by_id[it["id"]]["status"]] for it in items)
            pillar_scores[pillar] = {
                "score": round(weight / total, 2),
                "passed": sum(1 for it in items if by_id[it["id"]]["status"] == "pass"),
                "total": total,
            }
            for it in items:
                f = by_id[it["id"]]
                if f["status"] in ("risk", "fail"):
                    high_risks.append(
                        {
                            "item_id": it["id"],
                            "pillar": pillar,
                            "description": it["description"],
                            "status": f["status"],
                            "evidence": f["evidence"],
                            "recommendation": f.get("recommendation", ""),
                        }
                    )
        return ToolChunk(
            content=[
                TextBlock(
                    text=json.dumps(
                        {
                            "architecture_summary": architecture_summary,
                            "pillar_scores": pillar_scores,
                            "high_risks": high_risks,
                        },
                        ensure_ascii=False,
                    )
                )
            ]
        )
```

- [ ] **Step 5: 运行确认通过**

Run: `uv run pytest tests/unit/test_waf_tools.py -v`
Expected: 3 passed

- [ ] **Step 6: 提交**

```bash
git add skills/aliyun-waf/checklist.yaml src/openarch/tools/waf_tools.py tests/unit/test_waf_tools.py
git commit -m "feat: WAF 五支柱评审工具（清单校验+评分）"
```

---

### Task 8: 交付物打包工具

**Files:**
- Create: `src/openarch/tools/deliverable_tools.py`
- Test: `tests/unit/test_deliverable_tools.py`

- [ ] **Step 1: 写失败测试**

```python
import json

from openarch.tools.deliverable_tools import ExportDeliverableTool

REQ = {"card": {"business_scenario": "电商"}, "missing_fields": []}
WAF = {
    "pillar_scores": {"可靠性": {"score": 0.9, "passed": 4, "total": 5}},
    "high_risks": [],
}


async def test_export_writes_markdown(tmp_path):
    tool = ExportDeliverableTool(workspace=tmp_path)
    out = json.loads(
        (
            await tool(
                title="电商架构方案",
                requirements_card_json=json.dumps(REQ, ensure_ascii=False),
                solution_markdown="# 方案\n采用 SLB+ECS+RDS。",
                mermaid_code="flowchart TD\n  a[入口] --> b[应用]",
                waf_review_json=json.dumps(WAF, ensure_ascii=False),
            )
        ).content[0].text
    )
    path = tmp_path / out["file"]
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for section in ["需求卡", "架构方案", "架构图", "Well-Architected 评审"]:
        assert section in text
    assert "flowchart TD" in text and "SLB+ECS+RDS" in text


async def test_filename_is_timestamped(tmp_path):
    tool = ExportDeliverableTool(workspace=tmp_path)
    out = json.loads(
        (
            await tool(
                title="方案A",
                requirements_card_json="{}",
                solution_markdown="s",
                mermaid_code="flowchart TD\n  a --> b",
                waf_review_json="{}",
            )
        ).content[0].text
    )
    assert out["file"].endswith(".md") and "-" in out["file"]
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_deliverable_tools.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 `src/openarch/tools/deliverable_tools.py`**

```python
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from agentscope.message import TextBlock
from agentscope.tool import ToolChunk

from openarch.tools.base import OpenArchTool


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip()).strip("-")
    return (slug or "deliverable")[:40]


class ExportDeliverableTool(OpenArchTool):
    name = "export_deliverable"
    description = (
        "把一次架构设计会话的产物组装为 Markdown 交付文档（需求卡、方案、架构图、"
        "WAF 评审），写入工作目录并返回路径。工作流最后一步必须调用。"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "交付物标题"},
            "requirements_card_json": {"type": "string", "description": "structure_requirements 输出的 JSON"},
            "solution_markdown": {"type": "string", "description": "方案正文（Markdown）"},
            "mermaid_code": {"type": "string", "description": "已通过校验的 Mermaid 代码"},
            "waf_review_json": {"type": "string", "description": "review_with_waf 输出的 JSON"},
        },
        "required": ["title", "requirements_card_json", "solution_markdown", "mermaid_code", "waf_review_json"],
    }
    is_concurrency_safe = True
    is_read_only = False

    def __init__(self, workspace: Path):
        self._workspace = workspace

    def _pretty(self, raw: str) -> str:
        try:
            return json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return raw

    async def call(
        self,
        title: str,
        requirements_card_json: str,
        solution_markdown: str,
        mermaid_code: str,
        waf_review_json: str,
    ) -> ToolChunk:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self._workspace / f"{ts}-{_slugify(title)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {title}\n\n"
            f"> 由 OpenArch 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "## 需求卡\n\n```json\n"
            f"{self._pretty(requirements_card_json)}\n```\n\n"
            "## 架构方案\n\n"
            f"{solution_markdown}\n\n"
            "## 架构图\n\n```mermaid\n"
            f"{mermaid_code}\n```\n\n"
            "## Well-Architected 评审\n\n```json\n"
            f"{self._pretty(waf_review_json)}\n```\n",
            encoding="utf-8",
        )
        return ToolChunk(
            content=[TextBlock(text=json.dumps({"file": path.name}, ensure_ascii=False))]
        )
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_deliverable_tools.py -v`
Expected: 2 passed

- [ ] **Step 5: 提交**

```bash
git add src/openarch/tools/deliverable_tools.py tests/unit/test_deliverable_tools.py
git commit -m "feat: 交付物打包工具"
```

---

### Task 9: 三个技能包内容

**Files:**
- Create: `skills/arch-design/SKILL.md`、`skills/arch-design/content/patterns.md`、`skills/arch-design/content/decision-tree.md`
- Create: `skills/aliyun-waf/SKILL.md`
- Create: `skills/sa-playbooks/SKILL.md`、`skills/sa-playbooks/content/cloud-assessment.md`、`skills/sa-playbooks/content/cost-optimization.md`
- Test: `tests/unit/test_skills_format.py`

- [ ] **Step 1: 写格式 lint 测试（先失败）**

```python
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parents[2] / "skills"

EXPECTED = {"arch-design", "aliyun-waf", "sa-playbooks"}


def test_every_skill_has_valid_frontmatter():
    found = set()
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        found.add(skill_dir.name)
        fm = (skill_dir / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        meta = yaml.safe_load(fm)
        assert meta["name"] == skill_dir.name, skill_dir.name
        assert len(meta["description"]) > 10
    assert found == EXPECTED
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_skills_format.py -v`
Expected: FAIL — 目录为空

- [ ] **Step 3: 写 `skills/arch-design/SKILL.md`**

```markdown
---
name: arch-design
description: 架构设计方法论：需求分析框架、常见场景参考模式与阿里云选型决策树，用于产出云上架构方案
---

# 架构设计方法论

按以下顺序工作：**需求结构化 → 场景模式匹配 → 方案设计 → 图输出 → WAF 评审**。

## 1. 需求分析框架

先用 `structure_requirements` 工具固化需求卡。缺失字段必须追问，不要假设：

- 业务场景：做什么？谁是用户？
- 规模：QPS/并发/数据量/增长预期
- 可用性目标：99.9% 还是 99.99%？能否接受分钟级不可用？
- 预算与合规：成本约束、等保/行业监管要求
- 现有系统：迁移还是新建？有什么必须兼容？

## 2. 场景参考模式

见 `content/patterns.md`：Web 应用、数据平台、AI 推理服务三类高频场景的参考架构。

## 3. 选型决策树

见 `content/decision-tree.md`：计算、数据库、消息、缓存、网络的阿里云选型决策路径。

## 4. 方案输出要求

方案正文必须包含：组件清单与选型理由、容量估算依据、关键风险与对策。
架构图用 Mermaid flowchart（`flowchart TD` 开头），产出后调用 `validate_diagram` 校验。
```

- [ ] **Step 4: 写 `skills/arch-design/content/patterns.md`**

```markdown
# 常见场景参考模式（阿里云）

## Web 应用（交易/内容类）

SLB/ALB → 无状态应用（ECS 弹性伸缩组 / ACK）→ RDS PostgreSQL/MySQL（主备）
+ Redis 缓存 + OSS 静态资源 + CDN；异步任务走 RocketMQ；入口挂 WAF。
读多写少先加缓存与读写分离；峰值明显用 ESSD AutoPL 与弹性伸缩。

## 数据平台

DataWorks 同步 → OSS 数据湖（DLF 元数据）→ MaxCompute/EMR 加工 →
Hologres/StarRocks 服务化查询 → Quick BI。批流一体按时效要求选 Flink。

## AI 推理服务

PAI-EAS 或自建：GPU 节点池（ACK）+ 网关（自定义指标弹性伸缩）+ Cache 相同请求去重 +
模型工件 OSS + Prometheus/Grafana 观测。大流量场景评估 PD 分离与量化。

## 模式选择原则

先匹配最接近的参考模式做起点，再按需求卡逐项裁剪；每处偏离参考模式都要写明理由。
```

- [ ] **Step 5: 写 `skills/arch-design/content/decision-tree.md`**

```markdown
# 阿里云选型决策树（精简）

## 计算

- 容器化且需要编排 → ACK；简单无状态长驻 → ECS 弹性伸缩组
- 事件驱动/短任务/流量波动大 → 函数计算 FC
- GPU 推理 → ACK GPU 节点池 或 PAI-EAS

## 数据库

- 关系型、事务 → RDS MySQL/PostgreSQL（默认主备高可用版）
- 海量并发读 + 弹性 → PolarDB
- 文档/宽表、超大规模 → MongoDB/Lindorm
- 缓存 → Redis（集群版按 QPS 选规格）

## 消息

- 顺序/事务/延迟消息 → RocketMQ
- 大数据流接入、日志 → Kafka / 日志服务 SLS
- 仅异步解耦、轻量 → MNS

## 网络

- 公网入口 → SLB/ALB（+ WAF + DDoS 防护）
- 多环境隔离 → VPC + 交换机划分；混合云 → 高速通道/VPN 网关
- 全球加速 → GA

原则：托管服务优先于自建；同一方案内避免引入能力重叠的组件。
```

- [ ] **Step 6: 写 `skills/aliyun-waf/SKILL.md`**

```markdown
---
name: aliyun-waf
description: 阿里云 Well-Architected Framework 五支柱检查清单：架构方案评审时逐项评估并生成评分与风险清单
---

# 阿里云 Well-Architected 评审

对已完成初稿的架构方案执行评审：

1. 用 `review_with_waf` 工具的清单（`skills/aliyun-waf/checklist.yaml`）逐项对照方案：
   - **pass**：方案已明确覆盖，写明 evidence（方案中的对应设计）
   - **risk**：部分覆盖或依赖假设，写 evidence + recommendation
   - **fail**：完全未覆盖，写 evidence（缺失说明）+ recommendation
2. 所有条目都必须给出结论（工具会拒绝缺失/未知/重复条目）
3. 评审结论中：score < 0.6 的支柱和全部 fail 项必须在方案"关键风险与对策"中给出改进措施

清单基于阿里云公开的 Well-Architected Framework 文档整理（MVP 精简版，每支柱 5 项）。
```

- [ ] **Step 7: 写 `skills/sa-playbooks/SKILL.md`**

```markdown
---
name: sa-playbooks
description: SA 交付 playbook：上云评估与成本优化两个标准交付流程，含步骤、产出物与话术要点
---

# SA 交付 Playbook

两个标准流程，按客户请求选择：

- `content/cloud-assessment.md`：上云评估（从 0 到 1 或从 IDC 迁移）
- `content/cost-optimization.md`：云上成本优化（存量账单优化）

每个 playbook 产出物统一用 `export_deliverable` 打包交付。
```

- [ ] **Step 8: 写 `skills/sa-playbooks/content/cloud-assessment.md`**

```markdown
# 上云评估 Playbook

## 流程

1. **现状盘点**：应用清单、依赖拓扑、资源规格、年度 TCO（机房/硬件/人力/带宽）
2. **上云适配分析**：应用按"直接迁移 Rehost / 少量改造 Replatform / 重构 Refactor / 淘汰 Retire"分类
3. **目标架构设计**：按 arch-design 方法论产出目标架构与迁移批次
4. **成本对比**：目标云上月成本 vs 现状 TCO 摊销，给出 3 年 TCO 曲线
5. **风险与计划**：割接窗口、回滚方案、双跑期、责任矩阵

## 产出物

需求卡、目标架构图（Mermaid + drawio）、迁移批次表、TCO 对比表、风险清单。

## 关键话术

- 迁移不是照搬：先做适配分析再谈成本
- 割接必须有回滚窗口；数据库迁移用 DTS 双向同步做双跑
```

- [ ] **Step 9: 写 `skills/sa-playbooks/content/cost-optimization.md`**

```markdown
# 云上成本优化 Playbook

## 流程

1. **账单透视**：按产品/标签/团队拆分月账单，找 Top 5 成本项
2. **计算优化**：CPU/内存利用率画像 → 稳态负载转包年包月/节省计划 → 弹性负载上自动伸缩 → 长期低利用率实例降配或回收
3. **存储优化**：生命周期分层（热→低频→归档）、删除过期快照、ESSD 按性能等级降配
4. **网络优化**：跨区/公网流量治理、CDN 回源优化、闲置 EIP/SLB 清理
5. **机制建设**：费用标签规范、预算与异常告警、月度成本例会

## 产出物

需求卡、优化项清单（项/预期节省/责任人/风险）、优化后架构图（如有变更）、月度节省目标。

## 关键话术

- 先可观测再优化：没有成本标签的优化都是盲打
- 区分"省下的钱"与"延后的钱"：包年包月是把弹性换成折扣
```

- [ ] **Step 10: 运行确认通过**

Run: `uv run pytest tests/unit/test_skills_format.py -v`
Expected: 1 passed

- [ ] **Step 11: 提交**

```bash
git add skills/ tests/unit/test_skills_format.py
git commit -m "feat: 三个 SA 技能包（arch-design / aliyun-waf / sa-playbooks）"
```

---

### Task 10: Agent 装配与 CLI 入口

**Files:**
- Create: `src/openarch/agent.py`
- Create: `src/openarch/main.py`
- Test: `tests/unit/test_agent_build.py`

- [ ] **Step 1: 写失败测试**

```python
from openarch.agent import build_agent
from openarch.config import load_settings


def test_build_agent_with_fake_key(tmp_path):
    skills = tmp_path / "skills"
    (skills / "demo").mkdir(parents=True)
    (skills / "demo" / "SKILL.md").write_text(
        "---\nname: demo\ndescription: 演示技能\n---\n内容",
        encoding="utf-8",
    )
    settings = load_settings(
        env={"DASHSCOPE_API_KEY": "sk-test", "OPENARCH_SKILLS_DIR": str(skills)}
    )
    agent = build_agent(settings)
    assert agent.name == "openarch"


def test_build_agent_with_openai_compatible(tmp_path):
    settings = load_settings(
        env={
            "DASHSCOPE_API_KEY": "sk-test",
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": "sk-local",
        }
    )
    agent = build_agent(settings)
    assert agent.name == "openarch"
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_agent_build.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 `src/openarch/agent.py`**

```python
from __future__ import annotations

from pathlib import Path

from agentscope.agent import Agent
from agentscope.credential import DashScopeCredential
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.skill import LocalSkillLoader
from agentscope.tool import Toolkit

from openarch.config import Settings
from openarch.tools.deliverable_tools import ExportDeliverableTool
from openarch.tools.diagram_tools import ExportDrawioTool, ValidateDiagramTool
from openarch.tools.requirements_tools import StructureRequirementsTool
from openarch.tools.waf_tools import ReviewWithWafTool

SYSTEM_PROMPT = """你是 OpenArch，一名资深 Solutions Architect（阿里云方向）。

你的工作流（严格按顺序）：
1. 需求澄清：用 structure_requirements 固化需求卡；missing_fields 非空时逐项追问用户，不要假设
2. 方案生成：先读取 arch-design 技能（Skill viewer），按其方法论产出方案（含组件清单、选型理由、容量估算、风险对策）
3. 架构图：产出 Mermaid flowchart，用 validate_diagram 校验（失败修正重试，最多 2 次），通过后用 export_drawio 导出
4. WAF 评审：读取 aliyun-waf 技能，逐项评估后用 review_with_waf 提交，低分支柱与 fail 项必须写入方案对策
5. 交付打包：用 export_deliverable 生成 Markdown 交付文档并告知用户路径

原则：阿里云产品体系优先；托管服务优先于自建；每个选型给出理由；不确定的需求问用户。"""


def build_model(settings: Settings):
    if settings.base_url:
        return OpenAIChatModel(
            api_key=settings.openai_api_key,
            base_url=settings.base_url,
            model=settings.model,
        )
    return DashScopeChatModel(
        credential=DashScopeCredential(api_key=settings.dashscope_api_key),
        model=settings.model,
    )


def build_agent(settings: Settings) -> Agent:
    toolkit = Toolkit(
        tools=[
            StructureRequirementsTool(),
            ValidateDiagramTool(),
            ExportDrawioTool(workspace=settings.workspace),
            ReviewWithWafTool(
                checklist_path=_checklist_path(settings.skills_dir)
            ),
            ExportDeliverableTool(workspace=settings.workspace),
        ],
        skills_or_loaders=[
            LocalSkillLoader(directory=str(settings.skills_dir), scan_subdir=True)
        ],
    )
    return Agent(
        name="openarch",
        system_prompt=SYSTEM_PROMPT,
        model=build_model(settings),
        toolkit=toolkit,
    )


def _checklist_path(skills_dir: Path) -> Path:
    return skills_dir / "aliyun-waf" / "checklist.yaml"
```

- [ ] **Step 4: 实现 `src/openarch/main.py`**

```python
from __future__ import annotations

import asyncio

from agentscope.console import launch_console

from openarch.agent import build_agent
from openarch.config import load_settings


def main() -> None:
    settings = load_settings()
    agent = build_agent(settings)
    print(f"OpenArch 就绪（模型：{settings.model}，技能目录：{settings.skills_dir}）")
    asyncio.run(launch_console(agent))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 运行确认通过**

Run: `uv run pytest tests/unit/test_agent_build.py -v`
Expected: 2 passed

- [ ] **Step 6: 冒烟验证（手动）**

```bash
DASHSCOPE_API_KEY=sk-dummy uv run python -c "
from openarch.config import load_settings
from openarch.agent import build_agent
print(build_agent(load_settings(env={'DASHSCOPE_API_KEY': 'x'})).name)
"
```

Expected: 打印 `openarch`（含真实技能加载，无异常即通过）。再手动运行 `uv run openarch` 确认进入终端对话界面，Ctrl+C 退出。

- [ ] **Step 7: 提交**

```bash
git add src/openarch/agent.py src/openarch/main.py tests/unit/test_agent_build.py
git commit -m "feat: Agent 装配与 openarch CLI 入口（launch_console）"
```

---

### Task 11: Docker 与 CI

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 写 `Dockerfile`**

```dockerfile
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY skills/ ./skills/
COPY tests/ ./tests/

RUN uv sync --frozen --no-dev

ENV OPENARCH_WORKSPACE=/data/deliverables
VOLUME ["/data/deliverables"]

CMD ["uv", "run", "openarch"]
```

- [ ] **Step 2: 写 `docker-compose.yml`**

```yaml
services:
  openarch:
    build: .
    env_file: .env
    stdin_open: true
    tty: true
    volumes:
      - ./deliverables:/data/deliverables
```

- [ ] **Step 3: 写 `.github/workflows/ci.yml`**

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.11"
      - run: uv sync
      - run: uv run ruff check src tests
      - run: uv run pytest -m "not e2e" -v
```

- [ ] **Step 4: 本地验证 CI 等价命令**

```bash
uv run ruff check src tests
uv run pytest -m "not e2e" -v
```

Expected: ruff 无报错；全部单测通过。

- [ ] **Step 5: 提交**

```bash
git add Dockerfile docker-compose.yml .github/workflows/ci.yml
git commit -m "ci: Dockerfile、compose 与 GitHub Actions 单测流水线"
```

---

### Task 12: e2e 冒烟与 README

**Files:**
- Create: `tests/e2e/test_smoke.py`
- Create: `README.md`（重写占位文件）

- [ ] **Step 1: 写 e2e 冒烟测试**

```python
import os
from dataclasses import replace

import pytest

pytestmark = pytest.mark.e2e

pytest.importorskip("agentscope")


@pytest.fixture()
def settings(tmp_path):
    if not os.environ.get("DASHSCOPE_API_KEY"):
        pytest.skip("需要 DASHSCOPE_API_KEY")
    from openarch.config import load_settings

    return replace(load_settings(), workspace=tmp_path)


async def test_agent_replies(settings, tmp_path):
    from agentscope.message import Msg

    from openarch.agent import build_agent

    agent = build_agent(settings)
    reply = await agent(Msg("user", "给一个日均 10 万订单的电商设计架构，直接开始。", "user"))
    text = str(reply.get_text_content() or "")
    assert text.strip(), "Agent 返回了空回复"
    assert ("mermaid" in text) or any(tmp_path.iterdir()), (
        "回复中应包含架构图或产出交付物文件"
    )
```

（`Settings` 是 frozen dataclass，改 workspace 用 `dataclasses.replace`。若 `agent(Msg(...))` 或 `reply.get_text_content()` 签名与当前 agentscope 版本不符，按 https://docs.agentscope.io/latest/en/building-blocks/agent/overview 修正调用方式，断言保持不变。）

- [ ] **Step 2: 本地运行 e2e（需真实 Key）**

```bash
uv run pytest -m e2e -v
```

Expected: 1 passed（无 Key 时显示 skipped）。若 `agent(Msg(...))` 调用签名与 2.0.8 不符，按 https://docs.agentscope.io/latest/en/building-blocks/agent/overview 修正调用方式，断言保持不变。

- [ ] **Step 3: 写 `README.md`**

```markdown
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
```

- [ ] **Step 4: 全量回归**

```bash
uv run ruff check src tests && uv run pytest -m "not e2e" -v
```

Expected: 全部通过。

- [ ] **Step 5: 提交**

```bash
git add tests/e2e/test_smoke.py README.md
git commit -m "test+docs: e2e 冒烟测试与项目 README"
```

---

## 验收清单（对照规格）

| 规格条目 | 任务 |
|---|---|
| §3 总体架构（Agent+Toolkit+Console+DashScope） | Task 10 |
| §4 仓库结构 | Task 1（骨架），各任务逐一落实 |
| §5 工作流五步 | Task 6/3-5/7/8 + Task 10 系统提示词编排 |
| §6 技能资产（三个包 + SKILL.md 规范） | Task 9（+Task 7 checklist.yaml） |
| §7 五个工具 | Task 5/6/7/8 |
| §8 配置与启动（openarch 命令 / docker） | Task 2/10/11 |
| §9 错误处理（Key 缺失即败 / mermaid 重试 / 结构化错误） | Task 2/3/5 |
| §10 测试策略（单测+e2e） | 全部任务 TDD + Task 12 |
| §12 Non-Goals（无数据库/无用户系统） | 全程未引入 |
