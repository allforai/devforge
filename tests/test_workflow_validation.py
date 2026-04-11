import pytest
from devforge.workflow.models import NodeDefinition
from devforge.workflow.validation import validate_workflow


def _node(
    node_id: str,
    depends_on: list[str] | None = None,
    executor: str = "codex",
    mode: str | None = None,
) -> NodeDefinition:
    return {
        "id": node_id,
        "capability": "discovery",
        "goal": f"Run {node_id}",
        "exit_artifacts": [],
        "knowledge_refs": [],
        "executor": executor,
        "mode": mode,
        "depends_on": depends_on if depends_on is not None else [],
    }


def test_valid_linear_graph_passes() -> None:
    nodes = [_node("a"), _node("b", depends_on=["a"]), _node("c", depends_on=["b"])]
    validate_workflow(nodes)  # no exception


def test_duplicate_ids_raise() -> None:
    nodes = [_node("a"), _node("a")]
    with pytest.raises(ValueError, match="duplicate"):
        validate_workflow(nodes)


def test_missing_dependency_raises() -> None:
    nodes = [_node("b", depends_on=["nonexistent"])]
    with pytest.raises(ValueError, match="nonexistent"):
        validate_workflow(nodes)


def test_self_dependency_raises() -> None:
    nodes = [_node("a", depends_on=["a"])]
    with pytest.raises(ValueError, match="self"):
        validate_workflow(nodes)


def test_cyclic_dependency_raises() -> None:
    nodes = [_node("a", depends_on=["b"]), _node("b", depends_on=["a"])]
    with pytest.raises(ValueError, match="cycl"):
        validate_workflow(nodes)


def test_invalid_executor_raises() -> None:
    nodes = [_node("a", executor="invalid_executor")]
    with pytest.raises(ValueError, match="executor"):
        validate_workflow(nodes)


def test_empty_graph_passes() -> None:
    validate_workflow([])  # no exception
