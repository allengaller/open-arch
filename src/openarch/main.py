from __future__ import annotations

import asyncio
import sys

from agentscope.console import launch_console
from dotenv import load_dotenv

from openarch.agent import build_agent
from openarch.config import ConfigError, load_settings


def main() -> None:
    load_dotenv()
    try:
        settings = load_settings()
        agent = build_agent(settings)
    except ConfigError as e:
        print(f"配置错误：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"OpenArch 就绪（模型：{settings.model}，技能目录：{settings.skills_dir}）")
    asyncio.run(launch_console(agent))


if __name__ == "__main__":
    main()
