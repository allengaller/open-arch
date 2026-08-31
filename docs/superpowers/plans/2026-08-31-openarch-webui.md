# OpenArch Phase 2 · Web UI 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 OpenArch 增加浏览器 Web UI——`openarch web` 单进程启动 AgentScope Agent Service（FastAPI + SQLite + SSE），前端三区 SPA（会话侧栏 / 聊天主区 / 交付物面板）。

**Architecture:** 后端 100% 复用 AgentScope `create_app`（存储 `AsyncSQLAlchemyStorage(sqlite+aiosqlite)`、总线 `InMemoryMessageBus`、工作区 `LocalWorkspaceManager`），OpenArch 五件套工具经 `extra_agent_tools` 工厂注入并把交付物写进会话工作区，技能包经 `skill_paths` 原生种入。bootstrap 在 uvicorn 启动前幂等种子凭证与 agent 记录。前端 Vite+React+TS，fetch 式 SSE 消费（带 X-User-ID 头），mermaid 渲染，宽容解析未知事件。

**Tech Stack:** agentscope 2.0.7.post1（extras: `service`、`storage-sql`）、aiosqlite、FastAPI/uvicorn（随 extra）、Vite + React 18 + TypeScript + npm、mermaid、marked + dompurify、vitest。

**规格文档：** `docs/superpowers/specs/2026-08-31-openarch-webui-design.md`

---

## 环境注意事项（每个任务都适用）

- 包管理：Python 侧一律 `uv run ...`；前端在 `webui/` 内用 `npm`。
- **已知环境坑**：后台进程会给 `.venv/lib/python3.12/site-packages/*.pth` 重新打 `UF_HIDDEN` 标志，导致 `uv run python` 报 `ModuleNotFoundError: No module named 'openarch'`。遇到就执行 `chflags nohidden .venv/lib/python3.12/site-packages/*.pth` 再重试；pytest 不受影响（`pythonpath=["src"]`）。
- 测试命令：`uv run pytest -m "not e2e" -q`（全部单元）或指定文件。提交前确保 ruff 干净：`uv run ruff check src tests`。
- 前端测试：`cd webui && npm test`；构建：`npm run build`。

---

### Task 1: 配置扩展（OPENARCH_DB / OPENARCH_HOST / OPENARCH_PORT）

**Files:**
- Modify: `src/openarch/config.py`
- Test: `tests/unit/test_web_config.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/unit/test_web_config.py`：

```python
from pathlib import Path

from openarch.config import load_settings


def test_web_defaults():
    s = load_settings(env={"DASHSCOPE_API_KEY": "k"})
    assert s.web_host == "127.0.0.1"
    assert s.web_port == 8000
    assert s.db == Path("./data/openarch.db").resolve()
    assert s.workspace_root == s.db.parent / "workspaces"


def test_web_env_overrides(tmp_path):
    env = {
        "DASHSCOPE_API_KEY": "k",
        "OPENARCH_DB": str(tmp_path / "o.db"),
        "OPENARCH_HOST": "0.0.0.0",
        "OPENARCH_PORT": "9000",
    }
    s = load_settings(env=env)
    assert s.web_host == "0.0.0.0"
    assert s.web_port == 9000
    assert s.db == tmp_path / "o.db"
    assert s.workspace_root == (tmp_path / "o.db").parent / "workspaces"
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_web_config.py -q`
Expected: FAIL — `Settings` 无 `db/web_host/web_port` 属性（`AttributeError`）。

- [ ] **Step 3: 实现**

`src/openarch/config.py`：`Settings` 追加三个带默认值字段与一个派生属性（放在现有字段之后）：

```python
@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str | None
    openai_api_key: str | None
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
```

`load_settings` 在 return 前追加：

```python
    db = Path(e.get("OPENARCH_DB") or "./data/openarch.db").expanduser().resolve()
    web_port_raw = e.get("OPENARCH_PORT")
```

并把 return 改为：

```python
    return Settings(
        dashscope_api_key=dashscope_key,
        openai_api_key=openai_key,
        base_url=base_url,
        model=e.get("OPENARCH_MODEL") or _DEFAULT_MODEL,
        workspace=workspace,
        skills_dir=skills_dir,
        db=db,
        web_host=e.get("OPENARCH_HOST") or "127.0.0.1",
        web_port=int(web_port_raw) if web_port_raw else 8000,
    )
```

- [ ] **Step 4: 运行确认通过（含既有配置测试回归）**

Run: `uv run pytest tests/unit/test_web_config.py tests/unit/test_config.py -q`
Expected: 全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add src/openarch/config.py tests/unit/test_web_config.py
git commit -m "feat(config): 新增 OPENARCH_DB/HOST/PORT 与 Web 工作区根派生"
```

---

### Task 2: 依赖切换到官方 extras

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`（由 uv 生成）

- [ ] **Step 1: 修改 pyproject 依赖**

`pyproject.toml` 的 `dependencies` 从：

```toml
dependencies = [
    "agentscope>=2.0",
    "pydantic>=2.7",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
]
```

改为：

```toml
dependencies = [
    "agentscope[service,storage-sql]>=2.0",
    "aiosqlite>=0.20",
    "pydantic>=2.7",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
]
```

- [ ] **Step 2: 同步并验证导入**

Run:
```bash
uv sync
uv run python -c "from agentscope.app import create_app; from agentscope.app.storage import AsyncSQLAlchemyStorage; from agentscope.app.message_bus import InMemoryMessageBus; from agentscope.app.workspace_manager import LocalWorkspaceManager; import fastapi, uvicorn, aiosqlite; print('ok')"
```
Expected: 输出 `ok`（fastapi/uvicorn/apscheduler/ag-ui-protocol/sqlalchemy/alembic/aiosqlite 均随 extras 装入）。

- [ ] **Step 3: 全量测试回归**

Run: `uv run pytest -m "not e2e" -q`
Expected: 全部 PASS（既有 37 个测试不受影响）。

- [ ] **Step 4: 提交**

```bash
git add pyproject.toml uv.lock
git commit -m "build: 切到 agentscope[service,storage-sql] extras + aiosqlite"
```

---

### Task 3: bootstrap 幂等种子模块

**Files:**
- Create: `src/openarch/web/__init__.py`（空文件）
- Create: `src/openarch/web/bootstrap.py`
- Test: `tests/unit/test_web_bootstrap.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/unit/test_web_bootstrap.py`：

```python
from openarch.agent import SYSTEM_PROMPT
from openarch.config import load_settings
from openarch.web.bootstrap import run_bootstrap


def _settings(tmp_path):
    return load_settings(
        env={"DASHSCOPE_API_KEY": "sk-test", "OPENARCH_DB": str(tmp_path / "t.db")}
    )


async def test_bootstrap_idempotent(tmp_path):
    s = _settings(tmp_path)
    info1 = await run_bootstrap(s)
    info2 = await run_bootstrap(s)
    assert info1 == info2
    assert info1.agent_id
    assert info1.credential_id


async def test_bootstrap_seeds_agent_and_credential(tmp_path):
    from agentscope.app.storage import AsyncSQLAlchemyStorage

    s = _settings(tmp_path)
    await run_bootstrap(s)
    storage = AsyncSQLAlchemyStorage(f"sqlite+aiosqlite:///{s.db}")
    async with storage:
        agents = await storage.list_agents("local")
        creds = await storage.list_credentials("local")
    assert len(agents) == 1
    assert agents[0].data.name == "OpenArch"
    assert agents[0].data.system_prompt == SYSTEM_PROMPT
    assert len(creds) == 1
    assert creds[0].data.type == "dashscope_credential"


async def test_bootstrap_openai_compat_mode(tmp_path):
    s = load_settings(
        env={
            "OPENARCH_BASE_URL": "https://api.example.com/v1",
            "OPENARCH_API_KEY": "key-1",
            "OPENARCH_DB": str(tmp_path / "c.db"),
        }
    )
    info = await run_bootstrap(s)
    from agentscope.app.storage import AsyncSQLAlchemyStorage

    storage = AsyncSQLAlchemyStorage(f"sqlite+aiosqlite:///{s.db}")
    async with storage:
        creds = await storage.list_credentials("local")
    assert len(creds) == 1
    assert creds[0].data.type == "openai_credential"
    assert info.credential_id == creds[0].id
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_web_bootstrap.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'openarch.web'`。

