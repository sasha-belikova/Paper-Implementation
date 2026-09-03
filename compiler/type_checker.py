from .data_types import MatrixType, VectorType, IntType, SymbolTable


class TypeChecker:
    def __init__(self):
        self.symbols = SymbolTable()


    def check_assignment(self, node):
        var_name = str(node.children[0].children[0])
        right_type = self.check_expression(node.children[1])
        old_type = self.symbols.lookup(var_name)
        if old_type is not None and old_type != right_type:
            raise TypeError(
                f"Cannot reassign '{var_name}': "
                f"was {old_type}, now {right_type}")
        self.symbols.define(var_name, right_type)
        return right_type

    
    def add_parameters(self, params):
        for param in params.children:
            name = param.children[0]
            type_ = param.children[1]
            self.symbols.define(str(name.children[0]), type_)


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
        return MatrixType(left_type.rows, right_type.cols, left_type.semiring)


    def check_transpose(self, type_):
        if not isinstance(type_, MatrixType):
            raise TypeError("Only matrices can be transposed")
        return MatrixType(type_.cols, type_.rows, type_.semiring)


    def check_elementwise_multiply(self, left_type, right_type):
        if left_type != right_type:
            raise TypeError(
                f"Cannot elementwise multiply {left_type} and {right_type}")
        return left_type

    def check_pick_any(self, arg_type):
        if not isinstance(arg_type, MatrixType):
            raise TypeError("pickAny expects a Matrix argument")
        return arg_type


    def check_square_matrix_func(self, arg_type):
        if not isinstance(arg_type, MatrixType):
            raise TypeError("Not a matrix")
        if arg_type.rows != arg_type.cols:
            raise TypeError("Matrix is not square")
        return arg_type


    def check_expression(self, node):
        if node.data == "identifier":
                    name = node.children[0]
                    return self.check_identifier(name)
        if node.data == "number":
                    return IntType()
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
        if node.data == "func_call_1arg":
            return self.check_func_call_1arg(node)
        if node.data == "func_call_2arg":
            return self.check_func_call_2arg(node)

        raise TypeError(f"Unknown expression: {node.data}")

    def check_func_call_1arg(self, node):
        func_name = str(node.children[0])
        arg_type = self.check_expression(node.children[1])
        if func_name == "pickAny":
            return self.check_pick_any(arg_type)
        if func_name in ("WCC", "SCC"):
            return self.check_square_matrix_func(arg_type)
        if func_name == "eye":
            raise NotImplementedError()
        raise TypeError(f"Unknown function: {func_name}")

    def check_reach(self, source, matrix):
        func_name = str(source.children[0])



    def check_func_call_2arg(self, node):
        func_name = str(node.children[0])
        first_type = self.check_expression(node.children[1])
        second_type = self.check_expression(node.children[2])
        if func_name == "reach":
            raise NotImplementedError()
        raise TypeError(f"Unknown function: {func_name}")


    def check_statement(self, node):
        if node.data == "assignment":
            return self.check_assignment(node)
        if node.data == "for_stmt":
            raise NotImplementedError()
        raise TypeError(f"Unknown statement: {node.data}")
