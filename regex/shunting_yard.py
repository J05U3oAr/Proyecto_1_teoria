"""
ShuntingYard
============
Implementa el algoritmo de Shunting Yard de Dijkstra para convertir una
expresión regular tokenizada en notación infix a notación postfix.

Precedencia (de mayor a menor):
    1. *, +, ?      (unarios, postfijos)
    2. .            (concatenación, binario, asociativo a la izquierda)
    3. |            (alternación, binario, asociativo a la izquierda)
"""

from .tokenizer import UNARY_OPERATORS, BINARY_OPERATORS, ALL_OPERATORS


class ShuntingYard:
    """Convierte una lista de tokens infix (con concatenación explícita)
    a una lista de tokens en notación postfix."""

    _PRECEDENCE = {
        "*": 3,
        "+": 3,
        "?": 3,
        ".": 2,
        "|": 1,
    }

    def to_postfix(self, tokens: list[str]) -> list[str]:
        output: list[str] = []
        operator_stack: list[str] = []

        for tok in tokens:
            if self._is_literal(tok):
                output.append(tok)

            elif tok == "(":
                operator_stack.append(tok)

            elif tok == ")":
                while operator_stack and operator_stack[-1] != "(":
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Paréntesis desbalanceados: falta '('")
                operator_stack.pop()  # descarta el '('

            elif tok in ALL_OPERATORS:
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and self._precedence(operator_stack[-1]) >= self._precedence(tok)
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(tok)

            else:
                raise ValueError(f"Token no reconocido: '{tok}'")

        while operator_stack:
            op = operator_stack.pop()
            if op in ("(", ")"):
                raise ValueError("Paréntesis desbalanceados: falta ')'")
            output.append(op)

        return output

    def _precedence(self, op: str) -> int:
        return self._PRECEDENCE.get(op, 0)

    def _is_literal(self, tok: str) -> bool:
        return tok not in ALL_OPERATORS and tok not in ("(", ")")
