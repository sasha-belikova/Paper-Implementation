from lark import Lark, Transformer, Tree, Token

grammar = """
start: func_decl

func_decl: "func" IDENTIFIER "(" params ")" "->" type "{" statement* return_stmt "}"

statement: (assignment | addition_assignment | for_stmt) ";"?
for_stmt: "for" IDENTIFIER "in" IDENTIFIER "." ("nrows"| "ncols") "{" statement* "}"
return_stmt: "return" expression ";"

expression: addition

addition: multiplication ("+" multiplication)*
multiplication: postfix ("*" postfix)*
postfix: atom (method_call | transpose)*
method_call: ".multiply" "(" expression ")"
transpose: ".T"

atom: NUMBER | IDENTIFIER | func_call_1arg | func_call_2arg
assignment: IDENTIFIER "=" expression
addition_assignment: IDENTIFIER "+=" expression

param: IDENTIFIER ":" type
params: [param ("," param)*]

type: matrix_type | vector_type | int_type
matrix_type: "Matrix" "<" IDENTIFIER "," IDENTIFIER "," IDENTIFIER ">"
vector_type: "Vector" "<" IDENTIFIER "," IDENTIFIER ">"
int_type: "int"

func_call_1arg: ("eye" | "pickAny" | "WCC" | "SCC") "(" expression ")"
func_call_2arg: "reach" "(" expression "," expression ")"

NUMBER: /[0-9]+/
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS
"""


class DesugarAssignment(Transformer):
    def addition_assignment(self, items):
        var, expr = items
        addition = Tree('addition', [var, expr])
        return Tree('assignment', [var, addition])
    
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


