import re
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parents[2] / "skills"

EXPECTED = {
    "arch-design",
    "aliyun-waf",
    "sa-playbooks",
    "cloud-frameworks",
    "sa-concepts",
    "cloud-sa-playbook",
    "sa-perspectives",
    "sa-strategy",
}


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


def test_referenced_content_files_exist():
    expected_content = {
        "arch-design": {"content/patterns.md", "content/decision-tree.md"},
        "sa-playbooks": {"content/cloud-assessment.md", "content/cost-optimization.md"},
        "cloud-frameworks": {
            "content/aws-caf.md",
            "content/aliyun-landing-zone.md",
            "content/well-architected.md",
            "content/cross-cloud-mapping.md",
            "checklist.yaml",
        },
        "sa-concepts": {
            "content/cloud-basics.md",
            "content/networking.md",
            "content/compute.md",
            "content/storage-db.md",
            "content/architecture-principles.md",
            "content/resilience.md",
            "content/security-compliance.md",
            "content/observability-ops.md",
            "content/cost-finops.md",
            "content/data-ai.md",
        },
        "cloud-sa-playbook": {
            "content/acquisition-channels.md",
            "content/iron-triangle.md",
            "content/requirement-and-solution.md",
            "content/poc-playbook.md",
            "content/bidding-support.md",
            "content/migration-playbook.md",
            "content/account-deepening.md",
            "content/competitive-strategy.md",
            "content/ai-solutions.md",
            "content/enablement-influence.md",
            "content/industry-compliance.md",
            "content/global-expansion.md",
            "content/capability-model.md",
            "content/customer-segments.md",
            "content/customer-situations.md",
            "content/scenario-playbooks.md",
            "content/self-playbook.md",
            "content/internal-process.md",
            "checklist.yaml",
        },
        "sa-perspectives": {
            "content/customer-views.md",
            "content/sa-team-views.md",
            "content/sales-views.md",
            "content/product-views.md",
            "content/service-views.md",
        },
        "sa-strategy": {
            "content/strategy-framework.md",
            "content/deal-strategy.md",
            "content/account-strategy.md",
        },
    }
    for name, files in expected_content.items():
        for rel in files:
            assert (SKILLS_DIR / name / rel).exists(), f"{name}/{rel}"


# 知识文档里的反引号路径引用必须可解析，共四种写法：
#   ① `包名` 技能的 `路径`   ② `包名/content/xx.md` 合写
#   ③ `content/...`、`checklist.yaml`、`SKILL.md`（本包内）   ④ `name.md`（同目录）
_KNOW_SUFFIX = r"[\w./-]+\.(?:md|yaml|yml)"
_PACKS = "|".join(sorted(EXPECTED, key=len, reverse=True))  # 长名优先，避免前缀误匹配
_CROSS_REF = re.compile(rf"`({_PACKS})`\s*技能的\s*`({_KNOW_SUFFIX})`")
_COMBINED_REF = re.compile(rf"`((?:{_PACKS})/(?:content/)?{_KNOW_SUFFIX})`")
_PATH_REF = re.compile(rf"`({_KNOW_SUFFIX})`")


def test_knowledge_references_resolve():
    for md in sorted(SKILLS_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        covered: list[tuple[int, int]] = []
        for m in _CROSS_REF.finditer(text):
            covered.append(m.span())
            assert (SKILLS_DIR / m.group(1) / m.group(2)).exists(), f"{md}: {m.group(0)}"
        for m in _COMBINED_REF.finditer(text):
            covered.append(m.span())
            assert (SKILLS_DIR / m.group(1)).exists(), f"{md}: {m.group(0)}"
        for m in _PATH_REF.finditer(text):
            if any(s <= m.start() < e for s, e in covered):
                continue
            rel = m.group(1)
            if "/" in rel:
                # content/...、checklist.yaml、SKILL.md：相对技能包根
                target = md.parent / rel
            else:
                # 裸文件名：同目录优先，否则在包内任意位置查找
                same_dir = md.parent / rel
                target = same_dir if same_dir.exists() else next(iter(md.parent.rglob(rel)), same_dir)
            assert target.exists(), f"{md}: {rel}"
