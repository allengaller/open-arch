from __future__ import annotations

import logging
from pathlib import Path

import yaml
from agentscope.app import create_app
from agentscope.app.message_bus import InMemoryMessageBus
from agentscope.app.workspace_manager import LocalWorkspaceManager
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles

from openarch.config import Settings
from openarch.web.bootstrap import make_storage
from openarch.web.tools_factory import make_openarch_tools

logger = logging.getLogger(__name__)

# 知识库只读端点允许的文本后缀（Markdown 知识 + 机读清单）。
_SKILL_TEXT_SUFFIXES = {".md", ".yaml", ".yml"}

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


def _skill_meta(skill_dir: Path) -> dict | None:
    """读取技能包元信息：frontmatter 描述 + 白名单后缀的知识文件相对路径。"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    try:
        meta = yaml.safe_load(skill_md.read_text(encoding="utf-8").split("---")[1]) or {}
    except (IndexError, yaml.YAMLError):
        meta = {}
    files = sorted(
        str(p.relative_to(skill_dir))
        for p in skill_dir.rglob("*")
        if p.is_file() and p.suffix in _SKILL_TEXT_SUFFIXES
    )
    return {"name": skill_dir.name, "description": str(meta.get("description", "")), "files": files}


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

    @app.get("/openarch/skills")
    def list_skills() -> dict:
        """技能包清单（Web UI 知识库导航用），只暴露文本知识文件。"""
        packs = []
        if settings.skills_dir.is_dir():
            for d in sorted(settings.skills_dir.iterdir()):
                meta = _skill_meta(d)
                if meta:
                    packs.append(meta)
        return {"skills": packs}

    @app.get("/openarch/skills/{skill_name}/{file_path:path}")
    def read_skill_file(skill_name: str, file_path: str):
        """读取技能包内单个知识文件；解析后必须仍位于技能目录内（防路径穿越）。"""
        base = (settings.skills_dir / skill_name).resolve()
        if base.parent != settings.skills_dir.resolve():
            raise HTTPException(status_code=404, detail="技能包不存在")
        target = (base / file_path).resolve()
        if (
            target.suffix not in _SKILL_TEXT_SUFFIXES
            or settings.skills_dir.resolve() not in target.parents
            or not target.is_file()
        ):
            raise HTTPException(status_code=404, detail="知识文件不存在")
        return Response(target.read_text(encoding="utf-8"), media_type="text/markdown; charset=utf-8")

    # /gtm 必须先于根挂载注册：Mount("/") 按注册顺序捕获所有路径，
    # 顺序颠倒会让 /gtm/ 落进 webui dist 而返回 404。
    gtm_dir = find_gtm_dir()
    if gtm_dir is None:
        logger.warning(
            "未找到 GTM 营销页（仓库 GTM/ 或包内 static/gtm），"
            "webui「返回项目主页 → /gtm/index.html」入口将不可用。"
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
