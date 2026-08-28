"""Mermaid Flowchart → draw.io (mxGraph) XML 转换（纯逻辑，供 export_drawio 工具复用）。"""
from __future__ import annotations

import html
from xml.sax.saxutils import escape

from openarch.tools.mermaid import Flowchart

_W, _H, _DX, _DY = 160, 48, 240, 110

_SHAPE_STYLE = {
    "rect": "rounded=1;whiteSpace=wrap;html=1;",
    "round": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;",
    "diamond": "rhombus;whiteSpace=wrap;html=1;",
    "db": "shape=cylinder3;whiteSpace=wrap;html=1;",
    "point": "ellipse;whiteSpace=wrap;html=1;",
}


def _escape(text: str) -> str:
    # 属性值用双引号包裹，`"` 也必须转义，否则产生非法 XML
    return escape(html.unescape(text), {'"': "&quot;"})


def _layout(fc: Flowchart) -> tuple[dict[str, tuple[int, int]], list[list[str]]]:
    """按拓扑层级网格布局：返回 id→(x, y) 与分层列表。

    层级取从入度 0 根节点出发的 BFS 首达层级：每个节点只在首次到达时定级
    并入队，保证含环的图也能终止（按 max 松弛会在正环上永不收敛）。
    纯环等不可达节点兜底归入第 0 层。
    """
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
                if c not in level:
                    level[c] = level[nid] + 1
                    nxt.append(c)
        frontier = nxt
    for nid in fc.nodes:
        level.setdefault(nid, 0)
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
    pos, _rows = _layout(fc)
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
