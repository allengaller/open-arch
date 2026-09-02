from __future__ import annotations

import logging
from pathlib import Path

from agentscope.app import create_app
from agentscope.app.message_bus import InMemoryMessageBus
from agentscope.app.workspace_manager import LocalWorkspaceManager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from openarch.config import Settings
from openarch.web.bootstrap import make_storage
from openarch.web.tools_factory import make_openarch_tools

logger = logging.getLogger(__name__)

# 候选顺序：包内（Docker 构建产物）优先，仓库内（本地 npm run build）兜底。
_STATIC_CANDIDATES = (
    Path(__file__).parent / "static" / "dist",
    Path(__file__).parents[3] / "webui" / "dist",
)
_GTM_CANDIDATES = (
    Path(__file__).parent / "static" / "gtm",
    Path(__file__).parents[3] / "GTM",
)


def find_static_dir() -> Path | None:
    for candidate in _STATIC_CANDIDATES:
        if (candidate / "index.html").is_file():
            return candidate
    return None


def find_gtm_dir() -> Path | None:
    for candidate in _GTM_CANDIDATES:
        if (candidate / "index.html").is_file():
            return candidate
    return None


def create_web_app(settings: Settings) -> FastAPI:
    """装配 AgentScope Agent Service 并叠加 OpenArch 私有端点与静态托管。"""
    workspace_manager = LocalWorkspaceManager(
        basedir=str(settings.workspace_root),
        skill_paths=[str(settings.skills_dir)],
    )
    app = create_app(
        storage=make_storage(settings),
        message_bus=InMemoryMessageBus(),
        workspace_manager=workspace_manager,
        extra_agent_tools=make_openarch_tools(settings, workspace_manager),
        title="OpenArch",
    )

    @app.get("/openarch/config")
    def openarch_config() -> dict:
        """前端启动引导所需的服务端配置（不含任何密钥）。"""
        return {"model": settings.model}

    # /gtm 必须先于根挂载注册：Mount("/") 按注册顺序捕获所有路径，
    # 顺序颠倒会让 /gtm/ 落进 webui dist 而返回 404。
    gtm_dir = find_gtm_dir()
    if gtm_dir is None:
        logger.warning(
            "未找到 GTM 营销页（仓库 GTM/ 或包内 static/gtm），"
            "webui「返回项目主页 → /gtm/」入口将不可用。"
        )
    else:
        app.mount(
            "/gtm",
            StaticFiles(directory=gtm_dir, html=True),
            name="gtm",
        )

    static_dir = find_static_dir()
    if static_dir is None:
        logger.warning(
            "未找到 webui 静态产物（webui/dist 或包内 static/dist），静态托管已禁用；"
            "请执行 `npm run build`（见 webui/README）。"
        )
    else:
        app.mount(
            "/",
            StaticFiles(directory=static_dir, html=True),
            name="webui",
        )
    return app
