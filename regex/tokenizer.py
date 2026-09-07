r"""
RegexTokenizer
==============
Convierte una expresión regular infix (como texto) en una lista de tokens,
insertando el operador de concatenación implícito ('.') donde corresponde.

Símbolo de épsilon: se usa la secuencia ``\~``. No es una letra ni un
número, por lo que no se confunde con los símbolos ordinarios del alfabeto.
"""

# La notación elegida para ε en la entrada es ``\~``.  Se conserva como
# token interno para que nunca pueda confundirse con el carácter ``~``.
EPSILON = r"\~"

# Operadores soportados por el lenguaje de expresiones regulares
UNARY_OPERATORS = {"*", "+", "?"}
BINARY_OPERATORS = {"|", "."}  # '.' es la concatenación explícita interna
ALL_OPERATORS = UNARY_OPERATORS | BINARY_OPERATORS
CONCAT_OP = "."


def decode_literal(token: str) -> str:
    r"""Convierte un literal escapado a su símbolo real.

    ``\~`` queda reservado para epsilon; los demás escapes permiten usar
    operadores como caracteres ordinarios (por ejemplo, ``\*`` representa
    el símbolo ``*`` y no la cerradura de Kleene).
    """
    if token == EPSILON:
        return EPSILON
    return token[1:] if token.startswith("\\") else token


class RegexTokenizer:
    """Tokeniza una expresión regular infix y agrega la concatenación
    implícita para que ShuntingYard pueda procesarla sin ambigüedad.
    """

    def tokenize(self, regex: str) -> list[str]:
        raw_tokens = self._split_raw(regex)
        return self._insert_concat_operator(raw_tokens)

    # ------------------------------------------------------------------
    def _split_raw(self, regex: str) -> list[str]:
        """Separa el string en tokens individuales, respetando el
        escape con backslash (por ejemplo, \\* representa el símbolo
        literal '*', no el operador de Kleene)."""
        tokens: list[str] = []
        i = 0
        while i < len(regex):
            char = regex[i]

            if char.isspace():
                i += 1
                continue

            if char == "\\":
                if i + 1 >= len(regex):
                    raise ValueError(
                        f"Escape incompleto al final de la expresión: '{regex}'"
                    )
                escaped = regex[i : i + 2]
                # ``\~`` es la representación acordada de epsilon.  Los
                # demás escapes se conservan para que, por ejemplo, ``\*``
                # siga siendo un literal y no el operador de Kleene.
                tokens.append(EPSILON if escaped == EPSILON else escaped)
                i += 2
                continue

            tokens.append(char)
            i += 1

        return tokens

    def _insert_concat_operator(self, tokens: list[str]) -> list[str]:
        """Inserta '.' entre dos tokens t1 t2 cuando t1 puede terminar una
        sub-expresión (literal, ')', o un operador unario) y t2 puede
        iniciar una nueva (literal o '(')."""
        result: list[str] = []

        def ends_expression(tok: str) -> bool:
            return tok not in ("(",) and tok not in ("|",) and (
                tok == ")" or tok in UNARY_OPERATORS or self._is_literal(tok)
            )

        def starts_expression(tok: str) -> bool:
            return tok == "(" or self._is_literal(tok)

        for idx, tok in enumerate(tokens):
            if idx > 0:
                prev = tokens[idx - 1]
                if ends_expression(prev) and starts_expression(tok):
                    result.append(CONCAT_OP)
            result.append(tok)

        return result

    def _is_literal(self, tok: str) -> bool:
        return tok.startswith("\\") or (
            tok not in ALL_OPERATORS and tok not in ("(", ")")
        )
