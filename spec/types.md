# The DSL Type System

This document describes the specifications for the data types supported by the language, including containers, dimensions, and semirings.

## 1. Data Types
The language supports three basic scalar types for matrix and vector elements:
- **`bool`**: Boolean type (`True`/`False`), used for structural graphs and reachability operations (on a Boolean semiring with the operations $\lor$ and $\land$)[cite: 2].
- **`int`**: Integers, used primarily for working with dimensions, vertex indices, and iteration counters in loops.


## 2. Containers
Data is always represented as structured containers:
- **`Matrix <s1, s2, type>`**: A two-dimensional matrix with `s1` rows and `s2` columns, storing elements of the specified type[cite: 2].
- **`Vector <s, type>`**: A one-dimensional vector of size `s`[cite: 2].


## 3. Symbolic Dimensions
Abstract dimensions (such as `s`, `s1`, or `s2`) are used for type checking at compile time[cite: 2]. This allows for the verification of the correctness of operations (such as dimensional consistency in matrix multiplication) without having to execute the program[cite: 2].


