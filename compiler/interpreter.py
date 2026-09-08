from .data_types import SymbolTable
from scipy.sparse import eye
from python_prototypes import pickAny, WCC, SCC, reach
from lark import Tree


class Interpreter:
    def __init__(self):
        self.symbols = SymbolTable()

    def add_parameters(self, params, arguments):
        for param in params.children:
            name = param.children[0]
            param_name = str(name.children[0])
            arg = arguments[param_name]
            self.symbols.define(param_name, arg)

    def eval_identifier(self, name):
        arg = self.symbols.lookup(name)
        if arg is None:
            raise NameError(f"Undefined variable: {name}")
        return arg

    def eval_addition(self, left, right):
        return left + right

    def eval_multiplication(self, left, right):
        return left @ right

    def eval_elementwise_multiply(self, left, right):
            return left.multiply(right)

    def eval_transpose(self, arg):
        return arg.T

    def eval_func_call_1arg(self, node):
        func_name = str(node.children[0])
        arg = self.eval_expression(node.children[1])
        if func_name == "pickAny":
            return pickAny(arg)
        if func_name in ("WCC", "SCC"):
            return WCC(arg) if func_name == "WCC" else SCC(arg)
        if func_name == "eye":
            return eye(arg, dtype=bool, format='csr')
        raise NotImplementedError(f"Unknown function: {func_name}")

    def eval_func_call_2arg(self, node):
        func_name = str(node.children[0])
        first = self.eval_expression(node.children[1])
        second = self.eval_expression(node.children[2])
        if func_name == "reach":
            return reach(first, second)
        raise NotImplementedError(f"Unknown function: {func_name}")

    def eval_expression(self, node):
        if node.data == "identifier":
            name = node.children[0]
            return self.eval_identifier(name)
        if node.data == "number":
            return node.children[0]
        if node.data == "addition":
            left = self.eval_expression(node.children[0])
            right = self.eval_expression(node.children[1])
            return self.eval_addition(left, right)
        if node.data == "multiplication":
            left = self.eval_expression(node.children[0])
            right = self.eval_expression(node.children[1])
            return self.eval_multiplication(left, right)
        if node.data == "elementwise_multiply":
            left = self.eval_expression(node.children[0])
            right = self.eval_expression(node.children[1])
            return self.eval_elementwise_multiply(left, right)
        if node.data == "transpose":
            arg = self.eval_expression(node.children[0])
            return self.eval_transpose(arg)
        if node.data == "func_call_1arg":
            return self.eval_func_call_1arg(node)
        if node.data == "func_call_2arg":
            return self.eval_func_call_2arg(node) 
        raise NotImplementedError(f"Unknown expression: {node.data}")



    def eval_assignment(self, node):
        var_name = str(node.children[0].children[0])
        value = self.eval_expression(node.children[1])
        self.symbols.define(var_name, value)
        return value

    def eval_for_stmt(self, node):
        matrix_name = node.children[1].children[0]
        matrix = self.eval_identifier(matrix_name)
        dimension = str(node.children[2])
        if dimension == "nrows":
            iterations = matrix.shape[0]
        elif dimension == "ncols":
            iterations = matrix.shape[1]
        else:
            raise ValueError(f"Unknown matrix dimension: {dimension}")
        name = node.children[0].children[0]
        for i in range(iterations):
            self.symbols.define(name, i)
            for stmt_wrapper in node.children[2:]:   # <-- баг
                stmt = stmt_wrapper.children[0]
                self.eval_statement(stmt)

    def eval_statement(self, node):
        if node.data == "assignment":
            return self.eval_assignment(node)
        if node.data == "for_stmt":
            return self.eval_for_stmt(node)
        raise NotImplementedError(f"Unknown statement: {node.data}")

    def eval_return_stmt(self, node):
        return self.eval_expression(node.children[0])

    def run_func_decl(self, node, arguments):
        params = node.children[1]
        body = node.children[3:]
        self.add_parameters(params, arguments)
        for elem in body:
            if isinstance(elem, Tree) and elem.data == "statement":
                elem = elem.children[0]
            if isinstance(elem, Tree) and elem.data == "return_stmt":
                return self.eval_return_stmt(elem)
            self.eval_statement(elem)

