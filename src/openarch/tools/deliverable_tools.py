"""交付物打包工具：把一次架构设计会话的产物组装为 Markdown 文档。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import ClassVar

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
    input_schema: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "交付物标题"},
            "requirements_card_json": {
                "type": "string",
                "description": "structure_requirements 输出的 JSON",
            },
            "solution_markdown": {"type": "string", "description": "方案正文（Markdown）"},
            "mermaid_code": {"type": "string", "description": "已通过校验的 Mermaid 代码"},
            "waf_review_json": {"type": "string", "description": "review_with_waf 输出的 JSON"},
        },
        "required": [
            "title",
            "requirements_card_json",
            "solution_markdown",
            "mermaid_code",
            "waf_review_json",
        ],
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
        ts = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        path = self._workspace / f"{ts}-{_slugify(title)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        path.write_text(
            f"# {title}\n\n"
            f"> 由 OpenArch 生成于 {generated_at}\n\n"
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
            content=[
                TextBlock(
                    text=json.dumps(
                        {"file": str(path.relative_to(self._workspace))},
                        ensure_ascii=False,
                    )
                )
            ]
        )
