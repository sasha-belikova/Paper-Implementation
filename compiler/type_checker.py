from .data_types import MatrixType, VectorType, IntType

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def define(self, name, type_):
        self.symbols[name] = type_

    def lookup(self, name):
        return self.symbols.get(name)


class TypeChecker:
    def __init__(self):
        self.symbols = SymbolTable()


    def add_parameters(self, params):
        for param in params.children:
            name = param.children[0]
            type_ = param.children[1]
            self.symbols.define(
                str(name.children[0]),
                type_)

    def check_identifier(self, name):
        type_ = self.symbols.lookup(name)
        if type_ is None:
            raise TypeError(f"Undefined variable: {name}")
        return type_


    def check_addition(self, left_type, right_type):
        if left_type != right_type:
            raise TypeError(f"Cannot add {left_type} and {right_type}")
        return left_type


    def check_multiplication(self, left_type, right_type):
        if not isinstance(left_type, MatrixType):
            raise TypeError("Left operand must be a matrix")
        if not isinstance(right_type, MatrixType):
            raise TypeError("Right operand must be a matrix")
        if left_type.cols != right_type.rows:
            raise TypeError(
                f"Cannot multiply {left_type} and {right_type}: "
                f"{left_type.cols} != {right_type.rows}")
        if left_type.semiring != right_type.semiring:
            raise TypeError("Matrices must use the same semiring")
        return MatrixType(
            left_type.rows,
            right_type.cols,
            left_type.semiring)


    def check_transpose(self, type_):
        if not isinstance(type_, MatrixType):
            raise TypeError("Only matrices can be transposed")
        return MatrixType(
            type_.cols,
            type_.rows,
            type_.semiring)


    def check_elementwise_multiply(self, left_type, right_type):
        if left_type != right_type:
            raise TypeError(
                f"Cannot elementwise multiply {left_type} and {right_type}")
        return left_type


    def check_expression(self, node):
        if isinstance(node, str):
            return self.check_identifier(node)
        if node.data == "addition":
            left_type = self.check_expression(node.children[0])
            right_type = self.check_expression(node.children[1])
            return self.check_addition(left_type, right_type)
        if node.data == "multiplication":
            left_type = self.check_expression(node.children[0])
            right_type = self.check_expression(node.children[1])
            return self.check_multiplication(left_type, right_type)
        if node.data == "elementwise_multiply":
            left_type = self.check_expression(node.children[0])
            right_type = self.check_expression(node.children[1])
            return self.check_elementwise_multiply(
                left_type,
                right_type)
        if node.data == "transpose":
            operand_type = self.check_expression(node.children[0])
            return self.check_transpose(operand_type)
        raise TypeError(f"Unknown expression: {node.data}")