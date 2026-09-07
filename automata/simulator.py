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
            # Épsilon representa una transición que no consume entrada y no
            # forma parte del alfabeto. Lo mismo aplica a cualquier símbolo
            # desconocido recibido en la cadena.
            if symbol not in nfa.alphabet:
                return False
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
