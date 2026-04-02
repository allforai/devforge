"""Stable business-state node identities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


NodeType = Literal[
    "closure",
    "feature",
    "surface",
    "seam",
    "initiative",
]

LifecycleStatus = Literal[
    "active",
    "deprecated",
    "merged",
    "archived",
]


@dataclass(slots=True)
class StateNode:
    """Stable identity for one evolving business-state line."""

    node_id: str
    node_type: NodeType
    name: str
    business_goal: str
    lifecycle_status: LifecycleStatus = "active"
    tags: list[str] = field(default_factory=list)
