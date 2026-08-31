"""Web 模式 Copilot 冒烟：真实 Key 走 FastAPI TestClient 全链路。

建 session → POST /chat/ → 轮询 GET /sessions/{id}/messages，
直到出现 assistant 回复（或 120 秒超时失败）。
无 DASHSCOPE_API_KEY 时跳过（手动 `uv run pytest -m e2e` 触发）。
"""

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
            assert m.status_code == 200, m.text
            payload = m.json()
            if any(msg.get("role") == "assistant" for msg in payload["messages"]):
                break
            if not payload.get("is_running", True):
                pytest.fail(
                    f"agent 已停止（is_running=false）但无助手回复；"
                    f"session={session_id}，末次响应：{payload}"
                )
        else:
            pytest.fail(
                f"120 秒内未收到助手回复；session={session_id}，末次响应：{m.json()}"
            )
