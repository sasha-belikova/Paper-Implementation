from lark import Lark, Transformer, Tree, Token

grammar = """
start: func_decl

func_decl: "func" IDENTIFIER "(" params ")" "->" type "{" statement* return_stmt "}"

statement: (assignment | addition_assignment | for_stmt) ";"?
for_stmt: "for" IDENTIFIER "in" IDENTIFIER "." "nrows" "{" statement* "}"
return_stmt: "return" IDENTIFIER ";"

expression: NUMBER | IDENTIFIER | multiplication

multiplication: IDENTIFIER "*" IDENTIFIER 
assignment: IDENTIFIER "=" expression
addition_assignment: IDENTIFIER "+=" expression

param: IDENTIFIER ":" type
params: param ("," param)*

type: matrix_type | vektor_type
matrix_type: "Matrix" "<" IDENTIFIER "," IDENTIFIER "," IDENTIFIER ">"
vektor_type: "Vector" "<" IDENTIFIER "," IDENTIFIER ">"

NUMBER: /[0-9]+/
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS
"""

parser = Lark(grammar)

class DesugarAssignment(Transformer):
    def addition_assignment(self, items):
        var, expr = items
        addition = Tree('addition', [var, expr])
        return Tree('assignment', [var, addition])
    