"""Mermaid flowchart 解析与校验（纯逻辑，供后续 validate_diagram 工具与 draw.io 转换复用）。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_DIRECTIONS = {"TD", "TB", "LR", "RL", "BT"}

# 节点形状（按优先级排列）：[(文本)] 数据库 | [文本] 矩形 | (文本) 圆角 | {文本} 菱形
_SHAPE_ALT = r"\[\([^\]]*\)\]|\[[^\]]*\]|\([^)]*\)|\{[^}]*\}"
# 边的端点原子：裸 id，或 id + 可选形状，如 `slb`、`web[Web 前端]`、`db[(数据库)]`
_NODE_ATOM = rf"\w+\s*(?:{_SHAPE_ALT})?"

_NODE_RE = re.compile(
    r"^\s*(?P<id>\w+)\s*(?P<shape>\[\((?P<db>[^\]]*)\)\]|\[(?P<rect>[^\]]*)\]"
    r"|\((?P<round>[^)]*)\)|\{(?P<diamond>[^}]*)\})?\s*$"
)
_EDGE_RE = re.compile(
    r"^\s*(?P<src>" + _NODE_ATOM + r")\s*(?P<arrow>-{2,3}>|---)\s*"
    r"(?:\|(?P<label>[^|]*)\|\s*)?(?P<dst>" + _NODE_ATOM + r")\s*$"
)
_HEADER_RE = re.compile(r"^flowchart\s+(\S+)\s*$")


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


def _node_from_atom(atom: str) -> Node:
    """从边的端点原子（如 `web[Web 前端]`）还原节点；裸 id 视为 point 节点。"""
    m = _NODE_RE.match(atom.strip())
    return _node_from_match(m) if m else Node(atom.strip(), "point", "")


def _register_endpoint(fc: Flowchart, node: Node) -> None:
    """登记边的端点：带形状则定义/覆盖节点；裸 id 不覆盖已有节点定义。"""
    if node.shape == "point":
        fc.nodes.setdefault(node.id, node)
    else:
        fc.nodes[node.id] = node


def parse_flowchart(text: str) -> Flowchart:
    """解析（假设已通过 validate）。边缘引用的未知 id 按隐式节点处理。"""
    fc = Flowchart()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        header = _HEADER_RE.match(line)
        if header:
            fc.direction = header.group(1)
            continue
        e = _EDGE_RE.match(line)
        if e:
            src = _node_from_atom(e.group("src"))
            dst = _node_from_atom(e.group("dst"))
            fc.edges.append(
                Edge(
                    src=src.id,
                    dst=dst.id,
                    label=(e.group("label") or "").strip(),
                    directed=e.group("arrow").endswith(">"),
                )
            )
            _register_endpoint(fc, src)
            _register_endpoint(fc, dst)
            continue
        n = _NODE_RE.match(line)
        if n:
            _register_endpoint(fc, _node_from_match(n))
    return fc


def validate_mermaid(text: str) -> ValidationResult:
    errors: list[str] = []
    lines = text.splitlines()
    header_idx = next(
        (i for i, ln in enumerate(lines) if _HEADER_RE.match(ln.strip())), None
    )
    if header_idx is None:
        errors.append("第 1 行附近：缺少 `flowchart <方向>` 头，例如 `flowchart TD`")
    else:
        m = _HEADER_RE.match(lines[header_idx].strip())
        if not m or m.group(1) not in _DIRECTIONS:
            errors.append(
                f"第 {header_idx + 1} 行：`flowchart` 方向必须是 {'/'.join(sorted(_DIRECTIONS))}"
            )

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
