import pytest

from openarch.config import ConfigError, load_settings


def test_defaults_with_dashscope_key():
    s = load_settings(env={"DASHSCOPE_API_KEY": "sk-test"})
    assert s.model == "qwen-max"
    assert s.base_url is None
    assert s.workspace.name == "deliverables"
    assert s.dashscope_api_key == "sk-test"


def test_missing_key_raises_with_guidance():
    with pytest.raises(ConfigError) as exc:
        load_settings(env={})
    assert "DASHSCOPE_API_KEY" in str(exc.value)
    assert "README" in str(exc.value)


def test_base_url_switches_to_openai_compatible():
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": "sk-test",
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": "sk-local",
            "OPENARCH_MODEL": "my-model",
        }
    )
    assert s.base_url == "http://localhost:8000/v1"
    assert s.openai_api_key == "sk-local"
    assert s.model == "my-model"


def test_base_url_without_api_key_raises():
    with pytest.raises(ConfigError) as exc:
        load_settings(
            env={
                "DASHSCOPE_API_KEY": "sk-test",
                "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            }
        )
    assert "OPENARCH_API_KEY" in str(exc.value)


def test_workspace_and_skills_dir_overrides(tmp_path):
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": "sk-test",
            "OPENARCH_WORKSPACE": str(tmp_path / "out"),
            "OPENARCH_SKILLS_DIR": str(tmp_path / "skills"),
        }
    )
    assert s.workspace == tmp_path / "out"
    assert s.skills_dir == tmp_path / "skills"
