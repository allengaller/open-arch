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
    assert creds[0].data["type"] == "dashscope_credential"


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
    assert creds[0].data["type"] == "openai_credential"
    assert info.credential_id == creds[0].id


async def test_credential_rotation(tmp_path):
    from agentscope.app.storage import AsyncSQLAlchemyStorage

    db = tmp_path / "r.db"
    s1 = load_settings(
        env={"DASHSCOPE_API_KEY": "sk-A", "OPENARCH_DB": str(db)}
    )
    await run_bootstrap(s1)
    s2 = load_settings(
        env={"DASHSCOPE_API_KEY": "sk-B", "OPENARCH_DB": str(db)}
    )
    info = await run_bootstrap(s2)
    storage = AsyncSQLAlchemyStorage(f"sqlite+aiosqlite:///{db}")
    async with storage:
        creds = await storage.list_credentials("local")
    assert len(creds) == 1
    assert creds[0].data["api_key"] == "sk-B"
    assert info.credential_id == creds[0].id


async def test_agent_prompt_reassert(tmp_path):
    from agentscope.agent import ContextConfig, ReActConfig
    from agentscope.app.storage import (
        AgentData,
        AgentRecord,
        AsyncSQLAlchemyStorage,
    )

    db = tmp_path / "p.db"
    storage = AsyncSQLAlchemyStorage(
        f"sqlite+aiosqlite:///{db}", create_tables=True
    )
    async with storage:
        await storage.upsert_agent(
            "local",
            AgentRecord(
                id="openarch-agent",
                user_id="local",
                data=AgentData(
                    id="openarch-agent",
                    name="OpenArch",
                    system_prompt="stale prompt",
                    context_config=ContextConfig(),
                    react_config=ReActConfig(),
                ),
            ),
        )
    s = load_settings(
        env={"DASHSCOPE_API_KEY": "sk-test", "OPENARCH_DB": str(db)}
    )
    await run_bootstrap(s)
    storage2 = AsyncSQLAlchemyStorage(f"sqlite+aiosqlite:///{db}")
    async with storage2:
        agents = await storage2.list_agents("local")
    assert len(agents) == 1
    assert agents[0].data.name == "OpenArch"
    assert agents[0].data.system_prompt == SYSTEM_PROMPT
