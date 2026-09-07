"""Minimización de AFD por refinamiento de particiones."""

from __future__ import annotations

from .dfa import DFA
from .state import State


class DFAMinimizer:
    """Construye un AFD equivalente con estados indistinguibles unidos.

    Los AFD producidos por subconjuntos pueden ser parciales. Antes de
    minimizar se completan con un estado trampa no aceptante, requisito para
    que dos estados que solo difieren por una transición omitida se comparen
    correctamente.
    """

    def minimize(self, dfa: DFA) -> DFA:
        original_states = list(dfa.states)
        sink: State | None = None
        if dfa.alphabet and any(
            dfa.step(state, symbol) is None
            for state in original_states
            for symbol in dfa.alphabet
        ):
            sink = State(is_accept=False, label="trap")
        all_states = original_states + ([sink] if sink is not None else [])

        def transition(state: State, symbol: str) -> State:
            if state is sink:
                return sink
            return dfa.step(state, symbol) or sink  # type: ignore[return-value]

        accepting = set(dfa.accept_states)
        rejecting = set(all_states) - accepting
        partitions = [group for group in (accepting, rejecting) if group]

        while True:
            state_to_group = {
                state: index
                for index, group in enumerate(partitions)
                for state in group
            }
            refined: list[set[State]] = []
            changed = False
            for group in partitions:
                buckets: dict[tuple[int | None, ...], set[State]] = {}
                for state in group:
                    signature = tuple(state_to_group[transition(state, symbol)] for symbol in sorted(dfa.alphabet))
                    buckets.setdefault(signature, set()).add(state)
                refined.extend(buckets.values())
                changed |= len(buckets) > 1
            partitions = refined
            if not changed:
                break

        state_to_group = {
            state: index
            for index, group in enumerate(partitions)
            for state in group
        }
        states = [
            State(
                is_accept=any(state.is_accept for state in group),
                label=f"M{index}",
            )
            for index, group in enumerate(partitions)
        ]
        for index, group in enumerate(partitions):
            representative = next(iter(group))
            for symbol in sorted(dfa.alphabet):
                target = transition(representative, symbol)
                states[index].add_transition(symbol, states[state_to_group[target]])
        return DFA(states[state_to_group[dfa.start]], states, set(dfa.alphabet))
