"""Renderizado con Graphviz de AFN y AFD."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from graphviz import Digraph

from automata.dfa import DFA
from automata.nfa import NFA


class AutomatonRenderer:
    def render(self, automaton: NFA | DFA, title: str, output_path: str | Path) -> Path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        graph = Digraph(name=destination.stem, format="png")
        graph.attr(rankdir="LR", label=title, labelloc="t", fontsize="18")
        graph.attr("node", shape="circle", fontname="Arial")
        graph.node("__start__", "", shape="point")
        graph.edge("__start__", str(automaton.start.id))
        states = automaton.states
        for state in states:
            graph.node(
                str(state.id), state.label,
                shape="doublecircle" if state.is_accept else "circle",
            )
        labels: dict[tuple[int, int], list[str]] = defaultdict(list)
        for state in states:
            for symbol, targets in state.transitions.items():
                for target in targets:
                    labels[(state.id, target.id)].append(symbol)
        for (origin, target), symbols in labels.items():
            # DOT consume una barra invertida en una etiqueta. Duplicarla
            # conserva la notación visible de epsilon como ``\~``.
            visible_symbols = [symbol.replace("\\", "\\\\") for symbol in sorted(symbols)]
            graph.edge(str(origin), str(target), label=", ".join(visible_symbols))
        rendered = graph.render(filename=destination.stem, directory=str(destination.parent), cleanup=True)
        return Path(rendered)
