from fastapi.testclient import TestClient

from openarch.config import load_settings
from openarch.web.app import create_web_app

DUMMY_VALUE = "dummy-value"


def _settings(tmp_path, skills):
    return load_settings(
        env={
            "DASHSCOPE_API_KEY": DUMMY_VALUE,
            "OPENARCH_DB": str(tmp_path / "app.db"),
            "OPENARCH_SKILLS_DIR": str(skills),
        }
    )


def _make_pack(skills, name, description="演示技能"):
    pack = skills / name
    pack.mkdir(parents=True)
    (pack / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n说明",
        encoding="utf-8",
    )
    (pack / "content").mkdir()
    (pack / "content" / "basics.md").write_text("# 概念\n\n正文", encoding="utf-8")


def test_list_skills_returns_packs_with_files(tmp_path):
    skills = tmp_path / "skills"
    _make_pack(skills, "demo-a", "技能 A")
    (skills / "not-a-pack").mkdir()  # 缺 SKILL.md 的目录不计入
    app = create_web_app(_settings(tmp_path, skills))
    with TestClient(app) as client:
        r = client.get("/openarch/skills", headers={"x-user-id": "local"})
    assert r.status_code == 200
    packs = r.json()["skills"]
    assert [p["name"] for p in packs] == ["demo-a"]
    assert packs[0]["description"] == "技能 A"
    assert "content/basics.md" in packs[0]["files"]
    assert "SKILL.md" in packs[0]["files"]


def test_read_skill_file_returns_markdown(tmp_path):
    skills = tmp_path / "skills"
    _make_pack(skills, "demo-a")
    app = create_web_app(_settings(tmp_path, skills))
    with TestClient(app) as client:
        r = client.get("/openarch/skills/demo-a/content/basics.md", headers={"x-user-id": "local"})
    assert r.status_code == 200
    assert "# 概念" in r.text
    assert r.headers["content-type"].startswith("text/markdown")


def test_rejects_traversal_non_text_and_missing(tmp_path):
    skills = tmp_path / "skills"
    _make_pack(skills, "demo-a")
    (skills / "demo-a" / "tool.py").write_text("print()", encoding="utf-8")
    app = create_web_app(_settings(tmp_path, skills))
    with TestClient(app) as client:
        for url in (
            "/openarch/skills/demo-a/tool.py",  # 非白名单后缀
            "/openarch/skills/demo-a/%2e%2e/%2e%2e/secret.md",  # 路径穿越
            "/openarch/skills/missing/SKILL.md",  # 不存在的技能包
        ):
            r = client.get(url, headers={"x-user-id": "local"})
            assert r.status_code == 404, url
