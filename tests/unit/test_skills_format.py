from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parents[2] / "skills"

EXPECTED = {"arch-design", "aliyun-waf", "sa-playbooks"}


def test_every_skill_has_valid_frontmatter():
    found = set()
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        found.add(skill_dir.name)
        fm = (skill_dir / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        meta = yaml.safe_load(fm)
        assert meta["name"] == skill_dir.name, skill_dir.name
        assert len(meta["description"]) > 10
    assert found == EXPECTED
