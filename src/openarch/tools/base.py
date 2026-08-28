"""OpenArch 工具公共基类：权限一律 ALLOW（MVP 本地单用户场景）。"""

from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import ToolBase


class OpenArchTool(ToolBase):
    """OpenArch 能力工具基类：权限一律 ALLOW（MVP 本地单用户场景）。

    需要 ASK/DENY 的工具应覆写 check_permissions（权限引擎按实例分派）。
    """

    async def check_permissions(
        self, tool_input: dict, context: PermissionContext
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW, message="OpenArch local tool"
        )
