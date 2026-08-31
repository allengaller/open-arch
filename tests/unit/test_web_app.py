from fastapi.testclient import TestClient

from openarch.config import load_settings
from openarch.web.app import _STATIC_CANDIDATES, create_web_app, find_static_dir


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


def _with_candidates(monkeypatch, *dirs):
    monkeypatch.setattr("openarch.web.app._STATIC_CANDIDATES", dirs)


def test_find_static_dir_prefers_first_candidate(tmp_path, monkeypatch):
    # 包内（Docker 构建产物）优先于仓库兜底——顺序颠倒会让容器静默退化到旧产物。
    first, second = tmp_path / "pkg", tmp_path / "repo"
    for d in (first, second):
        d.mkdir()
        (d / "index.html").write_text("<html></html>")
    _with_candidates(monkeypatch, first, second)
    assert find_static_dir() == first


def test_find_static_dir_skips_dir_without_index_html(tmp_path, monkeypatch):
    # 目录存在但缺 index.html 不算有效产物，继续探测下一个候选。
    empty, valid = tmp_path / "empty", tmp_path / "valid"
    empty.mkdir()
    valid.mkdir()
    (valid / "index.html").write_text("<html></html>")
    _with_candidates(monkeypatch, empty, valid)
    assert find_static_dir() == valid


def test_find_static_dir_returns_none_when_all_missing(tmp_path, monkeypatch):
    # 本地未构建前端时返回 None，create_web_app 据此跳过静态挂载。
    _with_candidates(monkeypatch, tmp_path / "missing-a", tmp_path / "missing-b")
    assert find_static_dir() is None


def test_static_candidates_shape():
    # 锁定候选形态：包内 static/dist 在前、仓库 webui/dist 兜底在后。
    assert _STATIC_CANDIDATES[0].name == "dist"
    assert _STATIC_CANDIDATES[0].parent.name == "static"
    assert _STATIC_CANDIDATES[1].name == "dist"
    assert _STATIC_CANDIDATES[1].parent.name == "webui"

