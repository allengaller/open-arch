import json
import tempfile
from pathlib import Path

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
    path = tmp_path / out["file"]
    assert path.exists()
    assert "<mxGraphModel" in path.read_text(encoding="utf-8")


async def test_export_drawio_rejects_invalid(tmp_path):
    tool = ExportDrawioTool(workspace=tmp_path)
    out = json.loads(
        (await tool(mermaid_code="web -->\n", title="x")).content[0].text
    )
    assert "error" in out
    assert not (tmp_path / "diagrams").exists()


async def test_tools_register_into_real_toolkit():
    from agentscope.tool import Toolkit

    toolkit = Toolkit(
        tools=[ValidateDiagramTool(), ExportDrawioTool(workspace=Path(tempfile.mkdtemp()))]
    )
    assert toolkit  # 注册不抛异常即契约成立
