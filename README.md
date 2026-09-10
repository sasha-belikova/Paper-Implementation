# Paper Implementation — GraphAlg

This project is an independent implementation of the paper **[Algorithm Support in a Graph Database, Done Right](https://arxiv.org/abs/2601.06705)**.

The project reproduces a mini version of the GraphAlg language in Python. GraphAlg expresses graph algorithms in terms of linear algebra: graphs are represented as sparse adjacency matrices, and algorithms like reachability or connected components are computed through iterated matrix operations (multiplication, addition, element-wise ops) rather than explicit traversal with queues or stacks. This project implements a small DSL (Domain-Specific Language) built on that model — a grammar, a type checker, and a tree-walking interpreter.


```text
Paper-Implementation/
├── compiler/
│   ├── __init__.py
│   ├── data_types.py
│   ├── grammar.py
│   ├── parser.py
│   ├── type_checker.py
│   ├── interpreter.py
│   └── runner.py
│
├── spec/
│   ├── grammar.md
│   ├── semantics.md
│   └── types.md
│
├── tests/
│   ├── __init__.py
│   ├── test_data_types.py
│   ├── test_parser.py
│   ├── test_type_checker.py
│   ├── test_interpreter.py
│   └── test_end_to_end.py
│
├── examples/
│   ├── eye.graph / eye.json
│   ├── reach.graph / reach.json
│   ├── wcc.graph / wcc.json
│   └── scc.graph / scc.json
│
├── .gitignore
├── __init__.py
├── main.py
├── python_prototypes.py
├── README.md
└── requirements.txt
```

## Current Progress

* Implemented core graph operations (`reach`, `pickAny`, `WCC`, `SCC`, `eye`) in Python/SciPy, validated with property-based tests (`hypothesis` library) against brute-force.
* Defined a grammar for a simplified GraphAlg-like DSL (Lark, LALR), covering function declarations, arithmetic/matrix expressions, `for` loops over matrix dimensions, and built-in graph functions.
* Implemented a **type checker** with unification over symbolic dimension variables, catching dimension and semiring mismatches at compile time.
* Implemented a tree-walking **interpreter** that executes DSL programs by evaluating the AST (Abstract Syntax Tree) directly, dispatching each built-in graph function to its reference implementation in `python_prototypes.py`. 
* Added a CLI in `main.py` to run `.graph` program files against JSON-supplied arguments.
* Added an end-to-end test suite (`tests/test_end_to_end.py`) that parses real DSL source, type-checks it, and runs it through the interpreter, covering all built-in functions, plus-assignment (`+=`) and `for`-loop combinations and expected type errors.


## Usage

```bash
python main.py examples/reach.graph --args examples/reach.json
```

## Reference

D. de Graaf et al., *Algorithm Support in a Graph Database, Done Right*, VLDB 2025 / arXiv 2601.06705.

## Status

The core pipeline (grammar → type checker → interpreter) is complete and tested for five built-in graph operations: `eye`, `pickAny`, `reach`, `WCC`, `SCC`. Further work would extend the language with more operations, loop constructs, or richer types.