from pathlib import Path

from agentscope.app.workspace_manager import LocalWorkspaceManager

from openarch.config import load_settings
from openarch.web.tools_factory import make_openarch_tools


async def test_factory_binds_session_workdir(tmp_path):
    settings = load_settings(
        env={"DASHSCOPE_API_KEY": "k", "OPENARCH_DB": str(tmp_path / "db.sqlite")}
    )
    manager = LocalWorkspaceManager(basedir=str(tmp_path / "ws"))
    factory = make_openarch_tools(settings, manager)

    tools = await factory("local", "agent-1", "sess-1")

    names = [t.name for t in tools]
    assert names == [
        "structure_requirements",
        "validate_diagram",
        "export_drawio",
        "review_with_waf",
        "export_deliverable",
    ]
    workdir = Path(tmp_path / "ws" / "agent-1")
    drawio = next(t for t in tools if t.name == "export_drawio")
    deliverable = next(t for t in tools if t.name == "export_deliverable")
    assert drawio._workspace == workdir
    assert deliverable._workspace == workdir
    waf = next(t for t in tools if t.name == "review_with_waf")
    assert waf._checklist_path == settings.skills_dir / "aliyun-waf" / "checklist.yaml"
