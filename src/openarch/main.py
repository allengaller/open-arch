from __future__ import annotations

import argparse
import asyncio
import sys

from agentscope.console import launch_console
from dotenv import load_dotenv

from openarch.agent import build_agent
from openarch.config import ConfigError, Settings, load_settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="openarch",
        description="面向 Solutions Architect 的开箱即用工具箱与架构设计 Copilot",
    )
    sub = parser.add_subparsers(dest="command")
    web = sub.add_parser("web", help="启动浏览器 Web UI（AgentScope Agent Service）")
    web.add_argument("--host", default=None, help="监听地址（默认取 OPENARCH_HOST 或 127.0.0.1）")
    web.add_argument("--port", type=int, default=None, help="监听端口（默认取 OPENARCH_PORT 或 8000）")
    return parser.parse_args(argv)


def _run_web(settings: Settings, host: str | None, port: int | None) -> None:
    import uvicorn

    from openarch.web.app import create_web_app, find_static_dir
    from openarch.web.bootstrap import run_bootstrap

    # 显式传 0（uvicorn 随机端口）等合法 falsy 值不应被吞掉回落 settings。
    host = host if host is not None else settings.web_host
    port = port if port is not None else settings.web_port
    asyncio.run(run_bootstrap(settings))
    if find_static_dir() is None:
        print(
            "提示：未找到前端构建产物（webui/dist），本次仅提供 API。"
            "构建方法见 README「Web UI」一节。",
            file=sys.stderr,
        )
    print(f"OpenArch Web 就绪：http://{host}:{port}（模型：{settings.model}）")
    uvicorn.run(create_web_app(settings), host=host, port=port)


def main() -> None:
    load_dotenv()
    args = parse_args()
    try:
        settings = load_settings()
    except ConfigError as e:
        print(f"配置错误：{e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "web":
        _run_web(settings, host=args.host, port=args.port)
        return

    print(f"OpenArch 就绪（模型：{settings.model}，技能目录：{settings.skills_dir}）")
    asyncio.run(launch_console(build_agent(settings)))


if __name__ == "__main__":
    main()
