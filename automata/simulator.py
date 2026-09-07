"""
AutomatonSimulator
===================
Simula una cadena w sobre un AFN o un AFD para determinar si
w pertenece al lenguaje aceptado por el autómata.
"""

from __future__ import annotations

from .nfa import NFA
from .dfa import DFA


class AutomatonSimulator:
    def simulate_nfa(self, nfa: NFA, w: str) -> bool:
        current = nfa.epsilon_closure({nfa.start})
        for symbol in w:
            current = nfa.epsilon_closure(nfa.move(current, symbol))
            if not current:
                return False
        return nfa.accept in current

    def simulate_dfa(self, dfa: DFA, w: str) -> bool:
        current = dfa.start
        for symbol in w:
            next_state = dfa.step(current, symbol)
            if next_state is None:
                return False
            current = next_state
        return current.is_accept
