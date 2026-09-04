from agentscope.model import DashScopeChatModel, OpenAIChatModel

from openarch.agent import build_agent
from openarch.config import load_settings

DUMMY_VALUE = "dummy-value"


def test_build_agent_with_fake_key(tmp_path):
    skills = tmp_path / "skills"
    (skills / "demo").mkdir(parents=True)
    (skills / "demo" / "SKILL.md").write_text(
        "---\nname: demo\ndescription: 演示技能\n---\n内容",
        encoding="utf-8",
    )
    settings = load_settings(
        env={"DASHSCOPE_API_KEY": DUMMY_VALUE, "OPENARCH_SKILLS_DIR": str(skills)}
    )
    agent = build_agent(settings)
    assert isinstance(agent.model, DashScopeChatModel)
    assert agent.name == "openarch"


def test_build_agent_with_openai_compatible(tmp_path):
    settings = load_settings(
        env={
            "DASHSCOPE_API_KEY": DUMMY_VALUE,
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": DUMMY_VALUE,
        }
    )
    agent = build_agent(settings)
    assert isinstance(agent.model, OpenAIChatModel)
    assert agent.name == "openarch"