- [ ] **Step 3: 实现**

创建 `src/openarch/web/__init__.py`（空文件）。
创建 `src/openarch/web/bootstrap.py`：

```python
from __future__ import annotations

from dataclasses import dataclass

from agentscope.agent import ContextConfig, ReActConfig
from agentscope.app.storage import AsyncSQLAlchemyStorage
from agentscope.app.storage._model import AgentData, AgentRecord
from agentscope.credential import CredentialBase, CredentialFactory, DashScopeCredential, OpenAICredential
from pydantic import SecretStr

from openarch.agent import SYSTEM_PROMPT
from openarch.config import Settings

USER_ID = "local"
_AGENT_NAME = "OpenArch"


@dataclass(frozen=True)
class BootstrapInfo:
    agent_id: str
    credential_id: str


async def run_bootstrap(settings: Settings) -> BootstrapInfo:
    """幂等种子：凭证（按模式二选一）+ OpenArch agent 记录。

    在 uvicorn 启动前独立调用（不经 create_app 的 lifespan），
    因此这里自开一个短生命周期的 storage 连接。
    """
    storage = AsyncSQLAlchemyStorage(
        f"sqlite+aiosqlite:///{settings.db}", create_tables=True
    )
    async with storage:
        credential_id = await _seed_credential(storage, settings)
        agent_id = await _seed_agent(storage)
    return BootstrapInfo(agent_id=agent_id, credential_id=credential_id)


async def _seed_credential(storage: AsyncSQLAlchemyStorage, settings: Settings) -> str:
    if settings.base_url:
        credential: CredentialBase = OpenAICredential(
            api_key=SecretStr(settings.openai_api_key or ""),
            base_url=settings.base_url,
        )
    else:
        credential = DashScopeCredential(
            api_key=SecretStr(settings.dashscope_api_key or "")
        )
    for record in await storage.list_credentials(USER_ID):
        if record.data.type == credential.type:
            return record.id
    return await storage.upsert_credential(USER_ID, credential)


async def _seed_agent(storage: AsyncSQLAlchemyStorage) -> str:
    for record in await storage.list_agents(USER_ID):
        if record.data.name == _AGENT_NAME:
            return record.id
    record = AgentRecord(
        user_id=USER_ID,
        data=AgentData(
            name=_AGENT_NAME,
            system_prompt=SYSTEM_PROMPT,
            context_config=ContextConfig(),
            react_config=ReActConfig(),
        ),
    )
    return await storage.upsert_agent(USER_ID, record)
```

注意：`CredentialBase`/`DashScopeCredential`/`OpenAICredential` 从 `agentscope.credential` 导入；`CredentialFactory` 仅为类型参考可不导入——保持上面 import 干净，ruff 会揪出未用导入，直接删掉 `CredentialFactory` 一行。

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_web_bootstrap.py -q`
Expected: 3 PASS。若报 `ImportError: cannot import name 'ContextConfig' from 'agentscope.agent'`，改为 `from agentscope.agent._config import ContextConfig, ReActConfig` 并同步修正。

- [ ] **Step 5: 全量回归 + 提交**

```bash
uv run pytest -m "not e2e" -q
git add src/openarch/web/__init__.py src/openarch/web/bootstrap.py tests/unit/test_web_bootstrap.py
git commit -m "feat(web): bootstrap 幂等种子凭证与 agent 记录"
```

---

### Task 4: OpenArch 工具工厂（会话工作区感知）

**Files:**
- Create: `src/openarch/web/tools_factory.py`
- Test: `tests/unit/test_web_tools_factory.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/unit/test_web_tools_factory.py`：

```python
from pathlib import Path

from agentscope.app.workspace_manager import LocalWorkspaceManager

from openarch.config import load_settings
from openarch.web.tools_factory import make_openarch_tools


async def test_factory_binds_session_workdir(tmp_path):
    settings = load_settings(
        env={"DASHSCOPE_API_KEY": "k", "OPENARCH_DB": str(tmp_path / "db.sqlite")}
    )
    manager = LocalWorkspaceManager(basedir=str(tmp_path / "ws"))
    factory = make_openarch_tools(settings, manager)

    tools = await factory("local", "agent-1", "sess-1")

    names = [t.name for t in tools]
    assert names == [
        "structure_requirements",
        "validate_diagram",
        "export_drawio",
        "review_with_waf",
        "export_deliverable",
    ]
    workdir = Path(tmp_path / "ws" / "agent-1")
    drawio = next(t for t in tools if t.name == "export_drawio")
    deliverable = next(t for t in tools if t.name == "export_deliverable")
    assert drawio._workspace == workdir
    assert deliverable._workspace == workdir
    waf = next(t for t in tools if t.name == "review_with_waf")
    assert waf._checklist_path == settings.skills_dir / "aliyun-waf" / "checklist.yaml"
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_web_tools_factory.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'openarch.web.tools_factory'`。

- [ ] **Step 3: 实现**

创建 `src/openarch/web/tools_factory.py`：

```python
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
```

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_web_tools_factory.py -q`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add src/openarch/web/tools_factory.py tests/unit/test_web_tools_factory.py
git commit -m "feat(web): extra_agent_tools 工厂把五件套工具绑到会话工作区"
```

---

### Task 5: create_web_app（装配 + /openarch/config + 静态挂载）

**Files:**
- Create: `src/openarch/web/app.py`
- Test: `tests/unit/test_web_app.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/unit/test_web_app.py`：

```python
from fastapi.testclient import TestClient

from openarch.config import load_settings
from openarch.web.app import create_web_app


def _settings(tmp_path):
    return load_settings(
        env={"DASHSCOPE_API_KEY": "sk-test", "OPENARCH_DB": str(tmp_path / "app.db")}
    )


def test_health_and_openarch_config(tmp_path):
    app = create_web_app(_settings(tmp_path))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        r = client.get("/openarch/config")
        assert r.status_code == 200
        assert r.json() == {"model": "qwen-max"}


