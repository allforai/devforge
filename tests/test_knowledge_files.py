from pathlib import Path

KNOWLEDGE_ROOT = Path(__file__).parent.parent / "knowledge" / "testing"


def test_profile_rules_exists():
    assert (KNOWLEDGE_ROOT / "profile-rules.md").exists()


def test_profile_rules_has_required_sections():
    content = (KNOWLEDGE_ROOT / "profile-rules.md").read_text()
    for section in ["## 目标", "## Step 1", "## Step 2", "## Step 3", "## Step 4", "## Step 5"]:
        assert section in content, f"缺少章节: {section}"
    # Load-bearing content per section
    assert "tech-profile.json" in content  # Step 5 output
    assert "data-testid" in content         # Step 2 Web locator
    assert "backend_modules" in content     # Step 4 multi-module
    assert "covered" in content             # Step 3 coverage levels


def test_helper_rules_exists():
    assert (KNOWLEDGE_ROOT / "helper-rules.md").exists()


def test_helper_rules_has_8_rules():
    content = (KNOWLEDGE_ROOT / "helper-rules.md").read_text()
    for i in range(1, 9):
        assert f"**规则 {i}：" in content, f"缺少规则 {i}"


def test_helper_rules_has_coverage_matrix():
    content = (KNOWLEDGE_ROOT / "helper-rules.md").read_text()
    for level in ["covered", "partial", "uncovered"]:
        assert level in content, f"缺少覆盖程度: {level}"
