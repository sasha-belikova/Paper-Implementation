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




### Element-wise Multiplication

**Syntax:** `A.multiply(B)`

**Type:** 
    Input: Matrix<s1,s2,T> * Matrix<s1,s2,T>  →  Output: Matrix<s1,s2,T>

**Precondition:**
    Number of columns and rows of A must equal number of cloumns and rows of B.

**Semantics:** 
    (A.multiply(B))[i][j] = A[i][j] ⊗ B[i][j],  for each i in 1..s1, j in 1..s2
    



###  Multiplication

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



### For Loop (Vektors)

**Syntax:** `for i in G.nrows { ... }`

**Type:** 
    G: Matrix<s,s,T>
    Initial state: E₀: Vector<s,T>
    Body: E: Vector<s,T> → Vector<s,T>   (expression describing how to compute next state from current state)
    Count: s (= G.nrows)
    Output: Vector<s,T>

**Precondition:** 
    None beyond what is already enforced by the type.    

**Semantics:** 
    v₀ = E₀
    vₖ = E(vₖ₋₁),   for k = 1..s
    result = vₛ



### For Loop (Matrix)

**Syntax:** `for i in G.nrows { ... }`

**Type:** 
    G: Matrix<s,s,T>
    Initial state: E₀: Matrix<s,s,T>
    Body: E: Matrix<s,s,T> → Matrix<s,s,T>  
    Count: s (= G.nrows)
    Output: Matrix<s,s,T>

**Precondition:** 
     None beyond what is already enforced by the type (G and the initial state must share the same dimension s; the loop body must preserve the type Matrix<s,s,T> → Matrix<s,s,T>).    

**Semantics:** 
    m₀ = E₀
    mₖ = E(mₖ₋₁),   for k = 1..s
    result = mₛ



### Pick Any

**Syntax:** `pickAny(matrix)`

**Type:** 
    Input: Matrix <s1,s2,T> 
    Output: Matrix <s1,s2,T> 
    
**Precondition:** 
    None
        
**Semantics:** 
    result[i][j] = matrix[i][j], for exactly one arbitrarily chosen j where matrix[i][j] ≠ 0 (if such j exists)
    result[i][j] = 0, otherwise



### Transposition

**Syntax:** `A.T`

**Type:** 
    Input: Matrix <s1,s2,T> 
    Output: Matrix <s2,s1,T>
    
    
**Precondition:** 
    None
        
**Semantics:** 
    (A.T)[i][j] = A[j][i],  for each i in 1..s2, j in 1..s1



### Eye

**Syntax:** 
    eye(size)

**Type:** 
    Input: int
    Output: Matrix<s,s,T>   (where s = size)

**Precondition:** 
    None

**Semantics:** 
    eye(size)[i][j] = 1,  if i = j
    eye(size)[i][j] = 0,  if i ≠ j
    for each i, j in 1..size



### Reach

**Syntax:** 
    reach(source, G)

**Type:** 
    Input: source: Vector<s,T>, G: Matrix<s,s,T>
    Output: Vector<s,T>

**Precondition:** 
    Source and G must share the same dimension s.

**Semantics:** 
    reach(source, G) = for-loop (Vector version) with:
        E₀ = source
        E(v) = v + (v * G)



### WCC

**Syntax:** 
    WCC(matrix)

**Type:** 
    Input: matrix: Matrix<s,s,T>
    Output: Matrix<s,s,T>

**Precondition:** 
    Matrix must be square.

**Semantics:** 
    WCC(matrix) = pickAny(R)
    where R = for-loop (Matrix version) with:
        E₀ = eye(s)
        E(M) = pickAny(M + (matrix * M))
    (i.e. M₀ = eye(s); Mₖ = pickAny(Mₖ₋₁ + (matrix * Mₖ₋₁)) for k = 1..s; R = Mₛ)
    Each row i of the result contains exactly one nonzero entry j,
    identifying j as the representative (leader) of the connected component containing vertex i



### SCC

**Syntax:** 
    SCC(matrix)

**Type:** 
    Input: matrix: Matrix<s,s,T>
    Output: Matrix<s,s,T>

**Precondition:** 
    Matrix must be square, s×s.

**Semantics:** 
    SCC(matrix) = R.multiply(R.T)
    where R = for-loop (Matrix version) with:
        E₀ = eye(s)
        E(M) = M + (M * matrix)
    (i.e. M₀ = eye(s); Mₖ = Mₖ₋₁ + (Mₖ₋₁ * matrix) for k = 1..s; R = Mₛ)

    R[i][j] = true iff vertex j is reachable from vertex i.
    (R.multiply(R.T))[i][j] = true iff i and j are mutually reachable,
    i.e. i and j belong to the same strongly connected component.
     

