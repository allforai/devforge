"""LLM-driven acceptance evaluator."""

from __future__ import annotations

import uuid
from typing import Any

from app_factory.llm import LLMClient, MockLLMClient, StructuredGenerationRequest, build_task_llm_client
from app_factory.state.acceptance import (
    AcceptanceVerdict,
    ClosureDensityScore,
    GapItem,
    GoalCheckResult,
)


def evaluate_acceptance(
    *,
    project_id: str,
    cycle_id: str,
    acceptance_goals: list[str],
    work_package_results: list[dict[str, Any]],
    design_summary: dict[str, Any],
    closure_expansion: dict[str, Any] | None = None,
    llm_client: LLMClient | None = None,
    llm_preferences: dict[str, Any] | None = None,
) -> AcceptanceVerdict:
    """Use the LLM to evaluate acceptance criteria and return an AcceptanceVerdict.

    Parameters
    ----------
    project_id:
        Identifier of the project being evaluated.
    cycle_id:
        The current orchestration cycle identifier.
    acceptance_goals:
        Human-readable acceptance goals for this cycle.
    work_package_results:
        List of work package execution results (each has at minimum ``status``).
    design_summary:
        Product design summary dict (may include ``user_flows``, ``domains``, etc.).
    closure_expansion:
        Optional closure expansion data (``total_ring_0``, ``total_ring_1``,
        ``coverage_ratio``).
    llm_client:
        LLM client to use; defaults to ``MockLLMClient`` if none available.
    llm_preferences:
        Optional preference hints forwarded to ``build_task_llm_client``.

    Returns
    -------
    AcceptanceVerdict
    """
    llm_client = (
        llm_client
        or build_task_llm_client(task="acceptance_evaluation", preferences=llm_preferences)
        or MockLLMClient()
    )

    response = llm_client.generate_structured(
        StructuredGenerationRequest(
            task="acceptance_evaluation",
            schema_name="AcceptanceVerdict",
            instructions=(
                "Evaluate the acceptance criteria for the current cycle. "
                "Check each goal against the work package results. "
                "Identify gaps and assess production readiness. "
                "Return only JSON."
            ),
            input_payload={
                "acceptance_goals": acceptance_goals,
                "work_package_results": work_package_results,
                "design_summary": design_summary,
                "closure_expansion": closure_expansion,
            },
            metadata={"project_id": project_id, "cycle_id": cycle_id},
        )
    )

    output = response.output

    # Convert goal_checks
    goal_checks: list[GoalCheckResult] = [
        GoalCheckResult(
            goal=gc.get("goal", ""),
            status=gc.get("status", "partial"),
            reason=gc.get("reason", ""),
        )
        for gc in output.get("goal_checks", [])
    ]

    # Convert gaps
    gaps: list[GapItem] = [
        GapItem(
            gap_id=g.get("gap_id", f"gap-{i}"),
            description=g.get("description", ""),
            severity=g.get("severity", "medium"),
            attributed_domain=g.get("attributed_domain", ""),
            attributed_capability=g.get("attributed_capability", ""),
            remediation_target=g.get("remediation_target", "implementation"),
        )
        for i, g in enumerate(output.get("gaps", []))
    ]

    # Convert closure_density
    closure_density: ClosureDensityScore | None = None
    cd_data = output.get("closure_density")
    if cd_data:
        closure_density = ClosureDensityScore(
            total_ring_0=int(cd_data.get("total_ring_0", 0)),
            covered=int(cd_data.get("covered", 0)),
            coverage_ratio=float(cd_data.get("coverage_ratio", 0.0)),
        )

    # role_evaluations
    role_evaluations: dict[str, str] = dict(output.get("role_evaluations", {}))

    verdict_id = f"verdict-{uuid.uuid4().hex[:8]}"

    return AcceptanceVerdict(
        verdict_id=verdict_id,
        project_id=project_id,
        cycle_id=cycle_id,
        is_production_ready=bool(output.get("is_production_ready", False)),
        overall_score=float(output.get("overall_score", 0.0)),
        goal_checks=goal_checks,
        gaps=gaps,
        closure_density=closure_density,
        role_evaluations=role_evaluations,
        summary=output.get("summary", ""),
    )
