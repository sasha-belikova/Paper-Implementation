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