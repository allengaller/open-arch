from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MODEL = "qwen-max"


class ConfigError(RuntimeError):
    """环境变量配置错误（启动即失败，错误信息直接可操作）。"""


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str | None
    openai_api_key: str | None
    base_url: str | None
    model: str
    workspace: Path
    skills_dir: Path


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

    return Settings(
        dashscope_api_key=dashscope_key,
        openai_api_key=openai_key,
        base_url=base_url,
        model=e.get("OPENARCH_MODEL") or _DEFAULT_MODEL,
        workspace=workspace,
        skills_dir=skills_dir,
    )