def test_static_mount_when_dist_exists(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>openarch-ok</html>")
    monkeypatch.setattr("openarch.web.app.find_static_dir", lambda: dist)

    app = create_web_app(_settings(tmp_path))
    with TestClient(app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "openarch-ok" in resp.text
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_web_app.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'openarch.web.app'`。

- [ ] **Step 3: 实现**

创建 `src/openarch/web/app.py`：

```python
from __future__ import annotations

from pathlib import Path

from agentscope.app import create_app
from agentscope.app.message_bus import InMemoryMessageBus
from agentscope.app.storage import AsyncSQLAlchemyStorage
from agentscope.app.workspace_manager import LocalWorkspaceManager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from openarch.config import Settings
from openarch.web.tools_factory import make_openarch_tools

# 候选顺序：包内（Docker 构建产物）优先，仓库内（本地 npm run build）兜底。
_STATIC_CANDIDATES = (
    Path(__file__).parent / "static" / "dist",
    Path(__file__).parents[3] / "webui" / "dist",
)


def find_static_dir() -> Path | None:
    for candidate in _STATIC_CANDIDATES:
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
        storage=AsyncSQLAlchemyStorage(
            f"sqlite+aiosqlite:///{settings.db}",
            create_tables=True,
        ),
        message_bus=InMemoryMessageBus(),
        workspace_manager=workspace_manager,
        extra_agent_tools=make_openarch_tools(settings, workspace_manager),
        title="OpenArch",
    )

    @app.get("/openarch/config")
    def openarch_config() -> dict:
        """前端启动引导所需的服务端配置（不含任何密钥）。"""
        return {"model": settings.model}

    static_dir = find_static_dir()
    if static_dir is not None:
        app.mount(
            "/",
            StaticFiles(directory=static_dir, html=True),
            name="webui",
        )
    return app
```

要点：`app.mount("/")` 必须在 `create_app` 注册完全部路由之后调用（Starlette 按注册顺序匹配，先注册的 API 路由优先于 catch-all 静态挂载）。

- [ ] **Step 4: 运行确认通过**

Run: `uv run pytest tests/unit/test_web_app.py -q`
Expected: 2 PASS。（`find_static_dir` 会探测仓库根 `webui/dist`——本地未构建前端时返回 None，不影响测试。）

- [ ] **Step 5: 提交**

```bash
git add src/openarch/web/app.py tests/unit/test_web_app.py
git commit -m "feat(web): create_web_app 装配 Agent Service + /openarch/config + 静态托管"
```

---

### Task 6: CLI 子命令 `openarch web`

**Files:**
- Modify: `src/openarch/main.py`
- Test: `tests/unit/test_web_cli.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/unit/test_web_cli.py`：

```python
from openarch.main import parse_args


def test_parse_args_default_is_console():
    args = parse_args([])
    assert args.command is None


def test_parse_args_web_with_overrides():
    args = parse_args(["web", "--host", "0.0.0.0", "--port", "9000"])
    assert args.command == "web"
    assert args.host == "0.0.0.0"
    assert args.port == 9000


def test_parse_args_web_defaults():
    args = parse_args(["web"])
    assert args.command == "web"
    assert args.host is None
    assert args.port is None
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest tests/unit/test_web_cli.py -q`
Expected: FAIL — `ImportError: cannot import name 'parse_args'`。

- [ ] **Step 3: 实现**

重写 `src/openarch/main.py`：

```python
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

    host = host or settings.web_host
    port = port or settings.web_port
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
```

- [ ] **Step 4: 运行确认通过 + CLI 冒烟**

Run:
```bash
uv run pytest tests/unit/test_web_cli.py tests/unit/test_main.py -q
uv run openarch web --help
```
Expected: 测试全 PASS；`--help` 输出含 `--host/--port`。（`tests/unit/test_main.py` 若不存在则跳过该路径。）

- [ ] **Step 5: 提交**

```bash
git add src/openarch/main.py tests/unit/test_web_cli.py
git commit -m "feat(cli): openarch web 子命令（bootstrap → uvicorn）"
```

---

### Task 7: e2e Web 冒烟测试（需真实 Key，手动跑）

**Files:**
- Create: `tests/e2e/test_web_smoke.py`

- [ ] **Step 1: 写 e2e 测试（默认跳过）**

创建 `tests/e2e/test_web_smoke.py`：

```python
import asyncio
import os

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.skipif(
    not os.environ.get("DASHSCOPE_API_KEY"),
    reason="需要真实 DASHSCOPE_API_KEY",
)
async def test_web_copilot_roundtrip(tmp_path):
    from fastapi.testclient import TestClient

    from openarch.config import load_settings
    from openarch.web.app import create_web_app
    from openarch.web.bootstrap import run_bootstrap

    env = dict(os.environ)
    env["OPENARCH_DB"] = str(tmp_path / "e2e.db")
    settings = load_settings(env=env)
    info = await run_bootstrap(settings)

    app = create_web_app(settings)
    headers = {"X-User-ID": "local"}
    with TestClient(app) as client:
        r = client.post(
            "/sessions",
            json={
                "agent_id": info.agent_id,
                "chat_model_config": {
                    "type": "chat",
                    "credential_id": info.credential_id,
                    "model": settings.model,
                    "parameters": {},
                },
            },
            headers=headers,
        )
        assert r.status_code == 201, r.text
        session_id = r.json()["session_id"]

        r = client.post(
            "/chat/",
            json={
                "agent_id": info.agent_id,
                "session_id": session_id,
                "input": {
                    "role": "user",
                    "name": "user",
                    "content": [
                        {"type": "text", "text": "用一句话介绍你能帮我做什么"}
                    ],
                },
            },
            headers=headers,
        )
        assert r.status_code == 200, r.text

        for _ in range(60):
            await asyncio.sleep(2)
            m = client.get(
                f"/sessions/{session_id}/messages?agent_id={info.agent_id}",
                headers=headers,
            )
            if any(
                msg.get("role") == "assistant" for msg in m.json()["messages"]
            ):
                break
        else:
            pytest.fail("120 秒内未收到助手回复")
```

- [ ] **Step 2: 验证无 Key 时跳过 + 单测回归**

Run:
```bash
env -u DASHSCOPE_API_KEY uv run pytest tests/e2e/test_web_smoke.py -q
uv run pytest -m "not e2e" -q
```
Expected: 第一个命令 `1 skipped`；第二个全 PASS。

- [ ] **Step 3: 提交**

```bash
git add tests/e2e/test_web_smoke.py
git commit -m "test(e2e): Web 模式 Copilot 冒烟（真实 Key）"
```

---

### Task 8: webui 脚手架

**Files:**
- Create: `webui/`（Vite react-ts 模板 + 依赖）
- Create: `webui/vite.config.ts`（重写）
- Create: `webui/.gitignore`
- Modify: 根 `.gitignore`（追加 `webui/dist/`）

- [ ] **Step 1: 脚手架 + 依赖**

Run:
```bash
npm create vite@latest webui -- --template react-ts
cd webui && npm install && npm install mermaid marked dompurify && npm install -D vitest && cd ..
```
Expected: `webui/` 生成，安装成功。

> 依赖说明：`marked` 渲染 Markdown、`dompurify` 消毒 LLM 输出防 XSS——两者是对规格依赖清单的最小补充（规格 §6.1 列了 react/react-dom/mermaid；交付物预览需要 Markdown 渲染，手写解析器才是真正的范围蔓延）。

- [ ] **Step 2: 配置 vite（代理 + vitest）**

用以下内容完整替换 `webui/vite.config.ts`：

```ts
/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = 'http://127.0.0.1:8000'
const API_PREFIXES = [
  '/sessions',
  '/chat',
  '/workspace',
  '/agents',
  '/credentials',
  '/model',
  '/openarch',
  '/health',
]

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      API_PREFIXES.map((p) => [p, { target: API_TARGET, changeOrigin: true }]),
    ),
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
```

- [ ] **Step 3: 忽略规则**

创建 `webui/.gitignore`：

```
node_modules/
dist/
```

根 `.gitignore` 末尾追加一行：

```
webui/dist/
```

- [ ] **Step 4: 验证构建**

Run: `cd webui && npm run build && cd ..`
Expected: `vite build` 成功，产出 `webui/dist/index.html`。

- [ ] **Step 5: 提交**

```bash
git add webui .gitignore
git commit -m "feat(webui): Vite+React+TS 脚手架（mermaid/marked/dompurify/vitest）"
```

---

### Task 9: 前端纯逻辑库 + vitest（sse / mermaid / tree）

**Files:**
- Create: `webui/src/lib/sse.ts`
- Create: `webui/src/lib/mermaid.ts`
- Create: `webui/src/lib/tree.ts`
- Test: `webui/src/lib/sse.test.ts`、`webui/src/lib/mermaid.test.ts`、`webui/src/lib/tree.test.ts`

- [ ] **Step 1: 写失败测试**

创建 `webui/src/lib/sse.test.ts`：

```ts
import { describe, expect, it } from 'vitest'
import { applyEvent, emptyChatState } from './sse'

