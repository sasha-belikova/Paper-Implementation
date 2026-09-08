from lark import Lark
from compiler.grammar import grammar
from compiler.parser import DesugarAssignment
from compiler.type_checker import TypeChecker
from compiler.interpreter import Interpreter

parser = Lark(grammar, parser="lalr")


def run_program(code, arguments):
    tree = parser.parse(code)
    tree = DesugarAssignment().transform(tree)

    func = tree.children[0]

    checker = TypeChecker()
    checker.check_func_decl(func)

    interpreter = Interpreter()
    return interpreter.run_func_decl(func, arguments)