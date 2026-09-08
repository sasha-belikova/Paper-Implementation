import argparse
import json
import numpy as np
from scipy.sparse import csr_matrix
from compiler.runner import run_program


def load_arguments(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    arguments = {}
    for name, value in data.items():
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
    arguments = load_arguments(args.args)
    result = run_program(code, arguments)
    print(result.toarray())


if __name__ == "__main__":
    main()