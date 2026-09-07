# Analizador léxico — AFN/AFD desde expresiones regulares

Proyecto 1 de Teoría de la Computación. Dado una expresión regular `r`
y una cadena `w`, el programa:

1. Convierte `r` de notación infix a postfix (Shunting Yard).
2. Construye un AFN con el algoritmo de Thompson.
3. Convierte el AFN a un AFD (construcción de subconjuntos).
4. Minimiza el AFD (particionamiento por equivalencia de estados).
5. Simula `w` sobre el AFN y sobre el AFD, e indica aceptación
   ("sí"/"no").
6. Genera una imagen PNG del grafo de cada autómata (AFN, AFD, AFD
   minimizado).

## Instalación

Requiere Python 3.10+ y el binario `dot` de Graphviz instalado en el
sistema (`apt install graphviz` en Debian/Ubuntu, `brew install
graphviz` en macOS).

```bash
pip install -r requirements.txt
```

## Uso

**Una expresión regular y una cadena:**

```bash
python main.py -r "(b|b)*abb(a|b)*" -w "babbaaaa"
```

**Un archivo con una expresión regular por línea** (formato que
entrega el calificador), evaluada contra la misma cadena `w`:

```bash
python main.py -f examples/regexes.txt -w "babbaaaa"
```

**Modo interactivo** (sin argumentos, pide `r` y `w` en un ciclo):

```bash
python main.py
```

Las imágenes se guardan en `output/` (o en la carpeta que indiques
con `-o`), con el patrón `regex_<i>_afn.png`, `regex_<i>_afd.png` y
`regex_<i>_afd_min.png`.

## Sintaxis de expresiones regulares soportada

- Literales: cualquier carácter que no sea un operador.
- `|` alternación, `*` cerradura de Kleene, `+` una o más veces,
  `?` opcional, `()` agrupación.
- Concatenación implícita (no hace falta escribir un operador entre
  símbolos consecutivos).
- `\` para escapar un operador y tratarlo como símbolo literal (por
  ejemplo `\(` para el paréntesis literal).
- `~` como símbolo reservado para representar a épsilon (la cadena
  vacía) dentro de una expresión, por ejemplo `(a|~)b*`. Se eligió
  porque no es una letra, un número ni uno de los operadores soportados.

## Estructura del proyecto

```
lexical-analyzer/
├── main.py                       # CLI / punto de entrada
├── pipeline.py                   # LexicalAnalyzerPipeline (orquestador)
├── regex/
│   ├── tokenizer.py              # RegexTokenizer
│   └── shunting_yard.py          # ShuntingYard
├── automata/
│   ├── state.py                  # State
│   ├── nfa.py                    # NFA, NFAFragment
│   ├── dfa.py                    # DFA
│   ├── thompson.py               # ThompsonBuilder
│   ├── subset_construction.py    # SubsetConstructor
│   ├── minimizer.py              # DFAMinimizer
│   └── simulator.py              # AutomatonSimulator
├── visualization/
│   └── graph_renderer.py         # AutomatonRenderer (graphviz)
├── io_/
│   └── file_reader.py            # RegexFileReader
├── examples/
│   └── regexes.txt               # expresiones de ejemplo para el modo -f
└── tests/
    └── test_pipeline.py          # pruebas con pytest
```

## Pruebas

```bash
python -m pytest tests/
```

Además de las pruebas incluidas, el pipeline fue validado con más de
2000 pruebas aleatorias (fuzzing) comparando el resultado contra el
módulo `re` de Python, sin discrepancias.
