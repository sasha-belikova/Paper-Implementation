import numpy as np
import pytest
from hypothesis import given, strategies as st
from scipy.sparse import csr_matrix, eye
from lark import Lark, Transformer, Tree, Token
from compiler.grammar import grammar
from compiler.parser import DesugarAssignment
from compiler.type_checker import TypeChecker
from compiler.interpreter import Interpreter
from tests.test_interpreter import brute_force_wcc, square_bool_csr_matrices
from compiler.runner import run_program


parser = Lark(grammar, parser="lalr")


def brute_force_scc(matrix):
    graph = matrix.toarray().astype(bool)
    n = graph.shape[0]
    reachable = np.zeros((n, n), dtype=bool)
    for i in range(n):
        reachable[i, i] = True
        stack = [i]
        visited = {i}
        while stack:
            current = stack.pop()
            for neighbour in np.flatnonzero(graph[current]):
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        for j in visited:
            reachable[i, j] = True
    return csr_matrix(reachable & reachable.T, dtype=bool)

def brute_force_pick_any(matrix):
    matrix = matrix.tocsr()
    rows = []
    cols = []

    for i in range(matrix.shape[0]):
        start = matrix.indptr[i]
        end = matrix.indptr[i + 1]
        if start < end:
            rows.append(i)
            cols.append(matrix.indices[start])

    data = np.ones(len(rows), dtype=bool)
    return csr_matrix((data, (rows, cols)), shape = matrix.shape, dtype = bool)


def brute_force_reach(source, matrix):
    graph = matrix.toarray().astype(bool)
    reached = source.toarray().astype(bool)
    n = graph.shape[0]
    for i in range(n):
        new_reached = reached | (reached @ graph)
        if np.array_equal(new_reached, reached):
            break
        reached = new_reached
    return csr_matrix(reached, dtype=bool)

@st.composite
def square_bool_csr_matrix(draw, n):
    rows = []
    for _ in range(n):
        row = draw(st.lists(st.booleans(), min_size = n, max_size = n))
        rows.append(row)
    return csr_matrix(np.array(rows, dtype=bool))

@st.composite
def same_size_matrices(draw):
    n = draw(st.integers(min_value = 1, max_value = 8))
    A = draw(square_bool_csr_matrix(n))
    B = draw(square_bool_csr_matrix(n))
    return A, B

class TestEndToEnd:
    @given(n = pytest.importorskip("hypothesis").strategies.integers(min_value =  1, max_value = 8))
    def test_eye_end_to_end(self, n):
        code = """func test(n: int) -> Matrix<A,A,bool> 
            {return eye(n);}"""

        result = run_program(code, {"n": n})
        expected = eye(n, dtype=bool, format="csr")

        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    @given(data=same_size_matrices())
    def test_matrix_multiplication_end_to_end(self, data):
        A, B = data
        code = """func test(A: Matrix<A,A,bool>, B: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {return A * B;}"""
        
        result = run_program(code, {"A": A, "B": B})
        expected = A @ B
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    @given(data=same_size_matrices())
    def test_elementwise_and_transpose_end_to_end(self, data):
        A, B = data
        code = """func test(A: Matrix<A,A,bool>, B: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {C = A.multiply(B);
            D = C.T;
            return D;}"""

        result = run_program(code, {"A": A, "B": B})
        expected = A.multiply(B).T
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    @given(matrix=square_bool_csr_matrices())
    def test_pick_any_end_to_end(self, matrix):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {return pickAny(A);}"""
        result = run_program(code, {"A": matrix})
        expected = brute_force_pick_any(matrix)
        matrix = matrix.tocsr()
        np.testing.assert_array_equal(result.toarray(), expected.toarray())



    @given(matrix=square_bool_csr_matrices())
    def test_wcc_end_to_end(self, matrix):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {return WCC(A);}"""

        result = run_program(code, {"A": matrix})
        result_array = result.toarray()
        n = matrix.shape[0]
        assert result.dtype == bool

        row_sums = result_array.sum(axis=1)
        np.testing.assert_array_equal(row_sums, np.ones(n, dtype=int))

        component = brute_force_wcc(matrix)
        leaders = np.argmax(result_array, axis=1)

        for i in range(n):
            for j in range(n):
                if component[i] == component[j]:
                    assert leaders[i] == leaders[j]


    @given(matrix=square_bool_csr_matrices())
    def test_scc_end_to_end(self, matrix):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {return SCC(A);}"""

        result = run_program(code, {"A": matrix})
        expected = brute_force_scc(matrix)
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    @given(matrix=square_bool_csr_matrices())
    def test_reach_end_to_end(self, matrix):
        code = """func test(source: Vector<A,bool>, G: Matrix<A,A,bool>) -> Vector<A,bool> 
            {return reach(source, G);}"""
        n = matrix.shape[0]
        source = csr_matrix(([True], ([0], [0])), shape=(1, n), dtype=bool)

        result = run_program(code, {"source": source, "G": matrix,})
        expected = brute_force_reach(source, matrix)
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    @given(matrix=square_bool_csr_matrices())
    def test_addition_assignment_and_for_end_to_end(self, matrix):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> 
            {V = A;
            V += A;
            for i in A.nrows 
                {V = pickAny(V);}
            return V;}"""
        
        result = run_program(code, {"A": matrix})
        expected = brute_force_pick_any(matrix)
        np.testing.assert_array_equal(result.toarray(), expected.toarray())


    def test_invalid_matrix_multiplication_end_to_end(self):
        code = """func test(A: Matrix<A,B,bool>, B: Matrix<C,D,bool>) -> Matrix<A,D,bool> 
        {return A * B;}"""
        with pytest.raises(TypeError):
            run_program(code,  
                {"A": csr_matrix((2, 3), dtype=bool),
                "B": csr_matrix((4, 5), dtype=bool),})


    def test_semiring_mismatch_end_to_end(self):
        code = """func test(A: Matrix<A,A,bool>, B: Matrix<A,A,int>) -> Matrix<A,A,bool> 
            {return A * B;}"""
        with pytest.raises(TypeError, match="same semiring"):
            run_program(code, 
                {"A": csr_matrix((2, 2), dtype=bool),
                "B": csr_matrix((2, 2), dtype=np.int64),})


    def test_undefined_variable_end_to_end(self):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            return B;}"""
        with pytest.raises(TypeError, match="Undefined variable"):
            run_program(code, {"A": csr_matrix((2, 2), dtype=bool),})    
  




