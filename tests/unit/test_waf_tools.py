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
    assert out["pillar_scores"]["可靠性"]["score"] == 0.7  # (3 + 0.5) / 5
    assert out["pillar_scores"]["可靠性"]["total"] == 5
    assert {"item_id": "REL-03", "status": "fail"}.items() <= out["high_risks"][0].items()
    assert {"item_id": "REL-02", "status": "risk"}.items() <= out["high_risks"][1].items()


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


async def test_all_pass_gives_full_scores_and_no_risks():
    tool = ReviewWithWafTool(checklist_path=CHECKLIST)
    findings = [
        {"item_id": it["id"], "status": "pass", "evidence": "覆盖"}
        for items in load_checklist(CHECKLIST).values()
        for it in items
    ]
    out = json.loads(
        (await tool(architecture_summary="x", findings=findings)).content[0].text
    )
    assert all(s["score"] == 1.0 for s in out["pillar_scores"].values())
    assert out["high_risks"] == []


async def test_missing_checklist_returns_structured_error():
    tool = ReviewWithWafTool(checklist_path=Path("/nonexistent/checklist.yaml"))
    out = json.loads(
        (
            await tool(architecture_summary="x", findings=_all_findings())
        ).content[0].text
    )
    assert "error" in out
    assert "WAF 清单未找到" in out["error"][0]