describe('applyEvent', () => {
  it('REPLY_START 开启新气泡', () => {
    const s = applyEvent(emptyChatState(), { type: 'REPLY_START', reply_id: 'r1' })
    expect(s.bubbles).toHaveLength(1)
    expect(s.bubbles[0].replyId).toBe('r1')
    expect(s.bubbles[0].done).toBe(false)
  })

  it('TEXT_BLOCK_DELTA 拼接文本', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', delta: '架构' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', delta: '方案' })
    expect(s.bubbles[0].text).toBe('架构方案')
  })

  it('多个 TEXT 块之间补空行', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', block_id: 'b1', delta: 'A' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_START', reply_id: 'r1', block_id: 'b2' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', block_id: 'b2', delta: 'B' })
    expect(s.bubbles[0].text).toBe('A\n\nB')
  })

  it('TOOL_CALL_START 建条目，TOOL_RESULT_TEXT_DELTA 拼结果', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, {
      type: 'TOOL_CALL_START', reply_id: 'r1',
      tool_call_id: 't1', tool_call_name: 'review_with_waf',
    })
    s = applyEvent(s, {
      type: 'TOOL_RESULT_TEXT_DELTA', reply_id: 'r1',
      tool_call_id: 't1', delta: '{"score":0.7}',
    })
    expect(s.bubbles[0].tools[0].name).toBe('review_with_waf')
    expect(s.bubbles[0].tools[0].resultText).toBe('{"score":0.7}')
  })

  it('REPLY_END 置 done', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'REPLY_END', reply_id: 'r1' })
    expect(s.bubbles[0].done).toBe(true)
  })

  it('未知类型与缺 reply_id 的事件不抛错', () => {
    const s = applyEvent(emptyChatState(), { type: 'SOMETHING_NEW_IN_V3' })
    expect(s.bubbles).toHaveLength(0)
  })
})
```

创建 `webui/src/lib/mermaid.test.ts`：

```ts
import { describe, expect, it } from 'vitest'
import { splitMermaidSegments } from './mermaid'

describe('splitMermaidSegments', () => {
  it('提取单个 mermaid 块，前后文保留', () => {
    const segs = splitMermaidSegments('前文\n```mermaid\nflowchart LR\n  a-->b\n```\n后文')
    expect(segs).toEqual([
      { kind: 'text', content: '前文\n' },
      { kind: 'mermaid', content: 'flowchart LR\n  a-->b' },
      { kind: 'text', content: '\n后文' },
    ])
  })

  it('无块时整体为 text', () => {
    expect(splitMermaidSegments('纯文本')).toEqual([{ kind: 'text', content: '纯文本' }])
  })

  it('多个块全部提取', () => {
    const segs = splitMermaidSegments('```mermaid\na-->b\n```\n中\n```mermaid\nc-->d\n```')
    expect(segs.filter((s) => s.kind === 'mermaid')).toHaveLength(2)
  })
})
```

创建 `webui/src/lib/tree.test.ts`：

```ts
import { describe, expect, it } from 'vitest'
import { buildTree } from './tree'

