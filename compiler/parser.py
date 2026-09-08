from lark import Transformer, Tree
from .data_types import MatrixType, VectorType, IntType
from .grammar import grammar


class DesugarAssignment(Transformer):
    
    def IDENTIFIER(self, token):
        return Tree("identifier", [str(token)])

    def NUMBER(self, token):
        return Tree("number", [int(token)])

    def addition(self, items):
        if len(items) == 1:
            return items[0]

        result = items[0]
        for item in items[1:]:
            result = Tree("addition", [result, item])
        return result

    def addition_assignment(self, items):
            var, expr = items
            addition = Tree('addition', [var, expr])
            return Tree('assignment', [var, addition])

    def multiplication(self, items):
        if len(items) == 1:
            return items[0]

        result = items[0]
        for item in items[1:]:
            result = Tree("multiplication", [result, item])
        return result


    def atom(self, items):
        return items[0]

    def postfix(self, items):
        result = items[0]

        for operation in items[1:]:
            if isinstance(operation, Tree):
                if operation.data == "transpose":
                    result = Tree("transpose", [result])

                elif operation.data == "method_call":
                    result = Tree(
                        "elementwise_multiply",
                        [result, operation.children[0]]
                    )

        return result

    def expression(self, items):
        return items[0]

    def matrix_type(self, items):
        rows, cols, semiring = items
        return MatrixType(rows.children[0], cols.children[0], semiring.children[0])

    def vector_type(self, items):
        size, semiring = items
        return VectorType(size.children[0], semiring.children[0])

    def int_type(self, items):
        return IntType()
    
    def type(self, items):
        return items[0]




