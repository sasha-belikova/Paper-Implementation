from compiler.data_types import MatrixType, VectorType, IntType, SymbolTable


def test_matrix_type():
    matrix = MatrixType("A", "B", "bool")
    assert matrix.rows == "A"
    assert matrix.cols == "B"
    assert matrix.semiring == "bool"


def test_vector_type():
    vector = VectorType("A", "bool")
    assert vector.size == "A"
    assert vector.semiring == "bool"


def test_int_type():
    int_type = IntType()
    assert isinstance(int_type, IntType)


def test_symbol_table_define_and_lookup():
    table = SymbolTable()
    matrix = MatrixType("A", "B", "bool")
    table.define("M", matrix)
    assert table.lookup("M") == matrix


def test_symbol_table_unknown_variable():
    table = SymbolTable()
    assert table.lookup("unknown") is None


def test_symbol_table_overwrite():
    table = SymbolTable()
    first = IntType()
    second = MatrixType("A", "B", "bool")
    table.define("x", first)
    table.define("x", second)
    assert table.lookup("x") == second