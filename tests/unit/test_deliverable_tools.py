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
