import pytest
import numpy as np
from scipy.sparse import csr_matrix
from lark import Tree, Token
from compiler.interpreter import Interpreter
from hypothesis import given, strategies as st

@st.composite
def bool_arrays(draw, min_rows=1, max_rows=5,
                min_cols=1, max_cols=5):
    rows = draw(st.integers(min_rows, max_rows))
    cols = draw(st.integers(min_cols, max_cols))
    values = draw(
        st.lists(
            st.booleans(),
            min_size = rows * cols,
            max_size = rows * cols))
    return np.array(values, dtype=bool).reshape(rows, cols)


@st.composite
def bool_csr_matrices(draw, min_size=1, max_size=5):
    array = draw(
        bool_arrays(
            min_rows=min_size,
            max_rows=max_size,
            min_cols=min_size,
            max_cols=max_size))
    return csr_matrix(array, dtype=bool)


@st.composite
def square_bool_csr_matrices(draw, min_size=1, max_size=5):
    size = draw(st.integers(min_size, max_size))
    values = draw(st.lists(
            st.booleans(),
            min_size=size * size,
            max_size=size * size))
    array = np.array(values, dtype=bool).reshape(size, size)
    return csr_matrix(array, dtype=bool)


@st.composite
def compatible_matrices(draw):
    rows = draw(st.integers(1, 5))
    inner = draw(st.integers(1, 5))
    cols = draw(st.integers(1, 5))
    left_values = draw(
        st.lists(
            st.booleans(),
            min_size=rows * inner,
            max_size=rows * inner))
    right_values = draw(
        st.lists(
            st.booleans(),
            min_size = inner * cols,
            max_size = inner * cols))
    left = csr_matrix(np.array(left_values, dtype=bool).reshape(rows, inner))
    right = csr_matrix(np.array(right_values, dtype=bool).reshape(inner, cols))
    return left, right


def oracle_pick_any(matrix):
    array = matrix.toarray()
    result = np.zeros_like(array, dtype=bool)
    for i in range(array.shape[0]):
        true_positions = np.flatnonzero(array[i])
        if len(true_positions) > 0:
            result[i, true_positions[0]] = True
    return result


def oracle_reach(source, matrix):
    source = np.asarray(source, dtype=bool)
    matrix = matrix.toarray().astype(bool)
    reached = source.copy()
    for i in range(matrix.shape[0]):
        new_reached = (reached.astype(int) @ matrix.astype(int)) > 0
        new_reached = new_reached | reached
        if np.array_equal(new_reached, reached):
            break
        reached = new_reached
    return reached

def oracle_wcc(matrix):
    graph = matrix.toarray().astype(bool)
    undirected = graph | graph.T
    n = undirected.shape[0]
    component = [-1] * n
    current_id = 0
    for start in range(n):
        if component[start] != -1:
            continue
        stack = [start]
        component[start] = current_id
        while stack:
            current = stack.pop()
            neighbours = np.flatnonzero(undirected[current])
            for neighbour in neighbours:
                if component[neighbour] == -1:
                    component[neighbour] = current_id
                    stack.append(neighbour)
        current_id += 1
    return component


def oracle_scc(matrix):
    graph = matrix.toarray().astype(bool)
    n = graph.shape[0]
    reachability = np.zeros((n, n), dtype=bool)
    for start in range(n):
        reached = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            neighbours = np.flatnonzero(graph[current])
            for neighbour in neighbours:
                if neighbour not in reached:
                    reached.add(neighbour)
                    stack.append(neighbour)
        for vertex in reached:
            reachability[start, vertex] = True
    return reachability & reachability.T


