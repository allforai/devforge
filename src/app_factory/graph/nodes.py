"""Minimal meta-graph node functions."""

from __future__ import annotations

from dataclasses import asdict

from app_factory.llm import LLMClient
from app_factory.graph.runtime_state import RuntimeState
from app_factory.planning import llm_concept_collection_decider, llm_planning_decider


def project_scheduler_node(state: RuntimeState) -> RuntimeState:
    """Move the foreground project into the active slot when needed."""
    if state.foreground_project and not state.active_project_id:
        state.active_project_id = state.foreground_project
    return state


def concept_collection_node(
    state: RuntimeState,
    *,
    project: dict[str, object] | None = None,
    knowledge_ids: list[str] | None = None,
    specialized_knowledge: dict[str, object] | None = None,
    llm_client: LLMClient | None = None,
    llm_preferences: dict[str, object] | None = None,
) -> RuntimeState:
    """Attach a concept collection decision to the runtime state."""
    selected_knowledge = knowledge_ids or []
    specialized = specialized_knowledge or {}
    decision = llm_concept_collection_decider(
        project=project or {},
        selected_knowledge=selected_knowledge,
        specialized_knowledge=specialized,
        llm_client=llm_client,
        llm_preferences=llm_preferences,
    )
    state.selected_knowledge = selected_knowledge
    state.specialized_knowledge = specialized
    state.concept_decision = asdict(decision)
    state.current_phase = decision.phase or state.current_phase
    state.phase_goal = decision.goal or state.phase_goal
    return state


def planning_and_shaping_node(
    state: RuntimeState,
    workset_ids: list[str],
    *,
    project: dict[str, object] | None = None,
    knowledge_ids: list[str] | None = None,
    specialized_knowledge: dict[str, object] | None = None,
    node_knowledge_packet: dict[str, object] | None = None,
    llm_client: LLMClient | None = None,
    llm_preferences: dict[str, object] | None = None,
) -> RuntimeState:
    """Attach a newly planned workset to the runtime state."""
    selected_knowledge = knowledge_ids or []
    specialized = specialized_knowledge or {}
    packet = node_knowledge_packet or {}
    decision = llm_planning_decider(
        project=project or {},
        workset_ids=workset_ids,
        selected_knowledge=selected_knowledge,
        specialized_knowledge=specialized,
        node_knowledge_packet=packet,
        llm_client=llm_client,
        llm_preferences=llm_preferences,
    )
    state.current_workset = decision.selected_workset
    state.selected_knowledge = selected_knowledge
    state.specialized_knowledge = specialized
    state.node_knowledge_packet = packet
    state.planning_decision = asdict(decision)
    state.current_phase = decision.phase or state.current_phase
    state.phase_goal = decision.goal or state.phase_goal
    state.replan_reason = None
    return state


def graph_validation_node(state: RuntimeState) -> RuntimeState:
    """Set a replan reason when the current workset is empty."""
    if not state.current_workset:
        state.replan_reason = "no_runnable_work"
    return state
