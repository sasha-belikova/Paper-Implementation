## 1. Function Declaration
- `func FunctionName() -> Output { ... }`

## 2. Loop Syntax
Loops over a matrix dimension or an integer range are defined using the `for` keyword:
- `for i in G.nrows { ... }`
- `for i in int(0):iterations { ... }`

## 3. Assignment and Operations
Variables can be assigned or updated using standard operators. Matrix and vector operations (like multiplication) are built-in.
- **Standard assignment**: `variable = expression` (e.g., `v = source`)
- **Matrix addition** (addition follows the semiring's "+" operator; for bool this is logical OR): `variable + expression`
Can be used as assigning a value to a variable inside a loop (`variable += expression` equal to `v = v + E`)
- **Matrix multiplication**: `A * B`



## 4. Built-in Functions
The language provides native functions for common matrix transformations and operations:
- `eye(size)`: Takes a dimension and constructs an identity matrix.
- `pickAny(matrix)`: Retains only the first non-zero element in each row.


## 5. Advanced Transformations
- **Transpose**: `matrix.T` (Returns the transposed version of the matrix).
