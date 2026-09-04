from lark import Lark
from compiler.grammar import grammar
from compiler.parser import DesugarAssignment



parser = Lark(grammar, parser="lalr")


def transform(code):
    tree = parser.parse(code)
    return DesugarAssignment().transform(tree)

def test_add():
    tree = transform("""
        func foo(A: Matrix<n,m,bool>) -> Matrix<n,m,bool> {
            B = A + A;
            return B;}
            """)
    assert tree is not None


def test_multi():
    tree = transform("""
        func foo(A: Matrix<n,m,bool>, B: Matrix<m,k,bool>) -> Matrix<n,k,bool> {
            C = A * B;
            return C;}
    """)
    assert tree is not None


def test_add_and():
    tree = transform("""
        func foo(A: Matrix<n,m,bool>) -> Matrix<n,m,bool> {
            A += A;
            return A;}
    """)
    assert tree is not None


def test_transpose():
    tree = transform("""
        func foo(A: Matrix<n,m,bool>) -> Matrix<m,n,bool> {
            B = A.T;
            return B;}
    """)
    assert tree is not None


def test_method_call():
    tree = transform("""
        func foo(A: Matrix<n,m,bool>, B: Matrix<n,m,bool>) -> Matrix<n,m,bool> {
            C = A.multiply(B);
            return C;}
    """)
    assert tree is not None


def test_matrix_type():
    transformer = DesugarAssignment()
    result = transformer.transform(
        parser.parse("""
        func foo(A: Matrix<n,m,bool>) -> Matrix<n,m,bool> {
            return A;}
        """))
    assert result is not None