"""Orquestador: regex -> AFN -> AFD -> AFD mínimo -> resultados."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automata import AutomatonSimulator, DFAMinimizer, SubsetConstructor, ThompsonBuilder
from automata.dfa import DFA
from automata.nfa import NFA
from regex import RegexTokenizer, ShuntingYard
from visualization.graph_renderer import AutomatonRenderer


@dataclass
class AnalysisResult:
    regex: str
    postfix: list[str]
    nfa: NFA
    dfa: DFA
    minimized_dfa: DFA
    nfa_accepts: bool
    dfa_accepts: bool
    minimized_dfa_accepts: bool
    images: list[Path]


class LexicalAnalyzerPipeline:
    def analyze(self, regex: str, word: str, output_dir: str | Path, index: int = 1) -> AnalysisResult:
        postfix = ShuntingYard().to_postfix(RegexTokenizer().tokenize(regex))
        nfa = ThompsonBuilder().build(postfix)
        dfa = SubsetConstructor().convert(nfa)
        minimized = DFAMinimizer().minimize(dfa)
        simulator = AutomatonSimulator()
        renderer = AutomatonRenderer()
        output = Path(output_dir)
        images = [
            renderer.render(nfa, f"AFN - {regex}", output / f"regex_{index}_afn"),
            renderer.render(dfa, f"AFD - {regex}", output / f"regex_{index}_afd"),
            renderer.render(minimized, f"AFD minimizado - {regex}", output / f"regex_{index}_afd_min"),
        ]
        return AnalysisResult(
            regex, postfix, nfa, dfa, minimized,
            simulator.simulate_nfa(nfa, word),
            simulator.simulate_dfa(dfa, word),
            simulator.simulate_dfa(minimized, word), images,
        )
