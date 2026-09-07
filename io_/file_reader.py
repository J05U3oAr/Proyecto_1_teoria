"""Lectura de archivos de expresiones regulares."""

from pathlib import Path


class RegexFileReader:
    def read(self, path: str | Path, keep_empty: bool = False) -> list[str]:
        source = Path(path)
        try:
            lines = source.read_text(encoding="utf-8-sig").splitlines()
        except OSError as error:
            raise ValueError(f"No se pudo leer el archivo '{source}': {error}") from error
        expressions = [line.strip() for line in lines]
        if not keep_empty:
            expressions = [line for line in expressions if line]
        if not expressions:
            raise ValueError("El archivo no contiene expresiones regulares.")
        return expressions
