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
        # agentscope 2.0.7.post1 的 /health 声明了必需的 x-user-id 头，
        # 裸 GET 会 422；头值任意即可，这里取 bootstrap 的 USER_ID。
        assert (
            client.get("/health", headers={"x-user-id": "local"}).status_code == 200
        )
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
