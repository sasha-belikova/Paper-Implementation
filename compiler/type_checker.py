from .data_types import MatrixType, VectorType, IntType, SymbolTable
from lark import Tree


class TypeChecker:
    def __init__(self):
        self.symbols = SymbolTable()
        self.substitutions = {}        
        self._fresh_counter = 0

    def fresh_var(self):
        self._fresh_counter += 1
        return f"$s{self._fresh_counter}"

    def resolve(self, name):
        while name in self.substitutions:
            name = self.substitutions[name]
        return name

    def unify_dim(self, d1, d2):
        r1 = self.resolve(d1)
        r2 = self.resolve(d2)
        if r1 == r2:
            return r1
        if r1.startswith('$'):
            self.substitutions[r1] = r2
            return r2
        if r2.startswith('$'):
            self.substitutions[r2] = r1
            return r1
        raise TypeError(f"Cannot unify dimension '{r1}' with '{r2}'")

    def unify_type(self, t1, t2):
        if isinstance(t1, MatrixType) and isinstance(t2, MatrixType):
            if t1.semiring != t2.semiring:
                raise TypeError(f"Semiring mismatch: {t1.semiring} vs {t2.semiring}")
            rows = self.unify_dim(t1.rows, t2.rows)
            cols = self.unify_dim(t1.cols, t2.cols)
            return MatrixType(rows, cols, t1.semiring)

        if isinstance(t1, VectorType) and isinstance(t2, VectorType):
            if t1.semiring != t2.semiring:
                raise TypeError(f"Semiring mismatch: {t1.semiring} vs {t2.semiring}")
            size = self.unify_dim(t1.size, t2.size)
            return VectorType(size, t1.semiring)

        if isinstance(t1, IntType) and isinstance(t2, IntType):
            return IntType()

        raise TypeError(f"Cannot unify {t1} with {t2}")

    def check_assignment(self, node):
        var_name = str(node.children[0].children[0])
        right_type = self.check_expression(node.children[1])
        old_type = self.symbols.lookup(var_name)
        if old_type is not None:
            right_type = self.unify_type(old_type, right_type)
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
        return self.unify_type(left_type, right_type)

    def check_multiplication(self, left_type, right_type):
        if not isinstance(right_type, MatrixType):
            raise TypeError("Right operand must be a matrix")
        if left_type.semiring != right_type.semiring:
            raise TypeError("Matrices must use the same semiring")
        if isinstance(left_type, MatrixType):
            self.unify_dim(left_type.cols, right_type.rows)
            rows = self.resolve(left_type.rows)
            cols = self.resolve(right_type.cols)
            return MatrixType(rows, cols, left_type.semiring)
        elif isinstance(left_type, VectorType):
            self.unify_dim(left_type.size, right_type.rows)
            size = self.resolve(right_type.cols)
            return VectorType(size, left_type.semiring)
        else:
            raise TypeError("Left operand must be a matrix or vector")

    def check_transpose(self, type_):
        if not isinstance(type_, MatrixType):
            raise TypeError("Only matrices can be transposed")
        return MatrixType(type_.cols, type_.rows, type_.semiring)

    def check_elementwise_multiply(self, left_type, right_type):
        return self.unify_type(left_type, right_type)

    def check_pick_any(self, arg_type):
        if not isinstance(arg_type, MatrixType):
            raise TypeError("pickAny expects a Matrix argument")
        return arg_type

    def check_square_matrix_func(self, arg_type):
        if not isinstance(arg_type, MatrixType):
            raise TypeError("Not a matrix")
        u = self.unify_dim(arg_type.rows, arg_type.cols)
        return MatrixType(u, u, arg_type.semiring)

    def check_reach(self, source_type, g_type):
        if not isinstance(source_type, VectorType):
            raise TypeError("reach: first argument must be a Vector")
        g_type = self.check_square_matrix_func(g_type)
        size = self.unify_dim(source_type.size, g_type.rows)
        if source_type.semiring != g_type.semiring:
            raise TypeError(
            f"reach: semiring mismatch, "
            f"source is {source_type.semiring}, matrix is {g_type.semiring}")
        return VectorType(size, source_type.semiring)

    def check_eye(self, arg_type):
        if not isinstance(arg_type, IntType):
            raise TypeError("Argument must be a number")
        new_type = self.fresh_var()
        return MatrixType(new_type, new_type, 'bool')


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
            return self.check_eye(arg_type)
        raise TypeError(f"Unknown function: {func_name}")

    def check_func_call_2arg(self, node):
        func_name = str(node.children[0])
        first_type = self.check_expression(node.children[1])
        second_type = self.check_expression(node.children[2])
        if func_name == "reach":
            return self.check_reach(first_type, second_type)
        raise TypeError(f"Unknown function: {func_name}")

    def check_statement(self, node):
        if node.data == "assignment":
            return self.check_assignment(node)
        if node.data == "for_stmt":
            return self.check_for_stmt(node)
        raise TypeError(f"Unknown statement: {node.data}")

    def check_for_stmt(self, node):
        matrix_name = node.children[1].children[0]
        type_ = self.check_identifier(matrix_name)
        if not isinstance(type_, MatrixType):
            raise TypeError("Not a Matrix")
        name = node.children[0].children[0]
        self.symbols.define(name, IntType())
        for stmt_wrapper in node.children[3:]:
            stmt = stmt_wrapper.children[0]
            self.check_statement(stmt)
        return None

    def check_func_decl(self, node):
        params = node.children[1]
        declared_type = node.children[2]
        body = node.children[3:]
        self.add_parameters(params)
        result = None
        for elem in body:
            if isinstance(elem, Tree) and elem.data == "statement":
                elem = elem.children[0]
            if isinstance(elem, Tree) and elem.data == "return_stmt":
                result = self.check_return_stmt(elem, declared_type)
            else:
                self.check_statement(elem)
        return result


    def check_return_stmt(self, node, declared_type):
        return_expr = node.children[0]
        actual_type = self.check_expression(return_expr)
        return self.unify_type(declared_type, actual_type)

