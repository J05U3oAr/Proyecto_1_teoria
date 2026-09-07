"""
SubsetConstructor
==================
Convierte un AFN en un AFD equivalente mediante el algoritmo de
construcción de subconjuntos (cada estado del AFD es un conjunto de
estados del AFN).
"""

from __future__ import annotations

from collections import deque

from .state import State
from .nfa import NFA
from .dfa import DFA


class SubsetConstructor:
    def convert(self, nfa: NFA) -> DFA:
        start_set = frozenset(nfa.epsilon_closure({nfa.start}))
        dfa_states: dict[frozenset, State] = {}

        def get_or_create(nfa_state_set: frozenset) -> tuple[State, bool]:
            """Regresa el State del AFD para ese conjunto de estados del
            AFN, creándolo si es la primera vez que aparece. El segundo
            valor indica si fue recién creado (para encolarlo)."""
            if nfa_state_set in dfa_states:
                return dfa_states[nfa_state_set], False
            is_accept = nfa.accept in nfa_state_set
            label = f"D{len(dfa_states)}"
            new_state = State(is_accept=is_accept, label=label)
            dfa_states[nfa_state_set] = new_state
            return new_state, True

        start_state, _ = get_or_create(start_set)
        queue: deque[frozenset] = deque([start_set])
        visited: set[frozenset] = {start_set}

        while queue:
            current_set = queue.popleft()
            current_dfa_state = dfa_states[current_set]

            for symbol in sorted(nfa.alphabet):
                moved = nfa.move(set(current_set), symbol)
                if not moved:
                    continue
                target_set = frozenset(nfa.epsilon_closure(moved))
                target_state, is_new = get_or_create(target_set)
                current_dfa_state.add_transition(symbol, target_state)
                if is_new or target_set not in visited:
                    if target_set not in visited:
                        visited.add(target_set)
                        queue.append(target_set)

        return DFA(start_state, list(dfa_states.values()), set(nfa.alphabet))
