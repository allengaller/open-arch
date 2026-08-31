from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path

from agentscope.app.workspace_manager import WorkspaceManagerBase
from agentscope.tool import ToolBase

from openarch.config import Settings
from openarch.tools.deliverable_tools import ExportDeliverableTool
from openarch.tools.diagram_tools import ExportDrawioTool, ValidateDiagramTool
from openarch.tools.requirements_tools import StructureRequirementsTool
from openarch.tools.waf_tools import ReviewWithWafTool


def make_openarch_tools(
    settings: Settings,
    workspace_manager: WorkspaceManagerBase,
) -> Callable[[str, str, str], Awaitable[list[ToolBase]]]:
    """构造 extra_agent_tools 工厂：五件套工具绑定当前会话工作区。

    PER_AGENT 隔离下 workdir = basedir/<agent_id>，与该 agent 全部会话
    共享，因此交付物落盘位置确定且持久（TTL 驱逐不删目录）。
    """

    async def factory(
        user_id: str, agent_id: str, session_id: str
    ) -> list[ToolBase]:
        workspace = await workspace_manager.get_workspace(
            user_id, agent_id, session_id
        )
        workdir = Path(workspace.workdir)
        return [
            StructureRequirementsTool(),
            ValidateDiagramTool(),
            ExportDrawioTool(workdir),
            ReviewWithWafTool(settings.skills_dir / "aliyun-waf" / "checklist.yaml"),
            ExportDeliverableTool(workdir),
        ]

    return factory
