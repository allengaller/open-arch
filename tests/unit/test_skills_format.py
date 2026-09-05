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
        },
    }
    for name, files in expected_content.items():
        for rel in files:
            assert (SKILLS_DIR / name / rel).exists(), f"{name}/{rel}"
