"""
RegexFileReader
================
Lee un archivo de texto donde cada línea contiene una expresión
regular, tal como lo especifica el enunciado del proyecto (el
calificador entregará este archivo al momento de la presentación).
"""

from __future__ import annotations


class RegexFileReader:
    def read_regexes(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f]
        return [line for line in lines if line]

    def read_strings(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return [line.rstrip("\r\n") for line in f]