describe('buildTree', () => {
  it('扁平 entries 构建嵌套树，目录在前文件按名排序', () => {
    const nodes = buildTree('工作区', [
      { name: 'a.md', path: 'a.md', isDir: false, sizeBytes: 1 },
      { name: 'deliverables', path: 'deliverables', isDir: true, sizeBytes: null },
      { name: 'x.md', path: 'deliverables/x.md', isDir: false, sizeBytes: 2 },
      { name: 'diagrams', path: 'diagrams', isDir: true, sizeBytes: null },
    ])
    expect(nodes.map((n) => n.name)).toEqual(['deliverables', 'diagrams', 'a.md'])
    expect(nodes[0].children[0].path).toBe('deliverables/x.md')
  })

  it('空 entries 返回空数组', () => {
    expect(buildTree('工作区', [])).toEqual([])
  })
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd webui && npx vitest run && cd ..`
Expected: FAIL — 找不到 `./sse`、`./mermaid`、`./tree` 模块。

- [ ] **Step 3: 实现**

创建 `webui/src/lib/sse.ts`：

```ts
export interface ToolEntry {
  toolCallId: string
  name: string
  resultText: string
  done: boolean
}

export interface Bubble {
  replyId: string
  text: string
  thinking: string
  tools: ToolEntry[]
  done: boolean
}

export interface ChatStreamState {
  bubbles: Bubble[]
}

export function emptyChatState(): ChatStreamState {
  return { bubbles: [] }
}

function upsertBubble(state: ChatStreamState, replyId: string): Bubble {
  let b = state.bubbles.find((x) => x.replyId === replyId)
  if (!b) {
    b = { replyId, text: '', thinking: '', tools: [], done: false }
    state.bubbles.push(b)
  }
  return b
}

function upsertTool(bubble: Bubble, toolCallId: string, name?: string): ToolEntry {
  let t = bubble.tools.find((x) => x.toolCallId === toolCallId)
  if (!t) {
    t = { toolCallId, name: name ?? '', resultText: '', done: false }
    bubble.tools.push(t)
  } else if (name) {
    t.name = name
  }
  return t
}

// 宽容解析：未知 type 一律忽略——AgentScope 升级新增事件类型时前端不炸。
export function applyEvent(
  state: ChatStreamState,
  ev: Record<string, unknown>,
): ChatStreamState {
  const type = ev['type'] as string | undefined
  const replyId = (ev['reply_id'] as string | undefined) ?? 'unknown'
  switch (type) {
    case 'REPLY_START':
      upsertBubble(state, replyId)
      break
    case 'TEXT_BLOCK_START': {
      const b = upsertBubble(state, replyId)
      if (b.text !== '') b.text += '\n\n'
      break
    }
    case 'TEXT_BLOCK_DELTA': {
      const b = upsertBubble(state, replyId)
      b.text += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'THINKING_BLOCK_DELTA': {
      const b = upsertBubble(state, replyId)
      b.thinking += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'TOOL_CALL_START': {
      const b = upsertBubble(state, replyId)
      upsertTool(
        b,
        (ev['tool_call_id'] as string | undefined) ?? '',
        ev['tool_call_name'] as string | undefined,
      )
      break
    }
    case 'TOOL_RESULT_TEXT_DELTA': {
      const b = upsertBubble(state, replyId)
      const t = upsertTool(b, (ev['tool_call_id'] as string | undefined) ?? '')
      t.resultText += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'TOOL_CALL_END':
    case 'TOOL_RESULT_END': {
      const b = upsertBubble(state, replyId)
      const t = upsertTool(b, (ev['tool_call_id'] as string | undefined) ?? '')
      t.done = true
      break
    }
    case 'REPLY_END': {
      const b = upsertBubble(state, replyId)
      b.done = true
      break
    }
    default:
      // 心跳注释帧、未知类型：忽略
      break
  }
  return state
}

// ---- 传输层（fetch 式 SSE：EventSource 无法带 X-User-ID 头）----

function parseSseData(frame: string): string[] {
  const out: string[] = []
  let cur = ''
  for (const line of frame.split('\n')) {
    if (line.startsWith('data:')) {
      cur += (cur ? '\n' : '') + line.slice(5).trimStart()
    }
  }
  if (cur) out.push(cur)
  return out
}

export interface StreamCallbacks {
  onEvent: (ev: Record<string, unknown>) => void
  onClose?: (err?: unknown) => void
}

export async function streamSessionEvents(
  agentId: string,
  sessionId: string,
  cb: StreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const url = `/sessions/${encodeURIComponent(sessionId)}/stream?agent_id=${encodeURIComponent(agentId)}`
  try {
    const resp = await fetch(url, {
      headers: { 'X-User-ID': 'local', Accept: 'text/event-stream' },
      signal,
    })
    if (!resp.ok || !resp.body) throw new Error(`SSE 连接失败：HTTP ${resp.status}`)
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      let idx: number
      while ((idx = buf.indexOf('\n\n')) >= 0) {
        const frame = buf.slice(0, idx)
        buf = buf.slice(idx + 2)
        for (const data of parseSseData(frame)) {
          try {
            cb.onEvent(JSON.parse(data) as Record<string, unknown>)
          } catch {
            // 非 JSON 的 data 行忽略
          }
        }
      }
    }
    cb.onClose?.()
  } catch (err) {
    if (!signal?.aborted) cb.onClose?.(err)
  }
}
```

创建 `webui/src/lib/mermaid.ts`：

```ts
export interface Segment {
  kind: 'text' | 'mermaid'
  content: string
}

const FENCE = /^```mermaid[ \t]*\r?\n([\s\S]*?)^```[ \t]*$/gm

export function splitMermaidSegments(text: string): Segment[] {
  const segments: Segment[] = []
  let last = 0
  FENCE.lastIndex = 0
  for (const m of text.matchAll(FENCE)) {
    const start = m.index ?? 0
    if (start > last) segments.push({ kind: 'text', content: text.slice(last, start) })
    segments.push({ kind: 'mermaid', content: m[1].trim() })
    last = start + m[0].length
  }
  if (last < text.length) segments.push({ kind: 'text', content: text.slice(last) })
  return segments
}

let mermaidReady: Promise<typeof import('mermaid').default> | null = null

function loadMermaid() {
  if (!mermaidReady) {
    mermaidReady = import('mermaid').then((m) => {
      m.default.initialize({ startOnLoad: false, securityLevel: 'strict' })
      return m.default
    })
  }
  return mermaidReady
}

export async function renderMermaid(code: string): Promise<string> {
  const mermaid = await loadMermaid()
  const { svg } = await mermaid.render(
    `mmd-${Math.random().toString(36).slice(2)}`,
    code,
  )
  return svg
}
```

创建 `webui/src/lib/tree.ts`：

```ts
export interface Entry {
  name: string
  path: string
  isDir: boolean
  sizeBytes: number | null
}

export interface TreeNode {
  name: string
  path: string
  isDir: boolean
  sizeBytes: number | null
  children: TreeNode[]
}

export function buildTree(_rootName: string, entries: Entry[]): TreeNode[] {
  const dirs: TreeNode[] = []
  const files: TreeNode[] = []
  for (const e of entries) {
    const node: TreeNode = {
      name: e.name,
      path: e.path,
      isDir: e.isDir,
      sizeBytes: e.sizeBytes,
      children: [],
    }
    ;(e.isDir ? dirs : files).push(node)
  }
  const sortRec = (nodes: TreeNode[]) => {
    nodes.sort((a, b) =>
      a.isDir === b.isDir ? a.name.localeCompare(b.name) : a.isDir ? -1 : 1,
    )
    for (const n of nodes) {
      const kids = n.children
      const d = kids.filter((k) => k.isDir)
      const f = kids.filter((k) => !k.isDir)
      n.children = [...d, ...f]
      sortRec(n.children)
    }
  }
  sortRec(dirs)
  sortRec(files)
  return [...dirs, ...files]
}
```

- [ ] **Step 4: 运行确认通过**

Run: `cd webui && npx vitest run && cd ..`
Expected: 9 个测试全部 PASS（sse 6 + mermaid 3 + tree 2，按实际条数）。

- [ ] **Step 5: 提交**

```bash
git add webui/src
git commit -m "feat(webui): SSE reducer / mermaid 分段 / 目录树纯逻辑 + vitest"
```

---

### Task 10: api.ts 客户端封装

**Files:**
- Create: `webui/src/lib/api.ts`

- [ ] **Step 1: 实现**

创建 `webui/src/lib/api.ts`：

```ts
const USER_ID = 'local'
const JSON_HEADERS: Record<string, string> = {
  'Content-Type': 'application/json',
  'X-User-ID': USER_ID,
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(path, {
    ...init,
    headers: { ...JSON_HEADERS, ...((init?.headers as Record<string, string>) ?? {}) },
  })
  if (!resp.ok) {
    const detail = await resp.text().catch(() => '')
    throw new Error(`${init?.method ?? 'GET'} ${path} → ${resp.status} ${detail.slice(0, 200)}`)
  }
  return (await resp.json()) as T
}

export interface OpenArchConfig {
  model: string
}

export interface SessionSummary {
  id: string
  name: string
  status: string
}

export interface DirectoryEntryRaw {
  name: string
  is_dir: boolean
  size_bytes: number | null
  updated_at: string | null
}

export const api = {
  config: () => req<OpenArchConfig>('/openarch/config'),

  agentId: async (): Promise<string> => {
    const data = await req<{ agents: { id: string; data: { name: string } }[] }>('/agents')
    const agent = data.agents.find((a) => a.data.name === 'OpenArch')
    if (!agent) throw new Error('未找到 OpenArch agent——请确认服务端种子已执行（openarch web 启动时会自动执行）')
    return agent.id
  },

  credentialId: async (): Promise<string> => {
    const data = await req<{ credentials: { id: string; data: { type: string } }[] }>('/credentials')
    const cred = data.credentials.find(
      (c) => c.data.type === 'dashscope_credential' || c.data.type === 'openai_credential',
    )
    if (!cred) throw new Error('未找到已种子凭证——请重新执行 openarch web')
    return cred.id
  },

  listSessions: (agentId: string) =>
    req<{ sessions: { session: { id: string; config: { name: string } }; status: string }[] }>(
      `/sessions?agent_id=${encodeURIComponent(agentId)}`,
    ),

  createSession: (agentId: string, credentialId: string, model: string) =>
    req<{ session_id: string }>('/sessions', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        chat_model_config: { type: 'chat', credential_id: credentialId, model, parameters: {} },
      }),
    }),

  listMessages: (agentId: string, sessionId: string) =>
    req<{ messages: unknown[]; is_running: boolean; has_more: boolean }>(
      `/sessions/${encodeURIComponent(sessionId)}/messages?agent_id=${encodeURIComponent(agentId)}`,
    ),

  chat: (agentId: string, sessionId: string, text: string) =>
    req<unknown>('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        session_id: sessionId,
        input: { role: 'user', name: 'user', content: [{ type: 'text', text }] },
      }),
    }),

  interrupt: (agentId: string, sessionId: string) =>
    req<unknown>(
      `/sessions/${encodeURIComponent(sessionId)}/interrupt?agent_id=${encodeURIComponent(agentId)}`,
      { method: 'POST' },
    ),

  listDirectory: (agentId: string, sessionId: string, path: string) =>
    req<{ path: string; entries: DirectoryEntryRaw[] }>(
      `/workspace/directories?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}`,
    ),

  fileText: async (agentId: string, sessionId: string, path: string): Promise<string> => {
    const resp = await fetch(
      `/workspace/files?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}`,
      { headers: { 'X-User-ID': USER_ID } },
    )
    if (!resp.ok) throw new Error(`读取文件失败：HTTP ${resp.status}`)
    return resp.text()
  },

  downloadUrl: (agentId: string, sessionId: string, path: string) =>
    `/workspace/files?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}&download=true`,
}
```

- [ ] **Step 2: 类型检查**

Run: `cd webui && npx tsc -b --noEmit 2>&1 | head -20 && cd ..`
Expected: 无错误（api.ts 尚无消费者，纯编译检查）。

- [ ] **Step 3: 提交**

```bash
git add webui/src/lib/api.ts
git commit -m "feat(webui): REST 客户端封装（会话/聊天/中断/工作区文件）"
```

---

### Task 11: UI 组件与样式（三区布局）

**Files:**
- Create: `webui/src/MarkdownView.tsx`
- Create: `webui/src/SessionSidebar.tsx`
- Create: `webui/src/ChatPane.tsx`
- Create: `webui/src/DeliverablesPane.tsx`
- Modify: `webui/src/App.tsx`（完整替换）
- Modify: `webui/src/main.tsx`（保留挂载，删除模板样式导入）
- Create: `webui/src/styles.css`（替换 index.css 引用）
- Delete: `webui/src/App.css`、`webui/src/index.css`（模板文件）

- [ ] **Step 1: MarkdownView（含 mermaid 渲染与流式降级）**

创建 `webui/src/MarkdownView.tsx`：

```tsx
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { useEffect, useState } from 'react'
import { renderMermaid, splitMermaidSegments } from './lib/mermaid'

export function MarkdownView({
  role,
  text,
  live,
}: {
  role: string
  text: string
  live?: boolean
}) {
  const segments = splitMermaidSegments(text)
  return (
    <div className={`msg ${role === 'user' ? 'user' : 'assistant'}`}>
      {segments.map((seg, i) =>
        seg.kind === 'text' ? (
          <div
            key={i}
            className="md"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(marked.parse(seg.content, { async: false }) as string),
            }}
          />
        ) : (
          <MermaidBlock key={i} code={seg.content} live={live} />
        ),
      )}
    </div>
  )
}

