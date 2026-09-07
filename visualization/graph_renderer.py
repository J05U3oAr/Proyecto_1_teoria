"""
AutomatonRenderer
==================
Genera una imagen (PNG) del grafo de un autómata (AFN o AFD) usando la
librería graphviz: estado inicial (con una flecha de entrada), estados
normales (círculo) y estados de aceptación (doble círculo).
"""

from __future__ import annotations

import graphviz

from automata.nfa import NFA
from automata.dfa import DFA


class AutomatonRenderer:
    def render(
        self,
        automaton: NFA | DFA,
        filename: str,
        directory: str = ".",
        title: str | None = None,
    ) -> str:
        states, start, accept_states = self._extract(automaton)

        graph = graphviz.Digraph(format="png")
        graph.attr(rankdir="LR")
        if title:
            graph.attr(label=title, labelloc="t", fontsize="14")

        # Nodo invisible + flecha de entrada al estado inicial
        graph.node("__start__", shape="point", width="0.05")
        graph.edge("__start__", str(start.id))

        for state in states:
            shape = "doublecircle" if state in accept_states else "circle"
            graph.node(str(state.id), label=state.label, shape=shape)

        for (src_id, dst_id), symbols in self._grouped_edges(states).items():
            graph.edge(str(src_id), str(dst_id), label=", ".join(sorted(symbols)))

        return graph.render(filename=filename, directory=directory, cleanup=True)

    # ------------------------------------------------------------------
    def _extract(self, automaton: NFA | DFA):
        if isinstance(automaton, NFA):
            return automaton.states, automaton.start, {automaton.accept}
        if isinstance(automaton, DFA):
            return automaton.states, automaton.start, automaton.accept_states
        raise TypeError("automaton debe ser una instancia de NFA o DFA")

    def _grouped_edges(self, states) -> dict[tuple[int, int], list[str]]:
        """Agrupa los símbolos que comparten el mismo par (origen, destino)
        para no dibujar una arista repetida por cada símbolo."""
        edges: dict[tuple[int, int], list[str]] = {}
        for state in states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    key = (state.id, target.id)
                    edges.setdefault(key, []).append(symbol)
        return edges
