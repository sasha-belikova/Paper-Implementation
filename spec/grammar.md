## 1. Function Declaration
- `func FunctionName() -> Output { ... }`

## 2. Loop Syntax
Loops over a matrix dimension or an integer range are defined using the `for` keyword:
- `for i in G.nrows { ... }`
- `for i in int(0):iterations { ... }`

## 3. Assignment and Operations
Variables can be assigned or updated using standard operators. Matrix and vector operations (like multiplication) are built-in.

- **Standard assignment**: `variable = expression` (e.g., `v = source`)
- **In-place addition** (used for accumulating results): `variable += expression` 
- **Matrix multiplication**: `A * B`

*Example from Reachability:* `v += v * G`


## 4. Built-in Functions
The language provides native functions for common matrix transformations and operations:
- `eye(vector)`: Converts a one-dimensional vector into a diagonal matrix.
- `pickAny(matrix)`: Retains only the first non-zero element in each row.


## 5. Advanced Transformations
- **Transpose**: `matrix.T` (Returns the transposed version of the matrix).
