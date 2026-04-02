# tests/test_e2e_ecommerce_fixture.py
"""Tests for the e-commerce scenario snapshot factory."""

from tests.fixtures.e2e_ecommerce_snapshot import make_ecommerce_snapshot


def test_snapshot_has_initiative():
    snap = make_ecommerce_snapshot()
    assert snap["initiative"]["initiative_id"] == "ecom-001"
    assert snap["initiative"]["status"] == "active"


def test_snapshot_has_project():
    snap = make_ecommerce_snapshot()
    projects = snap["projects"]
    assert len(projects) >= 1
    assert projects[0]["project_archetype"] == "ecommerce"


def test_snapshot_has_work_packages():
    snap = make_ecommerce_snapshot()
    wps = snap["work_packages"]
    assert len(wps) >= 5
    ready_count = sum(1 for wp in wps if wp["status"] == "ready")
    assert ready_count >= 3


def test_snapshot_has_seams():
    snap = make_ecommerce_snapshot()
    seams = snap["seams"]
    assert len(seams) >= 1
    assert seams[0]["status"] == "frozen"


def test_snapshot_has_executor_policies():
    snap = make_ecommerce_snapshot()
    assert len(snap["executor_policies"]) >= 1
