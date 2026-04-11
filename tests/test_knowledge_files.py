from pathlib import Path

KNOWLEDGE_ROOT = Path("knowledge/testing")


def test_profile_rules_exists():
    assert (KNOWLEDGE_ROOT / "profile-rules.md").exists()


def test_profile_rules_has_required_sections():
    content = (KNOWLEDGE_ROOT / "profile-rules.md").read_text()
    for section in ["## 目标", "## Step 1", "## Step 2", "## Step 3", "## Step 4", "## Step 5"]:
        assert section in content, f"缺少章节: {section}"
