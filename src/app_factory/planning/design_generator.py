"""LLM-driven product design generator."""

from __future__ import annotations

import uuid
from typing import Any

from app_factory.llm import LLMClient, MockLLMClient, StructuredGenerationRequest, build_task_llm_client
from app_factory.state.design import (
    DomainSpec,
    InteractionMatrixEntry,
    ProductDesign,
    UserFlow,
)


def generate_product_design(
    *,
    concept: dict[str, Any],
    project: dict[str, Any],
    knowledge_ids: list[str] | None = None,
    llm_client: LLMClient | None = None,
    llm_preferences: dict[str, Any] | None = None,
) -> ProductDesign:
    """Call the LLM with task='product_design' and return a ProductDesign dataclass."""

    llm_client = (
        llm_client
        or build_task_llm_client(task="product_design", preferences=llm_preferences)
        or MockLLMClient()
    )

    response = llm_client.generate_structured(
        StructuredGenerationRequest(
            task="product_design",
            schema_name="ProductDesign",
            instructions=(
                "Generate a structured product design based on the concept and project. "
                "Include domains, user flows, interaction matrix, non-functional requirements, "
                "tech choices, and ring_0_tasks. Return only JSON."
            ),
            input_payload={
                "concept": concept,
                "project": project,
                "knowledge_ids": knowledge_ids or [],
            },
            metadata={"decision_kind": "product_design"},
        )
    )

    output = response.output

    domains = [
        DomainSpec(
            domain_id=d["domain_id"],
            name=d["name"],
            purpose=d["purpose"],
            inputs=list(d.get("inputs", [])),
            outputs=list(d.get("outputs", [])),
            dependencies=list(d.get("dependencies", [])),
        )
        for d in output.get("domains", [])
    ]

    user_flows = [
        UserFlow(
            flow_id=f["flow_id"],
            name=f["name"],
            role=f["role"],
            steps=list(f.get("steps", [])),
            entry_point=f.get("entry_point", ""),
            exit_point=f.get("exit_point", ""),
        )
        for f in output.get("user_flows", [])
    ]

    interaction_matrix = [
        InteractionMatrixEntry(
            feature=e["feature"],
            role=e["role"],
            frequency=e["frequency"],
            user_volume=e["user_volume"],
            principle=e.get("principle", ""),
        )
        for e in output.get("interaction_matrix", [])
    ]

    project_id = project.get("id") or project.get("project_id") or "unknown"
    initiative_id = project.get("initiative_id") or project_id

    return ProductDesign(
        design_id=f"D-{uuid.uuid4().hex[:8]}",
        initiative_id=initiative_id,
        project_id=project_id,
        product_name=output.get("product_name", ""),
        problem_statement=output.get("problem_statement", ""),
        target_users=list(output.get("target_users", [])),
        domains=domains,
        user_flows=user_flows,
        interaction_matrix=interaction_matrix,
        non_functional_requirements=list(output.get("non_functional_requirements", [])),
        tech_choices=dict(output.get("tech_choices", {})),
        ring_0_tasks=list(output.get("ring_0_tasks", [])),
    )