function MermaidBlock({ code, live }: { code: string; live?: boolean }) {
  const [svg, setSvg] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (live) return
    let cancelled = false
    renderMermaid(code)
      .then((s) => {
        if (!cancelled) {
          setSvg(s)
          setFailed(false)
        }
      })
      .catch(() => {
        if (!cancelled) setFailed(true)
      })
    return () => {
      cancelled = true
    }
  }, [code, live])

  if (live) return <pre className="code">{code}</pre>
  if (failed) return <pre className="code">{code}</pre>
  if (!svg) return <div className="mermaid-loading">渲染图中…</div>
  return <div className="mermaid" dangerouslySetInnerHTML={{ __html: svg }} />
}
```

- [ ] **Step 2: SessionSidebar**

创建 `webui/src/SessionSidebar.tsx`：

```tsx
import type { SessionSummary } from './lib/api'

interface Props {
  sessions: SessionSummary[]
  currentId: string | null
  onSelect: (s: SessionSummary) => void
  onCreate: () => void
}

export function SessionSidebar({ sessions, currentId, onSelect, onCreate }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-head">
        <span className="brand">OpenArch</span>
        <button className="btn btn-primary" onClick={onCreate}>
          + 新会话
        </button>
      </div>
      <ul className="session-list">
        {sessions.map((s) => (
          <li key={s.id}>
            <button
              className={s.id === currentId ? 'session-item active' : 'session-item'}
              onClick={() => onSelect(s)}
            >
              <span className="session-name">{s.name}</span>
              {s.status === 'running' && <span className="dot" title="运行中" />}
            </button>
          </li>
        ))}
        {sessions.length === 0 && <li className="empty-hint">暂无会话</li>}
      </ul>
    </aside>
  )
}
```

- [ ] **Step 3: ChatPane（历史 + SSE 实时 + 中断 + 对账）**

创建 `webui/src/ChatPane.tsx`：

```tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import type { AppCtx, SessionSummary } from './App'
import { api } from './lib/api'
import type { Bubble } from './lib/sse'
import { applyEvent, emptyChatState, streamSessionEvents } from './lib/sse'
import { MarkdownView } from './MarkdownView'

interface Props {
  ctx: AppCtx
  session: SessionSummary | null
  onSessionsChanged: () => void
}

interface HistoryMsg {
  role: string
  content: { type: string; text?: string }[]
}

export function ChatPane({ ctx, session, onSessionsChanged }: Props) {
  const [history, setHistory] = useState<HistoryMsg[]>([])
  const [live, setLive] = useState<Bubble[]>([])
  const [input, setInput] = useState('')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  // 选中会话：载历史 + 订阅事件流（断线 1.5s 后重连，服务端会先回放缓冲）
  useEffect(() => {
    if (!session) return
    let cancelled = false
    let retryTimer: ReturnType<typeof setTimeout> | undefined
    setHistory([])
    setLive([])
    setError('')
    setRunning(false)
    ;(async () => {
      try {
        const m = await api.listMessages(ctx.agentId, session.id)
        if (!cancelled) setHistory(m.messages as HistoryMsg[])
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    })()
    const ctrl = new AbortController()
    const pump = () => {
      streamSessionEvents(
        ctx.agentId,
        session.id,
        {
          onEvent: (ev) => {
            if (cancelled) return
            setLive((prev) => applyEvent({ bubbles: prev }, ev).bubbles)
            const t = ev['type']
            if (t === 'REPLY_START') setRunning(true)
            if (t === 'REPLY_END' || t === 'USER_INTERRUPT') {
              setRunning(false)
              onSessionsChanged()
            }
          },
          onClose: () => {
            if (!cancelled && !ctrl.signal.aborted) retryTimer = setTimeout(pump, 1500)
          },
        },
        ctrl.signal,
      )
    }
    pump()
    return () => {
      cancelled = true
      if (retryTimer) clearTimeout(retryTimer)
      ctrl.abort()
    }
  }, [session?.id, ctx, onSessionsChanged])

  // 全部 live 气泡完成后对账：以服务端持久化历史为准，清空实时态
  useEffect(() => {
    if (!session || live.length === 0 || !live.every((b) => b.done)) return
    let cancelled = false
    ;(async () => {
      try {
        const m = await api.listMessages(ctx.agentId, session.id)
        if (!cancelled) {
          setHistory(m.messages as HistoryMsg[])
          setLive([])
        }
      } catch {
        // 对账失败保留 live 内容
      }
    })()
    return () => {
      cancelled = true
    }
  }, [live, session, ctx])

  const send = useCallback(async () => {
    if (!session || !input.trim() || running) return
    const text = input.trim()
    setInput('')
    setHistory((prev) => [
      ...prev,
      { role: 'user', content: [{ type: 'text', text }] },
    ])
    setRunning(true)
    try {
      await api.chat(ctx.agentId, session.id, text)
    } catch (e) {
      setError(String(e))
      setRunning(false)
    }
  }, [session, input, running, ctx])

  const interrupt = useCallback(async () => {
    if (!session) return
    try {
      await api.interrupt(ctx.agentId, session.id)
    } catch (e) {
      setError(String(e))
    }
  }, [session, ctx])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, live])

  if (!session) {
    return (
      <main className="chat chat-empty">
        <p>从左侧选择一个会话，或点击「+ 新会话」开始。</p>
        <p className="muted">
          工作流：需求澄清 → 方案生成 → Mermaid 架构图 → WAF 评审 → 交付文档
        </p>
      </main>
    )
  }

  return (
    <main className="chat">
      <div className="chat-scroll">
        {history.map((m, i) => (
          <MarkdownView
            key={i}
            role={m.role}
            text={(m.content ?? [])
              .filter((c) => c.type === 'text')
              .map((c) => c.text ?? '')
              .join('\n')}
          />
        ))}
        {live.map((b) => (
          <LiveBubble key={b.replyId} bubble={b} />
        ))}
        <div ref={bottomRef} />
      </div>
      {error && (
        <div className="chat-error" onClick={() => setError('')}>
          {error}（点击关闭）
        </div>
      )}
      <div className="chat-input">
        <textarea
          value={input}
          placeholder={
            running
              ? '回复进行中…'
              : '描述你的业务需求，例如：为一个日均 10 万单的电商系统设计高可用架构'
          }
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              send()
            }
          }}
        />
        {running ? (
          <button className="btn btn-danger" onClick={interrupt}>
            中断
          </button>
        ) : (
          <button className="btn btn-primary" onClick={send} disabled={!input.trim()}>
            发送
          </button>
        )}
      </div>
    </main>
  )
}

function LiveBubble({ bubble }: { bubble: Bubble }) {
  return (
    <div className="msg assistant streaming">
      {bubble.thinking && (
        <details className="thinking">
          <summary>思考过程</summary>
          <pre>{bubble.thinking}</pre>
        </details>
      )}
      {bubble.tools.map((t) => (
        <details key={t.toolCallId} className="tool-entry">
          <summary>
            {t.done ? '🔧' : '⏳'} {t.name || '工具调用'}
          </summary>
          <pre className="tool-result">{t.resultText}</pre>
        </details>
      ))}
      <MarkdownView role="assistant" text={bubble.text} live={!bubble.done} />
    </div>
  )
}
```

- [ ] **Step 4: DeliverablesPane（递归列目录 + 预览/下载）**

创建 `webui/src/DeliverablesPane.tsx`：

```tsx
import { useCallback, useEffect, useState } from 'react'
import type { AppCtx } from './App'
import { api } from './lib/api'
import { buildTree } from './lib/tree'
import type { Entry, TreeNode } from './lib/tree'
import { MarkdownView } from './MarkdownView'

interface Props {
  ctx: AppCtx
  sessionId: string | null
}

