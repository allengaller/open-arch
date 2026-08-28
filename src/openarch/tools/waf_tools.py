"""WAF 评审工具：阿里云 Well-Architected 五支柱清单校验与评分。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

import yaml
from agentscope.message import TextBlock
from agentscope.tool import ToolChunk

from openarch.tools.base import OpenArchTool

_VALID_STATUS = {"pass", "risk", "fail"}
_WEIGHT = {"pass": 1.0, "risk": 0.5, "fail": 0.0}
_SEVERITY = {"fail": 0, "risk": 1}  # 高风险清单按严重程度排序：fail 在前，risk 在后


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
    input_schema: ClassVar[dict] = {
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
                            "evidence": f.get("evidence", ""),
                            "recommendation": f.get("recommendation", ""),
                        }
                    )
        high_risks.sort(key=lambda r: _SEVERITY[r["status"]])
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
