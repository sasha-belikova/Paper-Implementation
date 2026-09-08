import argparse
import json
import numpy as np
from scipy.sparse import csr_matrix
from lark import Lark
from compiler.grammar import grammar
from compiler.parser import DesugarAssignment
from compiler.data_types import IntType
from compiler.runner import run_program

_parser = Lark(grammar, parser="lalr")


def get_param_types(code):
    tree = _parser.parse(code)
    tree = DesugarAssignment().transform(tree)
    func = tree.children[0]
    params = func.children[1]
    types = {}
    for param in params.children:
        name = param.children[0]
        param_name = str(name.children[0])
        types[param_name] = param.children[1]
    return types


def load_arguments(path, param_types):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    arguments = {}
    for name, value in data.items():
        type_ = param_types.get(name)
        if isinstance(type_, IntType):
            arguments[name] = int(value)
        else:
            arguments[name] = csr_matrix(np.array(value, dtype=bool))
    return arguments


def main():
    parser = argparse.ArgumentParser(description="Run a GraphAlg-Implementation program.")
    parser.add_argument("program", help="Path to a .graph program")
    parser.add_argument(
        "--args",
        required=True,
        help="Path to a JSON file containing program arguments")
    args = parser.parse_args()
    with open(args.program, "r", encoding="utf-8") as file:
        code = file.read()
    param_types = get_param_types(code)
    arguments = load_arguments(args.args, param_types)
    result = run_program(code, arguments)
    print(result.toarray())


if __name__ == "__main__":
    main()