export function DeliverablesPane({ ctx, sessionId }: Props) {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [preview, setPreview] = useState<{ name: string; text: string } | null>(null)

  // 递归列出工作区（深度上限 3 层），交付物目录通常只有两级
  const loadAll = useCallback(async () => {
    if (!sessionId) {
      setTree([])
      return
    }
    const entries: Entry[] = []
    const walk = async (path: string, depth: number): Promise<void> => {
      const listing = await api.listDirectory(ctx.agentId, sessionId, path)
      for (const e of listing.entries) {
        const childPath = path ? `${path}/${e.name}` : e.name
        entries.push({ name: e.name, path: childPath, isDir: e.is_dir, sizeBytes: e.size_bytes })
        if (e.is_dir && depth < 3) await walk(childPath, depth + 1)
      }
    }
    try {
      await walk('', 0)
      setTree(buildTree('工作区', entries))
    } catch {
      setTree([])
    }
  }, [ctx, sessionId])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const openFile = async (node: TreeNode) => {
    if (!sessionId) return
    if (node.name.endsWith('.drawio')) {
      window.open(api.downloadUrl(ctx.agentId, sessionId, node.path), '_blank')
      return
    }
    try {
      const text = await api.fileText(ctx.agentId, sessionId, node.path)
      setPreview({ name: node.name, text })
    } catch (e) {
      setPreview({ name: node.name, text: String(e) })
    }
  }

  return (
    <aside className="files">
      <div className="files-head">
        <span>交付物</span>
        <button className="btn btn-ghost" onClick={loadAll} title="刷新">
          ↻
        </button>
      </div>
      <Tree nodes={tree} onOpen={openFile} />
      {tree.length === 0 && <div className="empty-hint">暂无交付物</div>}
      {preview && (
        <div className="preview">
          <div className="preview-head">
            <span>{preview.name}</span>
            <button className="btn btn-ghost" onClick={() => setPreview(null)}>
              ×
            </button>
          </div>
          <MarkdownView role="assistant" text={preview.text} />
        </div>
      )}
    </aside>
  )
}

function Tree({
  nodes,
  onOpen,
  depth = 0,
}: {
  nodes: TreeNode[]
  onOpen: (n: TreeNode) => void
  depth?: number
}) {
  return (
    <ul className={depth === 0 ? 'file-tree' : 'file-tree nested'}>
      {nodes.map((n) => (
        <li key={n.path}>
          {n.isDir ? (
            <details open={depth < 1}>
              <summary>{n.name}/</summary>
              <Tree nodes={n.children} onOpen={onOpen} depth={depth + 1} />
            </details>
          ) : (
            <button className="file-link" onClick={() => onOpen(n)}>
              {n.name}
            </button>
          )}
        </li>
      ))}
    </ul>
  )
}
```

- [ ] **Step 5: App.tsx（完整替换）**

用以下内容替换 `webui/src/App.tsx` 全部内容：

```tsx
import { useCallback, useEffect, useState } from 'react'
import { ChatPane } from './ChatPane'
import { DeliverablesPane } from './DeliverablesPane'
import { api } from './lib/api'
import type { SessionSummary } from './lib/api'
import { SessionSidebar } from './SessionSidebar'

export interface AppCtx {
  agentId: string
  credentialId: string
  model: string
}

export default function App() {
  const [ctx, setCtx] = useState<AppCtx | null>(null)
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [current, setCurrent] = useState<SessionSummary | null>(null)
  const [error, setError] = useState('')
  const [ready, setReady] = useState(false)

  useEffect(() => {
    ;(async () => {
      try {
        const cfg = await api.config()
        const [agentId, credentialId] = await Promise.all([api.agentId(), api.credentialId()])
        setCtx({ agentId, credentialId, model: cfg.model })
        const s = await api.listSessions(agentId)
        setSessions(
          s.sessions.map((v) => ({
            id: v.session.id,
            name: v.session.config.name,
            status: v.status,
          })),
        )
        setReady(true)
      } catch (e) {
        setError(String(e))
      }
    })()
  }, [])

  const refreshSessions = useCallback(async () => {
    if (!ctx) return
    const s = await api.listSessions(ctx.agentId)
    setSessions(
      s.sessions.map((v) => ({
        id: v.session.id,
        name: v.session.config.name,
        status: v.status,
      })),
    )
  }, [ctx])

  const createSession = useCallback(async () => {
    if (!ctx) return
    try {
      const { session_id } = await api.createSession(ctx.agentId, ctx.credentialId, ctx.model)
      await refreshSessions()
      setCurrent({ id: session_id, name: '新会话', status: 'idle' })
    } catch (e) {
      setError(String(e))
    }
  }, [ctx, refreshSessions])

  if (error) return <div className="boot boot-error">启动失败：{error}</div>
  if (!ready) return <div className="boot">加载中…</div>
  return (
    <div className="app">
      <SessionSidebar
        sessions={sessions}
        currentId={current?.id ?? null}
        onSelect={setCurrent}
        onCreate={createSession}
      />
      <ChatPane ctx={ctx} session={current} onSessionsChanged={refreshSessions} />
      <DeliverablesPane ctx={ctx} sessionId={current?.id ?? null} />
    </div>
  )
}
```

- [ ] **Step 6: main.tsx 与样式**

替换 `webui/src/main.tsx` 为：

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

删除模板残留：`rm webui/src/App.css webui/src/index.css`（若 `App.tsx`/`main.tsx` 原本引用它们，上面的替换已去掉引用）。

创建 `webui/src/styles.css`：

```css
* { box-sizing: border-box; }
html, body, #root { height: 100%; margin: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #1f2328;
  background: #f6f8fa;
}

