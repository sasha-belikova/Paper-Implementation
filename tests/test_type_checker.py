import pytest
from lark import Tree, Lark

from compiler.grammar import grammar
from compiler.parser import DesugarAssignment
from compiler.type_checker import TypeChecker
from compiler.data_types import MatrixType, IntType, VectorType





@pytest.fixture
def parser():
    return Lark(
        grammar,
        parser="lalr",
        start=["start", "expression", "type", "statement"],)


@pytest.fixture
def transformer():
    return DesugarAssignment()


def find_first(tree, name):
    if isinstance(tree, Tree):
        if tree.data == name:
            return tree
        for child in tree.children:
            found = find_first(child, name)
            if found is not None:
                return found
    return None


def parse_function(code, parser, transformer):
    tree = parser.parse(code, start="start")
    tree = transformer.transform(tree)
    return tree.children[0]


def run_expression_case(code, expected, parser, transformer):
    func = parse_function(code, parser, transformer)
    params = func.children[1]
    return_stmt = find_first(func, "return_stmt")
    return_expr = return_stmt.children[0]
    checker = TypeChecker()
    checker.add_parameters(params)
    result_type = checker.check_expression(return_expr)
    assert result_type == expected


class TestGraphOperations:

    def test_pick_any(self, parser, transformer):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            return pickAny(A);}"""
        run_expression_case(
            code,
            MatrixType("A", "A", "bool"),
            parser,
            transformer,)


    def test_pick_any_nn_matrix(self):
        checker = TypeChecker()
        with pytest.raises(TypeError, match="pickAny expects a Matrix"):
            checker.check_pick_any(VectorType("A", "bool"))    

    def test_wcc(self, parser, transformer):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            return WCC(A);}"""
        run_expression_case(
            code,
            MatrixType("A", "A", "bool"),
            parser,
            transformer,)

    def test_wcc_nn_matrix(self):
        checker = TypeChecker()
        with pytest.raises(TypeError, match="Not a matrix"):
            checker.check_square_matrix_func(VectorType("A", "bool"))

    def test_scc(self, parser, transformer):
        code = """func test(A: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            return SCC(A);}"""
        run_expression_case(
            code,
            MatrixType("A", "A", "bool"),
            parser,
            transformer,)

    def test_wcc_nnsquare(self, parser, transformer):
        code = """func test(A: Matrix<A,B,bool>) -> Matrix<A,B,bool> {
            return WCC(A);}"""
        with pytest.raises(TypeError):
            run_expression_case(
                code,
                None,
                parser,
                transformer,)

    def test_reach(self, parser, transformer):
        code = """func test(v: Vector<A,bool>, G: Matrix<A,A,bool>) -> Vector<A,bool> {
            return reach(v, G);}"""
        run_expression_case(
            code,
            VectorType("A", "bool"),
            parser,
            transformer,)

    def test_reach__mismatched_dim(self, parser, transformer):
        code = """func test(v: Vector<A,bool>, G: Matrix<B,B,bool>) -> Vector<A,bool> {
            return reach(v, G);}"""
        with pytest.raises(TypeError):
            run_expression_case(
                code,
                None,
                parser,
                transformer,)

    def test_reach_nn_square(self, parser, transformer):
        code = """func test(v: Vector<A,bool>, G: Matrix<A,B,bool>) -> Vector<A,bool> {
            return reach(v, G);}"""
        with pytest.raises(TypeError):
            run_expression_case(
                code,
                None,
                parser,
                transformer,)

    def test_reach_nvector(self):
        checker = TypeChecker()
        source = MatrixType("A", "A", "bool")
        graph = MatrixType("A", "A", "bool")
        with pytest.raises(TypeError, match="first argument must be a Vector"):
            checker.check_reach(source, graph)

    def test_reach_semiring_mismatch(self):
        checker = TypeChecker()
        source = VectorType("A", "bool")
        graph = MatrixType("A", "A", "real")
        with pytest.raises(TypeError, match="semiring mismatch"):
            checker.check_reach(source, graph)                


    def test_eye(self, parser, transformer):
            code = """func test(n: int) -> Matrix<A,A,bool> {
                return eye(n);}"""
            func = parse_function(code, parser, transformer)
            params = func.children[1]
            return_stmt = find_first(func, "return_stmt")
            return_expr = return_stmt.children[0]
            checker = TypeChecker()
            checker.add_parameters(params)
            result_type = checker.check_expression(return_expr)
            assert isinstance(result_type, MatrixType)
            assert result_type.rows == result_type.cols
            assert result_type.semiring == "bool"

    def test_eye_dimension(self, parser, transformer):
            code = """func test(n: int) -> Matrix<A,A,bool> {
                v = eye(n);
                return v;}"""
            func = parse_function(code, parser, transformer)
            params = func.children[1]
            checker = TypeChecker()
            checker.add_parameters(params)
            assignment_node = find_first(func, "assignment")
            checker.check_assignment(assignment_node)
            return_stmt = find_first(func, "return_stmt")
            return_expr = return_stmt.children[0]
            result_type = checker.check_expression(return_expr)
            assert isinstance(result_type, MatrixType)
            assert result_type.rows.startswith("$")

    def test_eye_assignment(self, parser, transformer):
            code = """func test(n: int) 
            -> Matrix<A,A,bool> {
                v = eye(n);
                return v;}"""
            func = parse_function(code, parser, transformer)
            checker = TypeChecker()
            result_type = checker.check_func_decl(func)
            assert result_type == MatrixType("A", "A", "bool")


    def test_mismatched_type(self, parser, transformer):
            code = """func test(n: int) -> Vector<A,bool> {
                return eye(n);}"""
            func = parse_function(code, parser, transformer)
            checker = TypeChecker()
            with pytest.raises(TypeError):
                checker.check_func_decl(func)
    
    def test_function_loop(self, parser, transformer):
        code = """func test(G: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            v = pickAny(G);
            for i in G.nrows {v = pickAny(v);}
            return v;}"""
        func = parse_function(code, parser, transformer)
        checker = TypeChecker()
        result_type = checker.check_func_decl(func)
        assert result_type == MatrixType("A", "A", "bool")


    def test_eye_multi(self, parser, transformer):
        code = """func test(n: int, G: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            return eye(n) * G;}"""
        func = parse_function(code, parser, transformer)
        checker = TypeChecker()
        result_type = checker.check_func_decl(func)
        assert result_type == MatrixType("A", "A", "bool")

    def test_square_matrix_function(self):
        checker = TypeChecker()
        matrix = MatrixType("A", "A", "bool")
        result = checker.check_square_matrix_func(matrix)
        assert result == MatrixType("A", "A", "bool")




