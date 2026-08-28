"""OpenArch 工具公共基类：权限一律 ALLOW（MVP 本地单用户场景）。"""

from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import ToolBase


class OpenArchTool(ToolBase):
    """OpenArch 能力工具基类：权限一律 ALLOW（MVP 本地单用户场景）。"""

    async def check_permissions(
        self, tool_input: dict, context: PermissionContext
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW, message="OpenArch local tool"
        )