.app { display: flex; height: 100%; }
.boot { display: flex; align-items: center; justify-content: center; height: 100%; color: #57606a; }
.boot-error { color: #cf222e; }

/* ---- 会话侧栏 ---- */
.sidebar {
  width: 240px; flex-shrink: 0; display: flex; flex-direction: column;
  background: #fff; border-right: 1px solid #d0d7de;
}
.sidebar-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px; border-bottom: 1px solid #d0d7de;
}
.brand { font-weight: 700; }
.session-list { list-style: none; margin: 0; padding: 8px; overflow-y: auto; flex: 1; }
.session-item {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  width: 100%; padding: 8px 10px; border: 0; border-radius: 6px;
  background: transparent; cursor: pointer; text-align: left; font-size: 14px;
}
.session-item:hover { background: #f3f4f6; }
.session-item.active { background: #ddf4ff; }
.session-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #1a7f37; flex-shrink: 0; }
.empty-hint { color: #8c959f; font-size: 13px; padding: 8px 10px; }

/* ---- 聊天主区 ---- */
.chat { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-empty { align-items: center; justify-content: center; color: #57606a; }
.chat-scroll { flex: 1; overflow-y: auto; padding: 24px 32px; }
.msg {
  max-width: 760px; margin: 0 auto 16px; padding: 12px 16px;
  border-radius: 10px; background: #fff; border: 1px solid #d0d7de;
  line-height: 1.65; word-break: break-word;
}
.msg.user { background: #ddf4ff; border-color: #a5d8ff; }
.msg .md > :first-child { margin-top: 0; }
.msg .md > :last-child { margin-bottom: 0; }
.msg .md pre, .code {
  background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px;
  padding: 10px; overflow-x: auto; font-size: 13px;
}
.mermaid { overflow-x: auto; background: #fff; }
.mermaid-loading { color: #8c959f; font-size: 13px; padding: 8px 0; }
.thinking summary, .tool-entry summary { cursor: pointer; color: #57606a; font-size: 13px; }
.tool-result { max-height: 240px; overflow: auto; }
.streaming { border-style: dashed; }
.chat-error {
  margin: 0 32px 8px; padding: 8px 12px; border-radius: 6px; cursor: pointer;
  background: #ffebe9; color: #cf222e; font-size: 13px;
}
.chat-input {
  display: flex; gap: 8px; padding: 12px 32px 16px;
  border-top: 1px solid #d0d7de; background: #fff;
}
.chat-input textarea {
  flex: 1; resize: none; height: 64px; padding: 10px 12px;
  border: 1px solid #d0d7de; border-radius: 8px; font: inherit;
}

/* ---- 交付物面板 ---- */
.files {
  width: 260px; flex-shrink: 0; display: flex; flex-direction: column;
  background: #fff; border-left: 1px solid #d0d7de; position: relative;
}
.files-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px; border-bottom: 1px solid #d0d7de; font-weight: 600;
}
.file-tree { list-style: none; margin: 0; padding: 8px 12px; overflow-y: auto; flex: 1; font-size: 13px; }
.file-tree.nested { padding: 0 0 0 14px; }
.file-tree summary { cursor: pointer; padding: 2px 0; }
.file-link {
  display: block; width: 100%; text-align: left; padding: 2px 4px; border: 0;
  background: transparent; cursor: pointer; border-radius: 4px; font-size: 13px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.file-link:hover { background: #f3f4f6; }
.preview {
  position: absolute; inset: 0; background: #fff; display: flex; flex-direction: column;
  border-left: 1px solid #d0d7de;
}
.preview-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-bottom: 1px solid #d0d7de; font-weight: 600; font-size: 13px;
}
.preview > .msg { border: 0; border-radius: 0; background: transparent; margin: 0; }

/* ---- 按钮 ---- */
.btn { padding: 6px 12px; border-radius: 6px; border: 1px solid #d0d7de; background: #fff; cursor: pointer; font-size: 13px; }
.btn:hover { background: #f3f4f6; }
.btn-primary { background: #0969da; border-color: #0969da; color: #fff; }
.btn-primary:hover { background: #0860ca; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger { background: #cf222e; border-color: #cf222e; color: #fff; }
.btn-ghost { border: 0; background: transparent; }
.muted { color: #8c959f; font-size: 13px; }
```

- [ ] **Step 7: 构建 + 全部前端测试**

Run: `cd webui && npm test && npm run build && cd ..`
Expected: vitest 全 PASS；`tsc -b` 无类型错误；`dist/` 产出。

- [ ] **Step 8: 提交**

```bash
git add webui/src
git commit -m "feat(webui): 三区 UI（会话侧栏/聊天主区/交付物面板）+ Mermaid 渲染"
```

---

### Task 12: Docker 多阶段 + compose

**Files:**
- Modify: `Dockerfile`（完整替换）
- Modify: `docker-compose.yml`
- Modify: `.dockerignore`

- [ ] **Step 1: 重写 Dockerfile**

用以下内容完整替换 `Dockerfile`：

```dockerfile
# syntax=docker/dockerfile:1

# ---- 前端构建 ----
FROM node:22-alpine AS webui
WORKDIR /webui
COPY webui/package.json webui/package-lock.json ./
RUN npm ci
COPY webui/ ./
RUN npm run build

# ---- Python 运行时 ----
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY skills/ ./skills/
COPY tests/ ./tests/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# 前端产物放进包内静态目录（app.py 的 find_static_dir 第一候选）
COPY --from=webui /webui/dist ./src/openarch/web/static/dist

ENV OPENARCH_DB=/data/openarch.db
ENV OPENARCH_WORKSPACE=/data/deliverables
VOLUME ["/data"]

CMD ["uv", "run", "--no-sync", "openarch", "web"]
```

- [ ] **Step 2: 更新 compose 与 dockerignore**

`docker-compose.yml` 改为：

```yaml
services:
  openarch:
    build: .
    stdin_open: true
    tty: true
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
```

`.dockerignore` 追加两行（若 `webui/` 已整行忽略则只需保证 `webui/node_modules` 不进上下文）：

```
webui/node_modules
webui/dist
```

- [ ] **Step 3: 语法验证（不实际构建，若本机 Docker 可用则构建）**

Run: `docker compose config -q`
Expected: 无输出（配置合法）。若 Docker 可用，额外执行 `docker build -t openarch .` 验证两阶段构建（网络较慢可跳过，留给用户验收）。

- [ ] **Step 4: 提交**

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "build(docker): node 前端构建阶段 + openarch web 入口"
```

---

### Task 13: CI 增加 webui job

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: 追加 webui job**

在 `.github/workflows/ci.yml` 的现有 python job 之后追加（保持缩进与现有 job 平级）：

```yaml
  webui:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: webui
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: webui/package-lock.json
      - run: npm ci
      - run: npm run build
      - run: npm test
```

- [ ] **Step 2: 本地验证 yaml**

Run: `docker compose config -q 2>/dev/null; python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml')); print('ok')"`
Expected: 输出 `ok`。

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: 增加 webui 构建 + vitest job"
```

---

### Task 14: README 与 .env.example 更新

**Files:**
- Modify: `README.md`
- Modify: `.env.example`

- [ ] **Step 1: README 增加 Web UI 章节**

在「快速开始」之后插入：

```markdown
## Web UI（浏览器）

    uv run openarch web        # 默认 http://127.0.0.1:8000
    # 或
    uv run openarch web --host 0.0.0.0 --port 9000

首次启动会自动完成初始化（幂等种子）：写入 SQLite（`OPENARCH_DB`）、
注册 OpenArch agent 与模型凭证（密钥只进服务端存储，不回传前端）。

浏览器打开 `http://127.0.0.1:8000`：

- 左栏：会话列表 + 新建会话
- 中间：聊天主区，实时流式回复，Mermaid 架构图自动渲染
- 右栏：交付物面板，Markdown 在线预览、draw.io 文件下载

前端开发模式：

    cd webui && npm install && npm run dev   # http://localhost:5173，代理 API 到 8000
```

「配置」表格追加三行（与现有风格一致）：

```markdown
| `OPENARCH_DB` | 否 | `./data/openarch.db` | Web 模式 SQLite 路径（工作区在其同级 `workspaces/`） |
| `OPENARCH_HOST` | 否 | `127.0.0.1` | Web 监听地址 |
| `OPENARCH_PORT` | 否 | `8000` | Web 监听端口 |
```

「开发」一节追加：`cd webui && npm test   # 前端单元测试`。

- [ ] **Step 2: .env.example 追加**

```
# Web UI（可选）
# OPENARCH_DB=./data/openarch.db
# OPENARCH_HOST=127.0.0.1
# OPENARCH_PORT=8000
```

- [ ] **Step 3: 全量回归 + 提交**

Run: `uv run pytest -m "not e2e" -q && uv run ruff check src tests`
Expected: 全 PASS、ruff 干净。

```bash
git add README.md .env.example
git commit -m "docs: README Web UI 章节 + 新配置项"
```

---

## 手动验收清单（完成后、请求用户验收前执行）

1. `uv run openarch web` 启动无报错；终端打印 `http://127.0.0.1:8000`；`data/openarch.db` 与 `data/workspaces/` 生成
2. 浏览器打开首页：三区布局渲染；左侧出现「+ 新会话」
3. 新建会话 → 发送「为一个日均 10 万单的电商系统设计高可用架构」→ 观察流式回复、工具调用折叠块、Mermaid 图渲染
4. 中断按钮：回复进行中点击中断，流停止
5. 右栏出现 `deliverables/`（或工作区根下）的 `.md` 交付物与 `diagrams/` 的 `.drawio`；`.md` 点击预览、`.drawio` 下载
6. 刷新页面：历史会话与消息仍在（SQLite 持久化）
7. `uv run openarch`（无参数）console 模式回归正常
8. 凭证安全核对：`curl -H "X-User-ID: local" http://127.0.0.1:8000/credentials` 检查响应不含明文 api_key
9. 浏览器 console 无未捕获异常（SSE 重连日志除外）

## Self-Review 记录

- **Spec 覆盖**：规格 §5 后端（Task 1/3/4/5/6）、§5.5 API（Task 8/9/10/11 消费面）、§6 前端（Task 8-11）、§7 Docker（Task 12）、§8 错误处理（Task 6 启动自检 + Task 11 前端错误条/SSE 重连）、§9 测试（Task 3-7 Python、Task 9 vitest、验收清单）、README/CI（Task 13/14）——无缺口。
- **占位符扫描**：无 TBD/TODO；所有代码步骤含完整代码。
- **类型一致性**：`BootstrapInfo(agent_id, credential_id)` 在 Task 3 定义、Task 6/7 消费；`make_openarch_tools(settings, manager)` 在 Task 4 定义、Task 5 消费；`find_static_dir` 在 Task 5 定义、Task 6 消费；`AppCtx`/`SessionSummary` 在 Task 11 定义并跨组件一致；`buildTree/Entry/TreeNode`、`applyEvent/ChatStreamState/Bubble`、`splitMermaidSegments/Segment` 定义与测试一致。
- **已批准偏差**：`marked` + `dompurify` 两个前端依赖为规格依赖清单的最小补充（Markdown 渲染 + XSS 消毒），理由写在 Task 8 Step 1。