class TestUnification:

    def test_unifies_dimension(self):
        checker = TypeChecker()
        fresh = checker.fresh_var()
        result = checker.unify_dim(fresh, "A")
        assert result == "A"
        assert checker.resolve(fresh) == "A"

    def test_different_dim(self):
        checker = TypeChecker()
        with pytest.raises(TypeError):
            checker.unify_dim("A", "B")

    def test_unify_mtypes(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("A", "B", "bool")
        result = checker.unify_type(a, b)
        assert result == MatrixType("A", "B", "bool")

    def test_unify_vtypes(self):
        checker = TypeChecker()
        a = VectorType("A", "bool")
        b = VectorType("A", "bool")
        result = checker.unify_type(a, b)
        assert result == VectorType("A", "bool")

    def test_unify_itypes(self):
        checker = TypeChecker()
        result = checker.unify_type(IntType(), IntType())
        assert isinstance(result, IntType)

    def test_unify_semiring(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("A", "B", "real")
        with pytest.raises(TypeError, match="Semiring mismatch"):
            checker.unify_type(a, b)

    def test_unify_diff_types(self):
        checker = TypeChecker()
        matrix = MatrixType("A", "B", "bool")
        vector = VectorType("A", "bool")
        with pytest.raises(TypeError):
            checker.unify_type(matrix, vector)        


class TestForStatement:

    def test_for_stmt(self, parser, transformer):
        code = """func test(G: Matrix<A,A,bool>, v: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            for i in G.nrows {
                v = pickAny(v);}
            return v;}"""
        func = parse_function(code, parser, transformer)
        params = func.children[1]
        checker = TypeChecker()
        checker.add_parameters(params)
        for_node = find_first(func, "for_stmt")
        checker.check_for_stmt(for_node)
        i_type = checker.symbols.lookup("i")
        assert isinstance(i_type, IntType)
        v_type = checker.symbols.lookup("v")
        assert v_type == MatrixType("A", "A", "bool")

    def test_for_stmt_nn_matrix(self, parser, transformer):
        code = """func test(G: int, v: Matrix<A,A,bool>) -> Matrix<A,A,bool> {
            for i in G.nrows {
                v = pickAny(v);}
            return v;}"""
        func = parse_function(code, parser, transformer)
        params = func.children[1]
        checker = TypeChecker()
        checker.add_parameters(params)
        for_node = find_first(func, "for_stmt")
        with pytest.raises(TypeError):
            checker.check_for_stmt(for_node)

    def test_for_stmt_type_change(self, parser, transformer):
        code = """func test(G: Matrix<A,A,bool>, v: Matrix<A,A,bool>, n: int) 
        -> Matrix<A,A,bool> {
            for i in G.nrows {v = n;}
            return v;}"""
        func = parse_function(code, parser, transformer)
        params = func.children[1]
        checker = TypeChecker()
        checker.add_parameters(params)
        for_node = find_first(func, "for_stmt")
        with pytest.raises(TypeError):
            checker.check_for_stmt(for_node)


    def test_for_requires_matrix(self):
        checker = TypeChecker()
        checker.symbols.define("v", VectorType("A", "bool"))
        node = Tree("for_stmt", [Tree("identifier", ["i"]), Tree("identifier", ["v"]),])
        with pytest.raises(TypeError, match="Not a Matrix"):
            checker.check_for_stmt(node)        


class TestMatrixOperations:

    def test_matrix_add(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("A", "B", "bool")
        result = checker.check_addition(a, b)
        assert result == MatrixType("A", "B", "bool")

    def test_matrix_add_dim_mismatch(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("C", "D", "bool")
        with pytest.raises(TypeError):
            checker.check_addition(a, b)

    def test_add_semiring_mismatch(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b= MatrixType("A", "B", "real")
        with pytest.raises(TypeError, match="Semiring mismatch"):
            checker.check_addition(a, b)

    def test_matrix_multi(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("B", "C", "bool")
        result = checker.check_multiplication(a, b)
        assert result == MatrixType("A", "C", "bool")

    def test_matrix_multi_dim_mismatch(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("C", "D", "bool")
        with pytest.raises(TypeError, match="Cannot unify dimension"):
            checker.check_multiplication(a, b)

    def test_matrix_multi_semiring(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("B", "C", "real")
        with pytest.raises(TypeError, match="semiring"):
            checker.check_multiplication(a, b)

    def not_not_matrix(self):
        checker = TypeChecker()
        with pytest.raises(TypeError, match="Left operand must be a matrix"):
            checker.check_multiplication(
                VectorType("A", "bool"),
                MatrixType("A", "B", "bool"))

    def not_matrix(self):
        checker = TypeChecker()
        with pytest.raises(TypeError, match="Right operand must be a matrix"):
            checker.check_multiplication(
                MatrixType("A", "B", "bool"),
                VectorType("B", "bool"))


    def test_transpose(self):
        checker = TypeChecker()
        matrix = MatrixType("A", "B", "bool")
        result = checker.check_transpose(matrix)
        assert result == MatrixType("B", "A", "bool")

    def test_transpose_nn_matrix(self):
        checker = TypeChecker()
        with pytest.raises(TypeError, match="Only matrices"):
            checker.check_transpose(VectorType("A", "bool"))

    def test_elem_multi(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("A", "B", "bool")
        result = checker.check_elementwise_multiply(a, b)
        assert result == MatrixType("A", "B", "bool")

    def test_elem_multi_dim_mismatch(self):
        checker = TypeChecker()
        a = MatrixType("A", "B", "bool")
        b = MatrixType("C", "D", "bool")
        with pytest.raises(TypeError):
            checker.check_elementwise_multiply(a, b)


class TestExpressionErrors:
    def test_unknown_exp(self):
        checker = TypeChecker()
        node = Tree("unknown_expression", [])
        with pytest.raises(TypeError, match="Unknown expression"):
            checker.check_expression(node)

    def test_unknown_1arg_func(self):
        checker = TypeChecker()
        node = Tree("func_call_1arg",
            ["unknown", Tree("number", ["1"])])
        with pytest.raises(TypeError, match="Unknown function"):
            checker.check_func_call_1arg(node)

    def test_unknown_2arg_func(self):
        checker = TypeChecker()
        node = Tree(
            "func_call_2arg",
            ["unknown",
            Tree("number", ["1"]),
            Tree("number", ["2"])])
        with pytest.raises(TypeError, match="Unknown function"):
            checker.check_func_call_2arg(node)

    def test_unknown_stmt(self):
        checker = TypeChecker()
        node = Tree("unknown_statement", [])
        with pytest.raises(TypeError, match="Unknown statement"):
            checker.check_statement(node)            