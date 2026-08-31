from __future__ import annotations

from dataclasses import dataclass

from agentscope.agent import ContextConfig, ReActConfig
from agentscope.app.storage import AgentData, AgentRecord, AsyncSQLAlchemyStorage
from agentscope.credential import (
    CredentialBase,
    DashScopeCredential,
    OpenAICredential,
)
from pydantic import SecretStr

from openarch.agent import SYSTEM_PROMPT
from openarch.config import Settings

USER_ID = "local"
_AGENT_NAME = "OpenArch"
_CREDENTIAL_ID = "openarch-primary"
_AGENT_ID = "openarch-agent"


@dataclass(frozen=True)
class BootstrapInfo:
    agent_id: str
    credential_id: str


async def run_bootstrap(settings: Settings) -> BootstrapInfo:
    """幂等种子：凭证（按模式二选一）+ OpenArch agent 记录。

    预设固定 id + 无条件 upsert：重复调用对同一行原地更新，
    配置轮换（api_key / base_url）与提示词升级随之生效。
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
            id=_CREDENTIAL_ID,
            api_key=SecretStr(settings.openai_api_key or ""),
            base_url=settings.base_url,
        )
    else:
        credential = DashScopeCredential(
            id=_CREDENTIAL_ID,
            api_key=SecretStr(settings.dashscope_api_key or ""),
        )
    return await storage.upsert_credential(USER_ID, credential)


async def _seed_agent(storage: AsyncSQLAlchemyStorage) -> str:
    record = AgentRecord(
        id=_AGENT_ID,
        user_id=USER_ID,
        data=AgentData(
            id=_AGENT_ID,
            name=_AGENT_NAME,
            system_prompt=SYSTEM_PROMPT,
            context_config=ContextConfig(),
            react_config=ReActConfig(),
        ),
    )
    return await storage.upsert_agent(USER_ID, record)
