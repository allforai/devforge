# tests/test_e2e_game_fixture.py
"""Tests for the game scenario snapshot factory."""

from tests.fixtures.e2e_game_snapshot import make_game_snapshot


def test_game_snapshot_has_initiative():
    snap = make_game_snapshot()
    assert snap["initiative"]["initiative_id"] == "game-001"


def test_game_snapshot_has_project():
    snap = make_game_snapshot()
    assert snap["projects"][0]["project_archetype"] == "gaming"


def test_game_snapshot_has_work_packages():
    snap = make_game_snapshot()
    assert len(snap["work_packages"]) >= 4


def test_game_snapshot_with_split():
    snap = make_game_snapshot(with_project_split=True)
    assert len(snap["projects"]) >= 2
    assert len(snap["seams"]) >= 1


def test_game_snapshot_with_requirement_change():
    snap = make_game_snapshot(with_requirement_change=True)
    assert len(snap["requirement_events"]) >= 1
    assert snap["requirement_events"][0]["type"] == "add"
