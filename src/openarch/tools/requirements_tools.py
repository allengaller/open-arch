"""需求结构化工具：把对话中提炼的需求整理为结构化需求卡。"""

from __future__ import annotations

import json
from typing import ClassVar

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
        return [
            f
            for f in (
                "scale",
                "availability_target",
                "budget_range",
                "compliance",
                "existing_systems",
            )
            if getattr(self, f) is None
        ]


class StructureRequirementsTool(OpenArchTool):
    name = "structure_requirements"
    description = (
        "把从对话中提炼的需求整理为结构化需求卡。business_scenario 必填；"
        "其余字段未从用户处获得时不要编造，留空并用 missing_fields 主动追问。"
    )
    input_schema: ClassVar[dict] = {
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
