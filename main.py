"""Interfaz de línea de comandos para el proyecto."""

from __future__ import annotations

import argparse
from pathlib import Path

from io_ import RegexFileReader
from pipeline import LexicalAnalyzerPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="AFN/AFD desde expresiones regulares")
    parser.add_argument(
        "-f", "--file", type=Path, default=Path("examples/regexes.txt"),
        help="Archivo de expresiones: una por línea.",
    )
    parser.add_argument(
        "-c", "--strings", type=Path, default=Path("examples/cadenas.txt"),
        help="Archivo de cadenas: una por línea, en el mismo orden que las expresiones.",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("output"))
    args = parser.parse_args()

    try:
        regexes = RegexFileReader().read(args.file, keep_empty=True)
        words = RegexFileReader().read(args.strings, keep_empty=True)
    except ValueError as error:
        print(f"Error al leer archivos: {error}")
        return 1
    if len(regexes) != len(words):
        print("Error: los archivos deben tener la misma cantidad de líneas.")
        return 1
    if any(not regex for regex in regexes) or any(not word for word in words):
        print("Error: no se permiten líneas vacías; use \\~ para representar ε.")
        return 1

    pipeline = LexicalAnalyzerPipeline()
    for index, (regex, word) in enumerate(zip(regexes, words), 1):
        # \~ es la única representación textual de ε, también cuando la
        # cadena de entrada es vacía.
        if word == r"\~":
            word = ""
        try:
            result = pipeline.analyze(regex, word, args.output, index)
        except (ValueError, OSError) as error:
            print(f"Error en {regex!r}: {error}")
            return 1
        displayed_word = r"\~" if word == "" else word
        print(f"Expresión {index}: {regex}")
        print(f"Cadena: {displayed_word}")
        print("Postfix:", " ".join(result.postfix))
        print("AFN:", "sí" if result.nfa_accepts else "no")
        print("AFD:", "sí" if result.dfa_accepts else "no")
        print("AFD minimizado:", "sí" if result.minimized_dfa_accepts else "no")
        accepted = result.nfa_accepts and result.dfa_accepts and result.minimized_dfa_accepts
        print("Cadena aceptada:", "sí" if accepted else "no")
        print("Imágenes:", ", ".join(str(image) for image in result.images))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
