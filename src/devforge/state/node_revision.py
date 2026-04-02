"""Versioned runtime revisions for state nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


RevisionStatus = Literal[
    "unknown",
    "concepted",
    "designed",
    "implementation_in_progress",
    "implemented",
    "verified",
    "blocked",
    "partial",
]


@dataclass(slots=True)
class NodeScope:
    """Current scope slice covered by a node revision."""

    projects: list[str] = field(default_factory=list)
    surfaces: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    repo_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NodeProgress:
    """Progress and evidence attached to a revision."""

    confidence: float = 0.0
    blockers: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    execution_refs: list[str] = field(default_factory=list)
    completion_signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NodeLineage:
    """Lineage information linking one revision to prior revisions."""

    supersedes: list[str] = field(default_factory=list)
    split_from: list[str] = field(default_factory=list)
    merged_from: list[str] = field(default_factory=list)
    rebound_from: list[str] = field(default_factory=list)
    derived_reason: str = ""


@dataclass(slots=True)
class NodeRevision:
    """A versioned definition/runtime view of one business-state node."""

    revision_id: str
    node_id: str
    phase: str | None = None
    status: RevisionStatus = "unknown"
    title: str = ""
    scope: NodeScope = field(default_factory=NodeScope)
    deliverables: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    related_seams: list[str] = field(default_factory=list)
    progress: NodeProgress = field(default_factory=NodeProgress)
    lineage: NodeLineage = field(default_factory=NodeLineage)
    created_at: str | None = None
    updated_at: str | None = None
