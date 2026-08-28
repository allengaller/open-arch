from __future__ import annotations

import asyncio

from agentscope.console import launch_console

from openarch.agent import build_agent
from openarch.config import load_settings


def main() -> None:
    settings = load_settings()
    agent = build_agent(settings)
    print(f"OpenArch 就绪（模型：{settings.model}，技能目录：{settings.skills_dir}）")
    asyncio.run(launch_console(agent))


if __name__ == "__main__":
    main()
