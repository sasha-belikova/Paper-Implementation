from dataclasses import dataclass

@dataclass
class MatrixType:
    rows: str
    cols: str
    semiring: str


@dataclass
class VectorType:
    size: str
    semiring: str


@dataclass
class IntType:
    pass



class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def define(self, name, type_):
        self.symbols[name] = type_

    def lookup(self, name):
        return self.symbols.get(name)