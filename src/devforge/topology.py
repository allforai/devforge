"""Business-project topology classification models and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devforge.llm.base import LLMClient
from devforge.llm.config_loader import load_llm_config
from devforge.llm.models import StructuredGenerationRequest
from devforge.llm.router import build_task_llm_client


@dataclass(slots=True)
class WorkspaceCandidate:
    """One discovered repository candidate under a workspace root."""

    project_id: str
    name: str
    repo_path: str
    markers: list[str] = field(default_factory=list)
    readme_excerpt: str = ""


@dataclass(slots=True)
class WorkspaceModelingDecision:
    """LLM decision for modeling discovered repositories."""

    mode: str
    business_project_name: str
    business_project_id: str
    surfaces: list[dict[str, Any]] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source: str = "unknown"


def default_live_llm_preferences(search_dir: str | Path) -> dict[str, Any]:
    """Load live LLM config when available; otherwise use a sensible live default."""
    preferences = load_llm_config(search_dir=search_dir)
    if preferences:
        preferences.setdefault("allow_live", True)
        return preferences
    return {
        "allow_live": True,
        "provider": "google",
        "model": "gemini-3.1-pro-preview",
    }


def classify_workspace_candidates(
    *,
    workspace_name: str,
    candidates: list[WorkspaceCandidate],
    llm_client: LLMClient | None = None,
    llm_preferences: dict[str, Any] | None = None,
) -> WorkspaceModelingDecision:
    """Use an LLM to decide whether candidates form one business project or a workspace."""
    llm_client = llm_client or build_task_llm_client(task="workspace_modeling", preferences=llm_preferences)
    response = llm_client.generate_structured(
        StructuredGenerationRequest(
            task="workspace_modeling",
            schema_name="WorkspaceModelingDecision",
            instructions=(
                "You are deciding how to model a codebase for DevForge onboarding.\n"
                "Judge business relationship, not build system boundaries.\n"
                "If multiple repositories look like different surfaces of the same product, return mode=single_project.\n"
                "If they look like distinct business projects, return mode=workspace.\n"
                "Return JSON with exact fields:\n"
                '- "mode": string, one of "single_project" or "workspace"\n'
                '- "business_project_name": string\n'
                '- "business_project_id": string\n'
                '- "surfaces": array of objects with fields: "surface_id", "label", "paths"\n'
                '- "projects": array of objects with fields: "project_id", "label", "paths"\n'
                '- "reasoning": array of short strings\n'
                '- "confidence": number between 0 and 1\n'
                "For single_project, surfaces should be populated and projects should be empty.\n"
                "For workspace, projects should be populated and surfaces may be empty.\n"
                "Prefer single_project when names share a product prefix and appear to be admin/api/ios/web variants of one product."
            ),
            input_payload={
                "workspace_name": workspace_name,
                "candidates": [
                    {
                        "project_id": item.project_id,
                        "name": item.name,
                        "repo_path": item.repo_path,
                        "markers": item.markers,
                        "readme_excerpt": item.readme_excerpt,
                    }
                    for item in candidates
                ],
            },
            metadata={"decision_kind": "workspace_modeling"},
        )
    )
    output = response.output
    return WorkspaceModelingDecision(
        mode=str(output.get("mode", "single_project")),
        business_project_name=str(output.get("business_project_name", workspace_name)),
        business_project_id=str(output.get("business_project_id", "project")),
        surfaces=list(output.get("surfaces", [])),
        projects=list(output.get("projects", [])),
        reasoning=list(output.get("reasoning", [])),
        confidence=float(output.get("confidence", 0.0)),
        source=f"{response.provider}:{response.model}",
    )


def dump_decision(decision: WorkspaceModelingDecision) -> dict[str, Any]:
    """Serialize a modeling decision into plain JSON-ready data."""
    return {
        "mode": decision.mode,
        "business_project_name": decision.business_project_name,
        "business_project_id": decision.business_project_id,
        "surfaces": decision.surfaces,
        "projects": decision.projects,
        "reasoning": decision.reasoning,
        "confidence": decision.confidence,
        "source": decision.source,
    }
