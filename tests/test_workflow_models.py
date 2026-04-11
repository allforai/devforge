from devforge.workflow.models import (
    NodeManifestEntry,
    NodeDefinition,
    WorkflowManifest,
    WorkflowIndex,
    WorkflowIndexEntry,
    TransitionEntry,
    PlannerOutput,
    NodeStatus,
    WorkflowStatus,
    WorkflowPhase,
)


def test_node_manifest_entry_is_dict() -> None:
    entry: NodeManifestEntry = {
        "id": "discover",
        "status": "pending",
        "depends_on": [],
        "exit_artifacts": [".devforge/artifacts/summary.json"],
        "executor": "codex",
        "mode": None,
        "parent_node_id": None,
        "depth": 0,
        "attempt_count": 0,
        "last_started_at": None,
        "last_completed_at": None,
        "last_error": None,
    }
    assert isinstance(entry, dict)
    assert entry["status"] == "pending"
    assert entry["attempt_count"] == 0
    assert entry["mode"] is None


def test_node_definition_is_dict() -> None:
    node: NodeDefinition = {
        "id": "discover",
        "capability": "discovery",
        "goal": "Scan the repo",
        "exit_artifacts": [".devforge/artifacts/summary.json"],
        "knowledge_refs": ["src/devforge/knowledge/content/capabilities/discovery.md"],
        "executor": "codex",
        "mode": None,
    }
    assert node["capability"] == "discovery"
    assert node["mode"] is None


def test_workflow_manifest_has_workflow_status() -> None:
    manifest: WorkflowManifest = {
        "id": "wf-test-001",
        "goal": "Test workflow",
        "created_at": "2026-04-11T00:00:00Z",
        "workflow_status": "running",
        "nodes": [],
    }
    assert manifest["workflow_status"] == "running"
    assert manifest["nodes"] == []


def test_workflow_index_is_dict() -> None:
    index: WorkflowIndex = {
        "schema_version": "1.0",
        "active_workflow_id": "wf-test-001",
        "workflows": [],
    }
    assert index["schema_version"] == "1.0"


def test_planner_output_is_dict() -> None:
    output: PlannerOutput = {
        "nodes": [],
        "summary": "計劃包含 0 個節點",
    }
    assert output["summary"] == "計劃包含 0 個節點"
