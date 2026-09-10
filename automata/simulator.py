"""Simulación de AFN y AFD."""

from __future__ import annotations

from .dfa import DFA
from .nfa import NFA


def _matches(symbol: str, character: str) -> bool:
    """Los escapes ya fueron decodificados al construir el autómata."""
    return symbol == character


class AutomatonSimulator:
    def simulate_nfa(self, nfa: NFA, word: str) -> bool:
        current = nfa.epsilon_closure({nfa.start})
        for character in word:
            next_states = set()
            for state in current:
                for symbol, targets in state.transitions.items():
                    if symbol != r"\~" and _matches(symbol, character):
                        next_states.update(targets)
            current = nfa.epsilon_closure(next_states)
        return nfa.accept in current

    def simulate_dfa(self, dfa: DFA, word: str) -> bool:
        current = dfa.start
        for character in word:
            target = next(
                (next(iter(targets)) for symbol, targets in current.transitions.items()
                 if _matches(symbol, character)),
                None,
            )
            if target is None:
                return False
            current = target
        return current.is_accept
