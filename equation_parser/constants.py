import math
import operator
from enum import Enum

import numpy as np

from .functions import delta, identity, relative_percentage

RESERVED_NAME = {"pi": math.pi}


class NodeType(str, Enum):
    """Convenience enumeration of node type"""

    Unary = "unary"
    Binary = "binary"
    Constant = "constant"
    Variable = "variable"


class Operators(str, Enum):
    """Convenience enumeration listing supported operation"""

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    POW = "pow"
    NEG = "neg"
    ID = "id"
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    ATAN = "atan"
    ABS = "abs"
    EXP = "exp"
    B100 = "b100"
    DELTA = "delta"
    SQRT = "sqrt"

    @staticmethod
    def get(value):
        """Return the function corresponding the enumeration value"""
        return OPERATORS_FUNC.get(value)


OPERATORS_FUNC = {
    Operators.ADD: operator.add,
    Operators.SUB: operator.sub,
    Operators.MUL: operator.mul,
    Operators.DIV: operator.truediv,
    Operators.POW: operator.pow,
    Operators.NEG: operator.neg,
    Operators.ID: identity,
    Operators.SIN: np.sin,
    Operators.COS: np.cos,
    Operators.TAN: np.tan,
    Operators.ATAN: np.arctan2,
    Operators.ABS: np.abs,
    Operators.EXP: np.exp,
    Operators.B100: relative_percentage,
    Operators.DELTA: delta,
    Operators.SQRT: np.sqrt,
}
