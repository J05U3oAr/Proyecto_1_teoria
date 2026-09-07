"""
ThompsonBuilder
===============
Construye un AFN a partir de una expresión regular en notación postfix,
usando el algoritmo de Thompson. Las reglas clásicas (símbolo, ε,
concatenación, unión, cerradura de Kleene) se extienden con '+' y '?'
para no tener que reescribir la expresión antes de procesarla.
"""

from __future__ import annotations

from .state import State
from .nfa import NFA, NFAFragment
from regex.tokenizer import (
    EPSILON,
    UNARY_OPERATORS,
    BINARY_OPERATORS,
    decode_literal,
)


class ThompsonBuilder:
    def build(self, postfix: list[str]) -> NFA:
        stack: list[NFAFragment] = []
        alphabet: set[str] = set()

        for token in postfix:
            if token == "*":
                stack.append(self._star(stack.pop()))
            elif token == "+":
                stack.append(self._plus(stack.pop()))
            elif token == "?":
                stack.append(self._optional(stack.pop()))
            elif token == ".":
                frag2 = stack.pop()
                frag1 = stack.pop()
                stack.append(self._concat(frag1, frag2))
            elif token == "|":
                frag2 = stack.pop()
                frag1 = stack.pop()
                stack.append(self._union(frag1, frag2))
            else:
                # símbolo literal (o épsilon explícito en la expresión)
                symbol = decode_literal(token)
                if symbol != EPSILON:
                    alphabet.add(symbol)
                stack.append(self._literal(symbol))

        if len(stack) != 1:
            raise ValueError(
                "Expresión regular inválida: la postfix no se redujo a un "
                "único fragmento (revisa paréntesis/operadores)."
            )

        fragment = stack.pop()
        fragment.accept.is_accept = True
        return NFA(fragment.start, fragment.accept, alphabet)

    # ------------------------------------------------------------------
    # Reglas de construcción (cada una regresa un nuevo NFAFragment)
    # ------------------------------------------------------------------
    def _literal(self, symbol: str) -> NFAFragment:
        start = State()
        accept = State()
        start.add_transition(symbol, accept)
        return NFAFragment(start, accept)

    def _concat(self, frag1: NFAFragment, frag2: NFAFragment) -> NFAFragment:
        frag1.accept.add_transition(EPSILON, frag2.start)
        return NFAFragment(frag1.start, frag2.accept)

    def _union(self, frag1: NFAFragment, frag2: NFAFragment) -> NFAFragment:
        start = State()
        accept = State()
        start.add_transition(EPSILON, frag1.start)
        start.add_transition(EPSILON, frag2.start)
        frag1.accept.add_transition(EPSILON, accept)
        frag2.accept.add_transition(EPSILON, accept)
        return NFAFragment(start, accept)

    def _star(self, frag: NFAFragment) -> NFAFragment:
        start = State()
        accept = State()
        start.add_transition(EPSILON, frag.start)
        start.add_transition(EPSILON, accept)
        frag.accept.add_transition(EPSILON, frag.start)
        frag.accept.add_transition(EPSILON, accept)
        return NFAFragment(start, accept)

    def _plus(self, frag: NFAFragment) -> NFAFragment:
        start = State()
        accept = State()
        start.add_transition(EPSILON, frag.start)
        frag.accept.add_transition(EPSILON, frag.start)
        frag.accept.add_transition(EPSILON, accept)
        return NFAFragment(start, accept)

    def _optional(self, frag: NFAFragment) -> NFAFragment:
        start = State()
        accept = State()
        start.add_transition(EPSILON, frag.start)
        start.add_transition(EPSILON, accept)
        frag.accept.add_transition(EPSILON, accept)
        return NFAFragment(start, accept)
