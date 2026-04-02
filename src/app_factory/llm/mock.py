"""Mock LLM client for deterministic local development."""

from __future__ import annotations

from dataclasses import dataclass

from .models import StructuredGenerationRequest, StructuredGenerationResponse


@dataclass(slots=True)
class MockLLMClient:
    """Deterministic mock client used until a real provider is wired in."""

    provider_name: str = "mock"
    model_name: str = "mock-structured-v1"

    def generate_structured(self, request: StructuredGenerationRequest) -> StructuredGenerationResponse:
        if request.task == "concept_collection":
            output = self._concept_output(request)
            return StructuredGenerationResponse(
                output=output,
                provider=self.provider_name,
                model=self.model_name,
                raw_text=str(output),
                metadata={"task": request.task, "schema_name": request.schema_name},
            )

        if request.task == "planning_and_shaping":
            output = self._planning_output(request)
            return StructuredGenerationResponse(
                output=output,
                provider=self.provider_name,
                model=self.model_name,
                raw_text=str(output),
                metadata={"task": request.task, "schema_name": request.schema_name},
            )

        return self._retry_output(request)

    def _concept_output(self, request: StructuredGenerationRequest) -> dict[str, object]:
        payload = request.input_payload
        project = payload.get("project", {})
        specialized = payload.get("specialized_knowledge", {})
        focus = list(specialized.get("focus", []))
        if not focus:
            archetype = project.get("project_archetype")
            phase = project.get("current_phase")
            focus = [item for item in [archetype, phase] if item]
        name = project.get("name") or "project"
        return {
            "phase": project.get("current_phase"),
            "goal": f"collect concept model for {name}",
            "focus_areas": focus,
            "questions": [
                "What is the primary user experience or outcome?",
                "Which domains are core versus optional in the first iteration?",
            ],
            "required_artifacts": ["concept_brief.md", "acceptance_goals.json"],
            "rationale": "collect concept inputs before detailed planning and execution",
            "confidence": 0.76,
            "notes": [
                "concept decision derived from project archetype and selected knowledge",
                "focus areas limited for layered disclosure",
            ],
        }

    def _planning_output(self, request: StructuredGenerationRequest) -> dict[str, object]:
        payload = request.input_payload
        project = payload.get("project", {})
        workset_ids = payload.get("workset_ids", [])
        packet = payload.get("node_knowledge_packet", {})
        focus = packet.get("focus", {})
        specialized = payload.get("specialized_knowledge", {})
        return {
            "selected_workset": workset_ids,
            "phase": focus.get("phase") or project.get("current_phase"),
            "goal": packet.get("brief") or project.get("name"),
            "rationale": "selected current runnable workset using project and knowledge context",
            "confidence": 0.74,
            "notes": [
                "planning decision derived from project archetype and selected knowledge",
                "specialized focus: " + ", ".join(str(item) for item in specialized.get("focus", [])[:3]),
            ],
        }

    def _retry_output(self, request: StructuredGenerationRequest) -> StructuredGenerationResponse:
        payload = request.input_payload
        summary = str(payload.get("result", {}).get("summary", "")).lower()
        context = payload.get("context", {})
        work_package = payload.get("work_package", {})

        output = {
            "action": "requeue",
            "reason": "retry_allowed",
            "confidence": 0.72,
            "next_executor": None,
            "notes": [],
        }

        if context.get("requirement_patch_applied"):
            output |= {
                "action": "replan",
                "reason": "requirement_context_changed",
                "notes": ["recent requirement patch may invalidate implementation assumptions"],
            }
        elif ("seam" in summary or "contract" in summary) and any(
            seam.get("status") not in {"frozen", "verified"} for seam in context.get("related_seams", [])
        ):
            output |= {
                "action": "block",
                "reason": "seam_not_stable",
                "notes": ["related seam state is not stable enough for blind retry"],
            }
        elif ("rejected" in summary or len(work_package.get("execution_history", [])) >= 2) and work_package.get("fallback_executors"):
            next_executor = None
            current_executor = payload.get("result", {}).get("execution_ref", {}).get("executor") or work_package.get("executor")
            for fallback in work_package.get("fallback_executors", []):
                if fallback != current_executor:
                    next_executor = fallback
                    break
            if next_executor is not None:
                output |= {
                    "action": "switch_executor",
                    "reason": "unsupported_by_executor" if "rejected" in summary else "repeated_executor_failure",
                    "next_executor": next_executor,
                    "notes": ["executor mismatch or repeated failures suggest switching executor"],
                }

        return StructuredGenerationResponse(
            output=output,
            provider=self.provider_name,
            model=self.model_name,
            raw_text=str(output),
            metadata={"task": request.task, "schema_name": request.schema_name},
        )
