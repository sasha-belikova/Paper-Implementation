## 1. Function Declaration
- `func FunctionName() -> Output { ... }`

## 2. Loop Syntax
Loops over a matrix dimension are defined using the `for` keyword:
- `for i in G.nrows { ... }`
- `for i in G.ncols { ... }`

## 3. Assignment and Operations
Variables can be assigned or updated using standard operators. Matrix and vector operations (like multiplication) are built-in.
- **Standard assignment**: `variable = expression` (e.g., `v = source`)
- **Matrix addition** (addition follows the semiring's "+" operator; for bool this is logical OR): `variable + expression`
Can be used as assigning a value to a variable inside a loop (`variable += expression` equal to `v = v + E`)
- **Matrix multiplication**: `A * B`
- **Transpose**: `matrix.T` (Returns the transposed version of the matrix).



## 4. Built-in Functions
The language provides native functions for common matrix transformations and operations:
- `eye(size)`: Takes a dimension and constructs an identity matrix.
- `pickAny(matrix)`: Retains only non-zero element in each row.
- `reach(source, G)`: Computes the set of vertices reachable from the source vertices by traversing the graph G.
- `WCC(matrix)`: Computes the weakly connected components of the graph, returning a matrix where each row identifies the representative (leader) vertex of its component.
- `SCC(matrix)`: Computes the strongly connected components of the graph, returning a matrix indicating which pairs of vertices are mutually reachable.


