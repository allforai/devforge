"""Compatibility wrapper for LangGraph.

Falls back to a minimal in-process state graph when `langgraph` is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

START = "__start__"
END = "__end__"

try:
    from langgraph.graph import END as LG_END, START as LG_START, StateGraph as LGStateGraph

    END = LG_END
    START = LG_START
    StateGraph = LGStateGraph
except ModuleNotFoundError:
    @dataclass
    class _CompiledGraph:
        nodes: dict[str, Callable[[dict[str, Any]], dict[str, Any]]]
        edges: dict[str, str]
        conditional_edges: dict[str, tuple[Callable[[dict[str, Any]], str], dict[str, str]]] = field(default_factory=dict)

        def invoke(self, initial_state: dict[str, Any]) -> dict[str, Any]:
            state = dict(initial_state)
            current = self.edges[START]
            while current != END:
                updates = self.nodes[current](state) or {}
                state.update(updates)
                if current in self.conditional_edges:
                    router, mapping = self.conditional_edges[current]
                    current = mapping[router(state)]
                else:
                    current = self.edges[current]
            return state

    class StateGraph:  # type: ignore[override]
        def __init__(self, _state_type: Any) -> None:
            self._nodes: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
            self._edges: dict[str, str] = {}
            self._conditional_edges: dict[str, tuple[Callable[[dict[str, Any]], str], dict[str, str]]] = {}

        def add_node(self, name: str, func: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
            self._nodes[name] = func

        def add_edge(self, source: str, dest: str) -> None:
            self._edges[source] = dest

        def add_conditional_edges(
            self,
            source: str,
            router: Callable[[dict[str, Any]], str],
            mapping: dict[str, str],
        ) -> None:
            self._conditional_edges[source] = (router, mapping)

        def compile(self) -> _CompiledGraph:
            return _CompiledGraph(self._nodes, self._edges, self._conditional_edges)