class TestInterpreter:

    def setup_method(self):
        self.interpreter = Interpreter()

    @given(bool_csr_matrices())
    def test_eval_identifier(self, matrix):
        self.interpreter.symbols.define("A", matrix)
        result = self.interpreter.eval_identifier("A")
        assert result is matrix

    def test_eval_identifier_undefined(self):
        with pytest.raises(NameError):
            self.interpreter.eval_identifier("A")

    @given(bool_csr_matrices())
    def test_eval_addition(self, matrix):
        result = self.interpreter.eval_addition(matrix, matrix)
        expected = (matrix.toarray() | matrix.toarray())
        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected)


    @given(bool_csr_matrices(), bool_csr_matrices())
    def test_eval_addition_different_values(self, A, B):
        if A.shape != B.shape:
            return
        result = self.interpreter.eval_addition(A, B)
        expected = (A.toarray() | B.toarray())
        np.testing.assert_array_equal(result.toarray(), expected)


    @given(compatible_matrices())
    def test_eval_multiplication(self, matrices):
        A, B = matrices
        result = self.interpreter.eval_multiplication(A, B)
        expected = (A.toarray().astype(int) @ B.toarray().astype(int)) > 0
        assert isinstance(result, csr_matrix)
        np.testing.assert_array_equal(result.toarray(), expected)


    @given(bool_csr_matrices(), bool_csr_matrices())
    def test_eval_elementwise_multiply(self, A, B):
        if A.shape != B.shape:
            return
        result = self.interpreter.eval_elementwise_multiply(A, B)
        expected = (A.toarray() & B.toarray())
        assert isinstance(result, csr_matrix)
        np.testing.assert_array_equal(result.toarray(), expected)


    @given(bool_csr_matrices())
    def test_eval_transpose(self, matrix):
        result = self.interpreter.eval_transpose(matrix)
        expected = matrix.toarray().T
        np.testing.assert_array_equal(result.toarray(), expected)


    def test_eval_expression_identifier(self):
        matrix = csr_matrix([[True, False], [False, True]], dtype=bool)
        self.interpreter.symbols.define("A", matrix)
        node = Tree("identifier", [Token("IDENTIFIER", "A")])
        result = self.interpreter.eval_expression(node)
        assert result is matrix

    def test_eval_expression_number(self):
        node = Tree("number", [42])
        result = self.interpreter.eval_expression(node)
        assert result == 42


    @given(bool_csr_matrices())
    def test_eval_assignment(self, matrix):
        node = Tree("assignment",
                [Tree ("identifier", [Token("IDENTIFIER", "A")]),
                Tree("identifier", [Token("IDENTIFIER", "B")])
                ])
        self.interpreter.symbols.define("B", matrix)
        result = self.interpreter.eval_assignment(node )
        assert result is matrix
        assert (self.interpreter.symbols.lookup("A") is matrix)

    

    @given(st.integers(min_value=1, max_value=10))
    def test_eye(self, n):
        node = Tree("func_call_1arg",
            [Token("FUNC_NAME_1ARG", "eye"), Tree("number", [n])])
        result = self.interpreter.eval_func_call_1arg(node)
        expected = np.eye(n, dtype=bool)
        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected)



    @given(bool_csr_matrices())
    def test_pick_any(self, matrix):
        self.interpreter.symbols.define("A", matrix)
        node = Tree("func_call_1arg",
            [Token("FUNC_NAME_1ARG", "pickAny"),
            Tree("identifier", [Token("IDENTIFIER", "A")])
            ])
        result = self.interpreter.eval_func_call_1arg(node)
        expected = oracle_pick_any(matrix)
        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected)



    @given(square_bool_csr_matrices(), st.integers(min_value=0, max_value=4))
    def test_reach(self, matrix, source_index):
        source_index %= matrix.shape[0]
        source = np.zeros((1, matrix.shape[0]), dtype=bool)
        source[0, source_index] = True
        source_matrix = csr_matrix(source, dtype=bool)

        self.interpreter.symbols.define("source", source_matrix)
        self.interpreter.symbols.define("G", matrix)

        node = Tree("func_call_2arg",[Token("FUNC_NAME_2ARG", "reach"),
                Tree("identifier", [Token("IDENTIFIER", "source")]),
                Tree("identifier", [Token("IDENTIFIER", "G")])
                ])
        result = self.interpreter.eval_func_call_2arg(node)
        expected = oracle_reach(source, matrix)

        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected)


    @given(square_bool_csr_matrices())
    def test_wcc(self, matrix):
        self.interpreter.symbols.define("G", matrix)
        node = Tree("func_call_1arg", [Token("FUNC_NAME_1ARG", "WCC"),
                Tree("identifier", [Token("IDENTIFIER", "G")])
                ])
        result = self.interpreter.eval_func_call_1arg(node)
        assert isinstance(result, csr_matrix)
        assert result.dtype == bool

        result_array = result.toarray()
        n = matrix.shape[0]

        row_sums = result_array.sum(axis=1)
        np.testing.assert_array_equal(row_sums, np.ones(n, dtype=int))
        leaders = np.argmax(result_array, axis=1)
        component = oracle_wcc(matrix)
        for i in range(n):
            for j in range(n):
                if component[i] == component[j]:
                    assert leaders[i] == leaders[j]   


    @given(square_bool_csr_matrices())
    def test_scc(self, matrix):
        self.interpreter.symbols.define("G", matrix)
        node = Tree("func_call_1arg", [Token("FUNC_NAME_1ARG", "SCC"),
                Tree("identifier", [Token("IDENTIFIER", "G")])
                ])
        result = self.interpreter.eval_func_call_1arg(node)
        expected = oracle_scc(matrix)

        assert isinstance(result, csr_matrix)
        assert result.dtype == bool
        np.testing.assert_array_equal(result.toarray(), expected)


    def test_unknown_function_1arg(self):
        matrix = csr_matrix([[True]], dtype=bool)
        self.interpreter.symbols.define("A", matrix)
        node = Tree("func_call_1arg", [Token("FUNC_NAME_1ARG", "unknown"),
                Tree("identifier", [Token("IDENTIFIER", "A")])
                ])
        with pytest.raises(NotImplementedError):
            self.interpreter.eval_func_call_1arg(node)

    def test_unknown_function_2arg(self):
        matrix = csr_matrix([[True]], dtype=bool)
        self.interpreter.symbols.define("A", matrix)
        node = Tree("func_call_2arg", [Token("FUNC_NAME_2ARG", "unknown"),
                Tree("identifier", [Token("IDENTIFIER", "A")]),
                Tree("identifier", [Token("IDENTIFIER", "A")])
                ])
        with pytest.raises(NotImplementedError):
            self.interpreter.eval_func_call_2arg(node)