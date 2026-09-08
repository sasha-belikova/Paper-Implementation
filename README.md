# Paper Implementation — GraphAlg

This project is an independent implementation based on the paper **[Algorithm Support in a Graph Database, Done Right](https://arxiv.org/abs/2601.06705)**.

The goal of the project is to study the **GraphAlg** programming model for graph algorithms and reproduce its main ideas step by step in Python. The project implements a small DSL for graph operations on sparse matrices, backed by **NumPy/SciPy**, including a grammar, a type checker with symbolic-dimension unification, and a tree-walking interpreter.

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

* Implemented core graph operations (`reach`, `pickAny`, `WCC`, `SCC`, `eye`) in Python/SciPy, validated with property-based tests (`hypothesis`) against brute-force oracles.
* Defined a grammar for a simplified GraphAlg-like DSL (Lark, LALR), covering function declarations, arithmetic/matrix expressions, `for` loops over matrix dimensions, and built-in graph functions.
* Implemented a full **type checker** with unification over symbolic dimension variables (`Matrix<s1,s2,T>`, `Vector<s,T>`), catching dimension and semiring mismatches at "compile time".
* Implemented a tree-walking **interpreter** that evaluates DSL programs directly, reusing the `python_prototypes.py` implementations under the hood (matrices/vectors are represented as `scipy.sparse.csr_matrix`).
* Added a CLI (`main.py`) to run `.graph` program files against JSON-supplied arguments.
* Added an end-to-end test suite (`tests/test_end_to_end.py`) that parses real DSL source, type-checks it, and runs it through the interpreter, covering all five built-in functions plus assignment/`for`-loop combinations and expected type errors.

## Project Structure

The project was developed incrementally:

1. Study the GraphAlg model and its representation of graph algorithms.
2. Implement core operations in Python/NumPy/SciPy.
3. Implement and test graph algorithms (`reach`, `pickAny`, `WCC`, `SCC`).
4. Define a GraphAlg-like DSL grammar.
5. Develop a parser and AST (Lark + a desugaring transformer).
6. Build a type checker and a tree-walking interpreter for the DSL.
7. Validate the full pipeline (parser → type checker → interpreter) with an end-to-end test suite, and expose it via a CLI runner.

## Usage

```bash
python main.py examples/reach.graph --args examples/reach.json
```

## Reference

D. de Graaf et al., *Algorithm Support in a Graph Database, Done Right*, VLDB 2025 / arXiv 2601.06705.

## Status

The core pipeline (grammar → type checker → interpreter) is complete and tested for five built-in graph operations: `eye`, `pickAny`, `reach`, `WCC`, `SCC`. Further work would extend the language with more operations, loop constructs, or richer types.