"""
DFA
===
Representa un Autómata Finito Determinista (AFD). A diferencia del AFN,
cada estado tiene a lo sumo un destino por símbolo (sin transiciones-ε).
"""

from __future__ import annotations

from .state import State


class DFA:
    def __init__(self, start: State, states: list[State], alphabet: set[str]):
        self.start = start
        self.states = states
        self.alphabet = alphabet
        self.accept_states = {s for s in states if s.is_accept}

    def step(self, state: State, symbol: str) -> State | None:
        targets = state.transitions.get(symbol)
        if not targets:
            return None
        # Por construcción, en un AFD cada símbolo lleva a un único estado.
        return next(iter(targets))
