"""
main.py
=======
Punto de entrada del analizador léxico.

Modos de uso:
  1) Una expresión regular y una cadena:
         python main.py -r "(b|b)*abb(a|b)*" -w "babbaaaa"

  2) Un archivo con una expresión regular por línea, evaluada contra
     la misma cadena w:
         python main.py -f regexes.txt -w "babbaaaa"

  3) Dos archivos: uno con expresiones regulares y otro con cadenas.
     Cada expresión regular se evalúa contra cada cadena:
         python main.py -f regexes.txt -s cadenas.txt

  4) Modo interactivo (sin argumentos): pide regex y cadena en un
     ciclo hasta que se deje la expresión regular en blanco.
         python main.py
"""

from __future__ import annotations

import argparse
import sys

from pipeline import LexicalAnalyzerPipeline, ProcessingResult
from io_.file_reader import RegexFileReader
from automata.simulator import AutomatonSimulator


def configure_terminal_encoding() -> None:
    """Permite imprimir símbolos de teoría de lenguajes en Windows."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def print_result(result: ProcessingResult) -> None:
    si_no = lambda ok: "sí" if ok else "no"
    print(f"\nExpresión regular      : {result.regex}")
    print(f"Postfix                : {' '.join(result.postfix)}")
    print(f"Cadena w               : {result.w}")
    print(f"¿w ∈ L(r)? AFN         : {si_no(result.nfa_accepts)}")
    print(f"¿w ∈ L(r)? AFD         : {si_no(result.dfa_accepts)}")
    print(f"¿w ∈ L(r)? AFD mínimo  : {si_no(result.min_dfa_accepts)}")
    print(f"Imagen AFN             : {result.nfa_image}")
    print(f"Imagen AFD             : {result.dfa_image}")
    print(f"Imagen AFD mínimo      : {result.min_dfa_image}")


def print_string_simulation(result: ProcessingResult, w: str) -> None:
    si_no = lambda ok: "sí" if ok else "no"
    simulator = AutomatonSimulator()
    nfa_accepts = simulator.simulate_nfa(result.nfa, w)
    dfa_accepts = simulator.simulate_dfa(result.dfa, w)
    min_dfa_accepts = simulator.simulate_dfa(result.min_dfa, w)

    print(f"\nCadena w               : {w!r}")
    print(f"¿w ∈ L(r)? AFN         : {si_no(nfa_accepts)}")
    print(f"¿w ∈ L(r)? AFD         : {si_no(dfa_accepts)}")
    print(f"¿w ∈ L(r)? AFD mínimo  : {si_no(min_dfa_accepts)}")


def run_single(pipeline: LexicalAnalyzerPipeline, regex: str, w: str, index: int = 0) -> ProcessingResult:
    result = pipeline.process(regex, w, index=index)
    print_result(result)
    return result


def run_batch(pipeline: LexicalAnalyzerPipeline, path: str, w: str) -> None:
    regexes = RegexFileReader().read_regexes(path)
    for i, regex in enumerate(regexes):
        run_single(pipeline, regex, w, index=i)


def run_batch_with_strings(
    pipeline: LexicalAnalyzerPipeline, regex_path: str, strings_path: str
) -> None:
    reader = RegexFileReader()
    regexes = reader.read_regexes(regex_path)
    strings = reader.read_strings(strings_path)

    if not strings:
        raise ValueError("El archivo de cadenas está vacío.")

    for i, regex in enumerate(regexes):
        result = run_single(pipeline, regex, strings[0], index=i)
        for w in strings[1:]:
            print_string_simulation(result, w)


def run_interactive(pipeline: LexicalAnalyzerPipeline) -> None:
    print("Analizador léxico (AFN/AFD) — Enter vacío en 'r' para salir.\n")
    index = 0
    while True:
        regex = input("Expresión regular r: ").strip()
        if not regex:
            break
        w = input("Cadena w: ").strip()
        run_single(pipeline, regex, w, index=index)
        index += 1


def main() -> None:
    configure_terminal_encoding()
    parser = argparse.ArgumentParser(
        description="Analizador léxico: construye AFN/AFD desde una expresión regular y evalúa una cadena."
    )
    parser.add_argument("-r", "--regex", help="Expresión regular r")
    parser.add_argument("-w", "--string", help="Cadena w a evaluar")
    parser.add_argument(
        "-f", "--file", help="Archivo de texto con una expresión regular por línea"
    )
    parser.add_argument(
        "-s",
        "--strings-file",
        help="Archivo de texto con una cadena por línea para evaluar",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Carpeta de salida para las imágenes generadas (default: output/)",
    )
    args = parser.parse_args()

    pipeline = LexicalAnalyzerPipeline(output_dir=args.output)

    if args.file:
        if args.strings_file:
            run_batch_with_strings(pipeline, args.file, args.strings_file)
        elif args.string is not None:
            run_batch(pipeline, args.file, args.string)
        else:
            parser.error("--file requiere --string o --strings-file.")
    elif args.regex is not None:
        if args.strings_file:
            strings = RegexFileReader().read_strings(args.strings_file)
            if not strings:
                parser.error("El archivo de cadenas está vacío.")
            result = run_single(pipeline, args.regex, strings[0])
            for w in strings[1:]:
                print_string_simulation(result, w)
        elif args.string is not None:
            run_single(pipeline, args.regex, args.string)
        else:
            parser.error("--regex requiere --string o --strings-file.")
    else:
        run_interactive(pipeline)


if __name__ == "__main__":
    main()
