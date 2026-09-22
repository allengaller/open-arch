import pytest

from openarch.config import ConfigError, load_settings

DUMMY_VALUE = "dummy-value"


def test_defaults_with_dashscope_key():
    s = load_settings(env={"DASHSCOPE_API_KEY": DUMMY_VALUE})
    assert s.model == "qwen-max"
    assert s.base_url is None
    assert s.workspace.name == "deliverables"
    assert s.dashscope_api_key is not None
    assert s.dashscope_api_key.get_secret_value() == DUMMY_VALUE


def test_secret_keys_not_leaked_by_repr():
    # SecretStr 加固：settings 被意外打印/记日志时 key 只显掩码。
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": DUMMY_VALUE,
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": DUMMY_VALUE,
        }
    )
    assert DUMMY_VALUE not in repr(s)
    assert DUMMY_VALUE not in str(s.dashscope_api_key)
    assert s.dashscope_api_key.get_secret_value() == DUMMY_VALUE
    assert s.openai_api_key is not None
    assert s.openai_api_key.get_secret_value() == DUMMY_VALUE


def test_invalid_port_raises_config_error():
    with pytest.raises(ConfigError) as exc:
        load_settings(env={"DASHSCOPE_API_KEY": DUMMY_VALUE, "OPENARCH_PORT": "abc"})
    assert "OPENARCH_PORT" in str(exc.value)


@pytest.mark.parametrize("port", ["-1", "99999"])
def test_out_of_range_port_raises_config_error(port):
    with pytest.raises(ConfigError) as exc:
        load_settings(env={"DASHSCOPE_API_KEY": DUMMY_VALUE, "OPENARCH_PORT": port})
    assert "OPENARCH_PORT" in str(exc.value)


def test_missing_key_raises_with_guidance():
    with pytest.raises(ConfigError) as exc:
        load_settings(env={})
    assert "DASHSCOPE_API_KEY" in str(exc.value)
    assert "README" in str(exc.value)


def test_base_url_switches_to_openai_compatible():
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": DUMMY_VALUE,
            "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            "OPENARCH_API_KEY": DUMMY_VALUE,
            "OPENARCH_MODEL": "my-model",
        }
    )
    assert s.base_url == "http://localhost:8000/v1"
    assert s.openai_api_key is not None
    assert s.openai_api_key.get_secret_value() == DUMMY_VALUE
    assert s.model == "my-model"


def test_base_url_without_api_key_raises():
    with pytest.raises(ConfigError) as exc:
        load_settings(
            env={
                "DASHSCOPE_API_KEY": DUMMY_VALUE,
                "OPENARCH_BASE_URL": "http://localhost:8000/v1",
            }
        )
    assert "OPENARCH_API_KEY" in str(exc.value)


def test_workspace_and_skills_dir_overrides(tmp_path):
    s = load_settings(
        env={
            "DASHSCOPE_API_KEY": DUMMY_VALUE,
            "OPENARCH_WORKSPACE": str(tmp_path / "out"),
            "OPENARCH_SKILLS_DIR": str(tmp_path / "skills"),
        }
    )
    assert s.workspace == tmp_path / "out"
    assert s.skills_dir == tmp_path / "skills"


def test_db_parent_dir_created_for_default_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = load_settings(env={"DASHSCOPE_API_KEY": DUMMY_VALUE})
    assert s.db == tmp_path / "data" / "openarch.db"
    assert s.db.parent.is_dir()


def test_db_parent_dir_created_for_custom_deep_path(tmp_path):
    db = tmp_path / "a" / "b" / "openarch.db"
    s = load_settings(env={"DASHSCOPE_API_KEY": DUMMY_VALUE, "OPENARCH_DB": str(db)})
    assert s.db == db
    assert s.db.parent.is_dir()
