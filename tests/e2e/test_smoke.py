import os
from dataclasses import replace

import pytest

pytestmark = pytest.mark.e2e

pytest.importorskip("agentscope")


@pytest.fixture()
def settings(tmp_path):
    if not os.environ.get("DASHSCOPE_API_KEY"):
        pytest.skip("需要 DASHSCOPE_API_KEY")
    from openarch.config import load_settings

    return replace(load_settings(), workspace=tmp_path)


async def test_agent_replies(settings, tmp_path):
    from agentscope.message import UserMsg

    from openarch.agent import build_agent

    agent = build_agent(settings)
    # agentscope 2.0.7: Agent 无 __call__，调用约定为 await agent.reply(...)；
    # Msg.content 仅接受 block 列表，普通字符串用 UserMsg 工厂包裹。
    reply = await agent.reply(
        UserMsg(name="user", content="给一个日均 10 万订单的电商设计架构，直接开始。")
    )
    text = str(reply.get_text_content() or "")
    assert text.strip(), "Agent 返回了空回复"
    assert ("mermaid" in text) or any(tmp_path.iterdir()), (
        "回复中应包含架构图或产出交付物文件"
    )
