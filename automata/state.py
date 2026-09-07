"""
State
=====
Representa un estado de un autómata. Se usa tanto para AFN (donde una
misma etiqueta puede llevar a varios estados, y existen transiciones-ε)
como para AFD (donde cada etiqueta lleva a un único estado).
"""

from __future__ import annotations

import itertools

from regex.tokenizer import EPSILON


class State:
    """Un estado de un autómata finito.

    Las transiciones se guardan siempre como `dict[str, set[State]]`
    para poder reutilizar la misma clase en AFN y AFD: en un AFD cada
    conjunto de destino simplemente tendrá tamaño 1.
    """

    _id_counter = itertools.count()

    def __init__(self, is_accept: bool = False, label: str | None = None):
        self.id = next(State._id_counter)
        self.is_accept = is_accept
        self.label = label if label is not None else f"q{self.id}"
        self.transitions: dict[str, set["State"]] = {}

    def add_transition(self, symbol: str, target: "State") -> None:
        self.transitions.setdefault(symbol, set()).add(target)

    def move(self, symbol: str) -> set["State"]:
        """Estados alcanzables desde este estado consumiendo `symbol`."""
        return set(self.transitions.get(symbol, set()))

    def epsilon_targets(self) -> set["State"]:
        return self.move(EPSILON)

    def __repr__(self) -> str:  # pragma: no cover - solo para debug
        marca = "*" if self.is_accept else ""
        return f"State({self.label}{marca})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, State) and self.id == other.id

    @classmethod
    def reset_counter(cls) -> None:
        """Útil en pruebas para que los ids empiecen siempre en 0."""
        cls._id_counter = itertools.count()
