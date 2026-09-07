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

**Dos archivos de texto:**

```bash
python main.py
```

Por defecto, el programa lee `examples/regexes.txt` y
`examples/cadenas.txt`. Ambos deben tener la misma cantidad de líneas: la
expresión de la línea *n* se evalúa con la cadena de la línea *n*.
El único símbolo textual para representar ε es `\~`, incluso para una
cadena vacía en `cadenas.txt`; no se permiten líneas vacías.

**Archivos con otro nombre o ubicación:**

```bash
python main.py -f ruta/expresiones_del_calificador.txt -c ruta/cadenas_del_calificador.txt
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
- `\~` representa explícitamente épsilon, es decir, la cadena vacía;
  por ejemplo, `(a|\~)b*`. La tilde con barra invertida queda reservada
  para esta finalidad.

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

