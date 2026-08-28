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
