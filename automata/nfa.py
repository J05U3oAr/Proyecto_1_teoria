"""
NFA
===
Representa un Autómata Finito No Determinista (AFN) y expone la función
de cerradura-épsilon, que reutilizan tanto la simulación del AFN como la
construcción de subconjuntos (AFN -> AFD).
"""

from __future__ import annotations

from .state import State
from regex.tokenizer import EPSILON


class NFAFragment:
    """Fragmento intermedio usado por ThompsonBuilder: un pedazo de AFN
    con exactamente un estado inicial y uno de aceptación. Los fragmentos
    se combinan (concatenación, unión, cerraduras) hasta formar el AFN
    completo de la expresión regular."""

    def __init__(self, start: State, accept: State):
        self.start = start
        self.accept = accept


class NFA:
    """AFN completo: solo un estado inicial y un estado de aceptación
    (consecuencia directa de la construcción de Thompson)."""

    def __init__(self, start: State, accept: State, alphabet: set[str]):
        self.start = start
        self.accept = accept
        self.alphabet = alphabet
        self.states = self._collect_states()

    def _collect_states(self) -> list[State]:
        visited: dict[int, State] = {}
        stack = [self.start]
        while stack:
            current = stack.pop()
            if current.id in visited:
                continue
            visited[current.id] = current
            for targets in current.transitions.values():
                for target in targets:
                    if target.id not in visited:
                        stack.append(target)
        return list(visited.values())

    def epsilon_closure(self, states: set[State]) -> set[State]:
        """Conjunto de estados alcanzables desde `states` usando
        únicamente transiciones-ε (incluyendo los propios `states`)."""
        closure = set(states)
        stack = list(states)
        while stack:
            current = stack.pop()
            for target in current.epsilon_targets():
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return closure

    def move(self, states: set[State], symbol: str) -> set[State]:
        result: set[State] = set()
        for state in states:
            result |= state.move(symbol)
        return result
