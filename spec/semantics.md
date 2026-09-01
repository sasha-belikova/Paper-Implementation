### Pre-explanation
⊕ — the T-semi-ring addition operation; for bool, this is ∨ (logical OR)



### Addition
**Syntax:** `A + B`

**Type:** 
    Input: Matrix<s1,s2,T> + Matrix<s1,s2,T>  →  Output: Matrix<s1,s2,T>
    Input: Vector<s,T> + Vector<s,T>          →  Output: Vector<s,T>

**Precondition:** A and B must have the same dimensions and the same type (semiring).

**Semantics:** 
    For A, B: Matrix<s1,s2,T>: (A + B)[i][j] = A[i][j] + B[i][j], for each i in s1, j in s2
    For A, B: Vector<s,T>:     (A + B)[i]    = A[i] + B[i],       for each i in s




### Multiplication
**Syntax:** `A * B`

**Type:** 
    Input: Matrix<s1,s2,T> * Matrix<s2,s3,T>  →  Output: Matrix<s1,s2,T>
    Input: Vector<s,T> * Matrix<s,s,T>           →  Output: Vector<s,T>

**Precondition:**
    Matrix * Matrix: number of columns of A must equal number of rows of B.
    Vector * Matrix: length of vector must equal number of rows of the matrix.
    Both operands must have the same type (semiring).

**Semantics:** 
    For A: Matrix<s1,s2,T>, B: Matrix<s2,s3,T>:
        (A * B)[i][j] = \sum_{k=1}^{s2} ( A[i][k] * B[k][j] ),  for each i in s1, j in s3
    For v: Vector<s,T>, B: Matrix<s,s,T>:
        (v * B)[j] = \sum_{k=1}^{s} ( v[k] * B[k][j] ),  for each j in s



### Loop
**Syntax:** `for i in G.nrows`


