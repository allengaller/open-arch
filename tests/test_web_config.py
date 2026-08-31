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
