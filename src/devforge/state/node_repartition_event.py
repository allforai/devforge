"""Events describing node repartition and lineage changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


RepartitionType = Literal[
    "node_revised",
    "node_split",
    "node_merge",
    "node_deprecated",
    "node_rebound",
]

TriggerType = Literal[
    "information_input",
    "execution_result",
    "manual_adjustment",
    "state_recompute",
]


@dataclass(slots=True)
class RepartitionImpact:
    """Planning/runtime impact caused by a repartition event."""

    topology_changed: bool = False
    closure_map_changed: bool = False
    planning_required: bool = True
    affected_work_packages: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NodeRepartitionEvent:
    """One explicit event describing how node boundaries changed."""

    event_id: str
    event_type: RepartitionType
    trigger_type: TriggerType
    trigger_ref: str | None = None
    reason: str = ""
    before_revision_ids: list[str] = field(default_factory=list)
    after_revision_ids: list[str] = field(default_factory=list)
    impact: RepartitionImpact = field(default_factory=RepartitionImpact)
    created_at: str | None = None
