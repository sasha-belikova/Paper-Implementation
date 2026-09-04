# Paper Implementation — GraphAlg

This project is an independent implementation based on the paper **[Algorithm Support in a Graph Database, Done Right](https://arxiv.org/abs/2601.06705)**.

The goal of the project is to study the **GraphAlg** programming model for graph algorithms and reproduce its main ideas step by step in Python. The project currently focuses on implementing graph operations using **NumPy/SciPy** and on building the foundation for a simplified GraphAlg-like language.


```text
Paper-Implementation/
├── compiler/
│   ├── __init__.py
│   ├── data_types.py
│   ├── grammar.py
│   ├── parser.py
│   └── type_checker.py
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
│   └── test_type_checker.py
│
├── .gitignore
├── __init__.py
├── python_prototypes.py
├── README.md
└── requirements.txt 
```

## Current Progress

* Implemented basic graph operations and representations using **NumPy** and **SciPy sparse matrices**.
* Implemented the first graph algorithm, **Reach**, based on the matrix-based approach described in the paper.
* Started developing a **grammar and parser** for a simplified GraphAlg-like syntax, beginning with the `Reach` algorithm.

## Project Structure

The project is being developed incrementally:

1. Study the GraphAlg model and its representation of graph algorithms.
2. Implement core operations in Python/NumPy.
3. Implement and test graph algorithms.
4. Define a simplified GraphAlg-like syntax.
5. Develop a parser and AST.
6. Build an interpreter for the language.
7. Implement and test several algorithms using the new language.

## Reference

D. de Graaf et al., *Algorithm Support in a Graph Database, Done Right*, VLDB 2025 / arXiv 2601.06705.

## Status

**Work in progress.**

The implementation is intentionally developed step by step to understand the GraphAlg model before building the complete language and execution pipeline.
