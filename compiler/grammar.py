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

func_call_1arg: FUNC_NAME_1ARG "(" expression ")"
func_call_2arg: FUNC_NAME_2ARG "(" expression "," expression ")"

FUNC_NAME_1ARG.2: "eye" | "pickAny" | "WCC" | "SCC"
FUNC_NAME_2ARG.2: "reach"
NUMBER: /[0-9]+/
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS
"""