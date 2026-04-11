from pathlib import Path
from devforge.workflow.artifacts import check_artifacts


def test_check_artifacts_all_present(tmp_path: Path) -> None:
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text("{}")
    f2.write_text("{}")
    assert check_artifacts(tmp_path, ["a.json", "b.json"]) is True


def test_check_artifacts_one_missing(tmp_path: Path) -> None:
    f1 = tmp_path / "a.json"
    f1.write_text("{}")
    assert check_artifacts(tmp_path, ["a.json", "missing.json"]) is False


def test_check_artifacts_empty_list(tmp_path: Path) -> None:
    assert check_artifacts(tmp_path, []) is True


def test_check_artifacts_nested_path(tmp_path: Path) -> None:
    nested = tmp_path / "sub" / "deep.json"
    nested.parent.mkdir(parents=True)
    nested.write_text("{}")
    assert check_artifacts(tmp_path, ["sub/deep.json"]) is True


def test_check_artifacts_empty_file_returns_false(tmp_path: Path) -> None:
    f = tmp_path / "empty.json"
    f.write_text("")
    assert check_artifacts(tmp_path, ["empty.json"]) is False
