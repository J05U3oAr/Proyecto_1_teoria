"""
DFAMinimizer
============
Minimiza un AFD mediante particionamiento por equivalencia de estados
(algoritmo de Moore / refinamiento de particiones).

Una transición no definida se trata, para efectos de la comparación de
equivalencia, como si llevara a una clase-fantasma de "rechazo" fija
(un sumidero conceptual que nunca cambia de clase). Esto evita tener
que agregar un estado sumidero explícito al autómata minimizado
resultante: si el AFD original era parcial, el minimizado también lo
será, con exactamente el mismo comportamiento de aceptación/rechazo.
"""

from __future__ import annotations

from .state import State
from .dfa import DFA

_PHANTOM_REJECT = -1  # clase fija para "no hay transición definida"


class DFAMinimizer:
    def minimize(self, dfa: DFA) -> DFA:
        alphabet = sorted(dfa.alphabet)
        states = list(dfa.states)

        accept = [s for s in states if s.is_accept]
        nonaccept = [s for s in states if not s.is_accept]
        partition: list[list[State]] = [g for g in (accept, nonaccept) if g]

        changed = True
        while changed:
            changed = False
            membership = self._membership_map(partition)

            new_partition: list[list[State]] = []
            for group in partition:
                buckets: dict[tuple, list[State]] = {}
                for s in group:
                    signature = tuple(
                        self._group_of(dfa.step(s, sym), membership)
                        for sym in alphabet
                    )
                    buckets.setdefault(signature, []).append(s)
                if len(buckets) > 1:
                    changed = True
                new_partition.extend(buckets.values())
            partition = new_partition

        return self._build_minimized_dfa(dfa, partition, alphabet)

    # ------------------------------------------------------------------
    def _membership_map(self, partition: list[list[State]]) -> dict[int, int]:
        membership: dict[int, int] = {}
        for group_index, group in enumerate(partition):
            for state in group:
                membership[state.id] = group_index
        return membership

    def _group_of(self, state: State | None, membership: dict[int, int]) -> int:
        if state is None:
            return _PHANTOM_REJECT
        return membership[state.id]

    def _build_minimized_dfa(
        self, dfa: DFA, partition: list[list[State]], alphabet: list[str]
    ) -> DFA:
        membership = self._membership_map(partition)

        new_states: list[State] = []
        for group_index, group in enumerate(partition):
            representative = group[0]
            new_states.append(
                State(is_accept=representative.is_accept, label=f"M{group_index}")
            )

        for group_index, group in enumerate(partition):
            representative = group[0]
            for symbol in alphabet:
                target = dfa.step(representative, symbol)
                if target is not None:
                    target_group = membership[target.id]
                    new_states[group_index].add_transition(symbol, new_states[target_group])

        start_group = membership[dfa.start.id]
        return DFA(new_states[start_group], new_states, set(dfa.alphabet))
