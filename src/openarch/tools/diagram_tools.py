"""架构图工具：Mermaid 校验与 draw.io 导出（AgentScope ToolBase 子类）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import ClassVar

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
    input_schema: ClassVar[dict] = {
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
            content=[
                TextBlock(
                    text=json.dumps(
                        {"ok": r.ok, "errors": r.errors}, ensure_ascii=False
                    )
                )
            ]
        )


class ExportDrawioTool(OpenArchTool):
    name = "export_drawio"
    description = (
        "将已通过 validate_diagram 校验的 Mermaid flowchart 转为可编辑的 "
        "draw.io 文件，返回文件路径。"
    )
    input_schema: ClassVar[dict] = {
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
                content=[
                    TextBlock(
                        text=json.dumps({"error": r.errors}, ensure_ascii=False)
                    )
                ]
            )
        out_dir = self._workspace / "diagrams"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        path = out_dir / f"{ts}-{_slugify(title)}.drawio"
        path.write_text(
            flowchart_to_drawio(parse_flowchart(mermaid_code), title),
            encoding="utf-8",
        )
        return ToolChunk(
            content=[
                TextBlock(
                    text=json.dumps(
                        {"file": str(path.relative_to(self._workspace))},
                        ensure_ascii=False,
                    )
                )
            ]
        )
