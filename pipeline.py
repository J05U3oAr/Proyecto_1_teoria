"""
LexicalAnalyzerPipeline
========================
Clase orquestadora: encadena tokenización, Shunting Yard, construcción
de Thompson, construcción de subconjuntos, minimización, renderizado de
los tres autómatas y simulación de la cadena w sobre cada uno.
"""

from __future__ import annotations

from dataclasses import dataclass

from regex.tokenizer import RegexTokenizer
from regex.shunting_yard import ShuntingYard
from automata.thompson import ThompsonBuilder
from automata.subset_construction import SubsetConstructor
from automata.minimizer import DFAMinimizer
from automata.simulator import AutomatonSimulator
from automata.nfa import NFA
from automata.dfa import DFA
from visualization.graph_renderer import AutomatonRenderer


@dataclass
class ProcessingResult:
    regex: str
    w: str
    postfix: list[str]
    nfa: NFA
    dfa: DFA
    min_dfa: DFA
    nfa_accepts: bool
    dfa_accepts: bool
    min_dfa_accepts: bool
    nfa_image: str
    dfa_image: str
    min_dfa_image: str


class LexicalAnalyzerPipeline:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.tokenizer = RegexTokenizer()
        self.shunting_yard = ShuntingYard()
        self.thompson = ThompsonBuilder()
        self.subset_constructor = SubsetConstructor()
        self.minimizer = DFAMinimizer()
        self.simulator = AutomatonSimulator()
        self.renderer = AutomatonRenderer()

    def process(self, regex: str, w: str, index: int = 0) -> ProcessingResult:
        tokens = self.tokenizer.tokenize(regex)
        postfix = self.shunting_yard.to_postfix(tokens)

        nfa = self.thompson.build(postfix)
        dfa = self.subset_constructor.convert(nfa)
        min_dfa = self.minimizer.minimize(dfa)

        nfa_accepts = self.simulator.simulate_nfa(nfa, w)
        dfa_accepts = self.simulator.simulate_dfa(dfa, w)
        min_dfa_accepts = self.simulator.simulate_dfa(min_dfa, w)

        base = f"regex_{index}"
        nfa_image = self.renderer.render(
            nfa, f"{base}_afn", directory=self.output_dir, title=f"AFN — {regex}"
        )
        dfa_image = self.renderer.render(
            dfa, f"{base}_afd", directory=self.output_dir, title=f"AFD — {regex}"
        )
        min_dfa_image = self.renderer.render(
            min_dfa,
            f"{base}_afd_min",
            directory=self.output_dir,
            title=f"AFD minimizado — {regex}",
        )

        return ProcessingResult(
            regex=regex,
            w=w,
            postfix=postfix,
            nfa=nfa,
            dfa=dfa,
            min_dfa=min_dfa,
            nfa_accepts=nfa_accepts,
            dfa_accepts=dfa_accepts,
            min_dfa_accepts=min_dfa_accepts,
            nfa_image=nfa_image,
            dfa_image=dfa_image,
            min_dfa_image=min_dfa_image,
        )
