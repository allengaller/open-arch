from fastapi.testclient import TestClient

from openarch.config import load_settings
from openarch.web.app import _STATIC_CANDIDATES, create_web_app, find_static_dir

DUMMY_VALUE = "dummy-value"


def _settings(tmp_path):
    return load_settings(
        env={"DASHSCOPE_API_KEY": DUMMY_VALUE, "OPENARCH_DB": str(tmp_path / "app.db")}
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


def test_gtm_mount_not_swallowed_by_root_mount(tmp_path, monkeypatch):
    # Mount("/") 按注册顺序捕获所有路径：/gtm 必须先于 webui 根挂载注册，
    # 否则 /gtm/ 落进 webui dist 找不到文件而 404。
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>openarch-ok</html>")
    gtm = tmp_path / "gtm"
    gtm.mkdir()
    (gtm / "index.html").write_text("<html>gtm-ok</html>")
    monkeypatch.setattr("openarch.web.app.find_static_dir", lambda: dist)
    monkeypatch.setattr("openarch.web.app.find_gtm_dir", lambda: gtm)

    app = create_web_app(_settings(tmp_path))
    with TestClient(app) as client:
        assert "gtm-ok" in client.get("/gtm/").text
        assert "openarch-ok" in client.get("/").text


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


async def test_credential_response_masks_api_key(tmp_path):
    # agentscope 的 /credential/ 会原样回显存储的 api_key；OpenArch 在装配层
    # 统一掩码，保证明文 key 永不出服务端（手动验收清单第 8 项）。
    from openarch.web.bootstrap import run_bootstrap

    s = _settings(tmp_path)
    await run_bootstrap(s)
    app = create_web_app(s)
    with TestClient(app) as client:
        r = client.get("/credential/", headers={"x-user-id": "local"})
        assert r.status_code == 200
        assert DUMMY_VALUE not in r.text, "明文 key 不得出现在凭证响应中"

        def walk(node):
            if isinstance(node, dict):
                yield node
                for v in node.values():
                    yield from walk(v)
            elif isinstance(node, list):
                for v in node:
                    yield from walk(v)

        api_keys = [d["api_key"] for d in walk(r.json()) if "api_key" in d]
        assert api_keys == ["***"], f"api_key 应被掩码，实际：{api_keys}"


async def test_masking_middleware_passes_through_other_routes(tmp_path):
    # 掩码 middleware 只拦 /credential*：其余端点（含 SSE 类路径）不受缓冲影响。
    from openarch.web.bootstrap import run_bootstrap

    s = _settings(tmp_path)
    await run_bootstrap(s)
    app = create_web_app(s)
    with TestClient(app) as client:
        r = client.get("/openarch/config")
        assert r.status_code == 200
        assert r.json() == {"model": "qwen-max"}


async def test_masking_preserves_credential_schemas(tmp_path):
    # GET /credential/schemas 里的 api_key 是 JSON Schema 定义对象（type: string、
    # format: password）而非密钥值；掩码只作用于标量值，否则凭证表单拿到的契约被破坏。
    from openarch.web.bootstrap import run_bootstrap

    s = _settings(tmp_path)
    await run_bootstrap(s)
    app = create_web_app(s)
    with TestClient(app) as client:
        r = client.get("/credential/schemas", headers={"x-user-id": "local"})
        assert r.status_code == 200

        def walk(node):
            if isinstance(node, dict):
                yield node
                for v in node.values():
                    yield from walk(v)
            elif isinstance(node, list):
                for v in node:
                    yield from walk(v)

        schemas = [d["api_key"] for d in walk(r.json()) if "api_key" in d]
        assert schemas, "响应中应存在 api_key 的 schema 定义"
        assert all(
            isinstance(v, dict) and v.get("type") == "string" for v in schemas
        ), f"schema 定义对象不得被掩码：{schemas}"


async def test_masking_middleware_omits_content_length_on_204(tmp_path):
    # RFC 7230 §3.3.2：204 响应不得携带 Content-Length；middleware 重算头时要跳过。
    from openarch.web.bootstrap import run_bootstrap

    s = _settings(tmp_path)
    await run_bootstrap(s)
    app = create_web_app(s)
    with TestClient(app) as client:
        lst = client.get("/credential/", headers={"x-user-id": "local"})
        assert lst.status_code == 200
        cred_id = lst.json()["credentials"][0]["id"]
        r = client.delete(f"/credential/{cred_id}", headers={"x-user-id": "local"})
        assert r.status_code == 204
        assert "content-length" not in r.headers

