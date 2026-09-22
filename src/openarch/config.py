from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from pydantic import SecretStr

_DEFAULT_MODEL = "qwen-max"


class ConfigError(RuntimeError):
    """环境变量配置错误（启动即失败，错误信息直接可操作）。"""


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: SecretStr | None
    openai_api_key: SecretStr | None
    base_url: str | None
    model: str
    workspace: Path
    skills_dir: Path
    db: Path = Path("./data/openarch.db")
    web_host: str = "127.0.0.1"
    web_port: int = 8000

    @property
    def workspace_root(self) -> Path:
        """Web 模式下 AgentScope 服务工作区根（<DB 所在目录>/workspaces）。"""
        return self.db.parent / "workspaces"


def load_settings(env: dict[str, str] | None = None) -> Settings:
    e = dict(os.environ) if env is None else env

    base_url = e.get("OPENARCH_BASE_URL") or None
    dashscope_key = e.get("DASHSCOPE_API_KEY") or None
    openai_key = e.get("OPENARCH_API_KEY") or None

    if base_url and not openai_key:
        raise ConfigError(
            "设置了 OPENARCH_BASE_URL 但缺少 OPENARCH_API_KEY。"
            "请在 .env 中填写 OPENARCH_API_KEY（见 README「配置」一节）。"
        )
    if not base_url and not dashscope_key:
        raise ConfigError(
            "缺少 DASHSCOPE_API_KEY。请执行 `cp .env.example .env` 并填写"
            " DASHSCOPE_API_KEY（见 README「配置」一节）。"
        )

    workspace = Path(e.get("OPENARCH_WORKSPACE") or "./deliverables").expanduser().resolve()
    default_skills = Path(__file__).resolve().parents[2] / "skills"
    skills_dir = Path(e.get("OPENARCH_SKILLS_DIR") or default_skills).expanduser().resolve()

    db = Path(e.get("OPENARCH_DB") or "./data/openarch.db").expanduser().resolve()
    db.parent.mkdir(parents=True, exist_ok=True)
    web_port_raw = e.get("OPENARCH_PORT")
    try:
        web_port = int(web_port_raw) if web_port_raw else 8000
    except ValueError:
        raise ConfigError(
            f"OPENARCH_PORT 不是合法整数：{web_port_raw!r}。"
            "请改为数字端口（如 8000），或删除该变量使用默认值。"
        ) from None
    if not 0 <= web_port <= 65535:
        raise ConfigError(
            f"OPENARCH_PORT 超出合法范围 0-65535：{web_port_raw!r}。"
            "请改为数字端口（如 8000）。"
        )

    return Settings(
        dashscope_api_key=SecretStr(dashscope_key) if dashscope_key else None,
        openai_api_key=SecretStr(openai_key) if openai_key else None,
        base_url=base_url,
        model=e.get("OPENARCH_MODEL") or _DEFAULT_MODEL,
        workspace=workspace,
        skills_dir=skills_dir,
        db=db,
        web_host=e.get("OPENARCH_HOST") or "127.0.0.1",
        web_port=web_port,
    )
