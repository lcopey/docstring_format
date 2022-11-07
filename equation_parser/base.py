"""Implement base object that constitutes the tree of computation"""
from collections import OrderedDict
from typing import Union

import pandas as pd

from .constants import RESERVED_NAME, NodeType, Operators


class Node:
    """Basic structure for all nodes"""

    def __repr__(self, level=0):
        if level == 0:
            sep = ""
        else:
            sep = "    " * (level - 1) + " |--"
        return f"{sep}<{self.__class__.__name__}>"

    def eval(self, *args, **kwargs):
        """General evaluation method"""
        raise NotImplementedError

    def serialize(self) -> OrderedDict:
        """Serialize to dict"""
        raise NotImplementedError

    def __eq__(self, other: "Node"):
        return self.serialize() == other.serialize()

    @classmethod
    def from_dict(cls, datas: dict):
        """Instantiate the tree structure from existing serialized Tree as dictionary"""
        node_type = datas.pop("type")
        node_class = NODES_DEFINITION[node_type]
        return node_class(**datas)


class UnaryNode(Node):
    """Node implementing unary operation"""

    def __init__(self, value: Union[Node, dict], func_type):
        if isinstance(value, dict):
            value = Node.from_dict(value)
        self.value: Node = value
        self.func_type = func_type
        self.func = Operators.get(func_type)

    def eval(self, datas: pd.DataFrame, *args, **kwargs):
        """Apply func to value"""
        return self.func(self.value.eval(datas, *args, **kwargs), *args, **kwargs)

    def serialize(self) -> OrderedDict:
        """Serialize to Ordered dict"""
        return OrderedDict(
            [
                ("type", NodeType.Unary),
                ("value", self.value.serialize()),
                ("func_type", self.func_type),
            ]
        )

    def __repr__(self, level=0):
        return (
            f"""{super().__repr__(level)}: {self.func_type}\n"""
            f"""{self.value.__repr__(level + 1)}"""
        )


class BinaryNode(Node):
    """Node implementing binary operation"""

    def __init__(self, left: Union[Node, dict], right: Union[Node, dict], func_type):
        if isinstance(left, dict):
            left = Node.from_dict(left)
        if isinstance(right, dict):
            right = Node.from_dict(right)
        self.left = left
        self.right = right
        self.func_type = func_type
        self.func = Operators.get(func_type)

    def eval(self, datas: pd.DataFrame, *args, **kwargs):
        """Apply func to left and right value"""
        return self.func(
            self.left.eval(datas, *args, **kwargs),
            self.right.eval(datas, *args, **kwargs),
        )

    def serialize(self) -> OrderedDict:
        return OrderedDict(
            [
                ("type", NodeType.Binary),
                ("left", self.left.serialize()),
                ("right", self.right.serialize()),
                ("func_type", self.func_type),
            ]
        )

    def __repr__(self, level=0):
        return (
            f"""{super().__repr__(level)}: {self.func_type}\n"""
            f"""{self.left.__repr__(level + 1)}\n"""
            f"""{self.right.__repr__(level + 1)}"""
        )


class TerminalNode(Node):
    """Base class for terminal Node"""

    def __init__(self, value):
        self.value = value

    def __repr__(self, level=0):
        return f"""{super().__repr__(level)}: {self.value}"""

    def eval(self, *args, **kwargs):
        raise NotImplementedError

    def serialize(self) -> OrderedDict:
        raise NotImplementedError


class ConstantNode(TerminalNode):
    """Node implementing constant value"""

    def eval(self, datas: pd.DataFrame, *args, **kwargs):
        """Return value"""
        if self.value in RESERVED_NAME.keys():
            return RESERVED_NAME[self.value]
        return self.value

    def serialize(self) -> OrderedDict:
        """Serialize as OrderedDict"""
        return OrderedDict([("type", NodeType.Constant), ("value", self.value)])


class VariableNode(TerminalNode):
    """Node implementing variable name"""

    def eval(self, datas: pd.DataFrame, *args, **kwargs):
        """Return the columns in datas named value"""
        return datas[self.value]

    def serialize(self) -> OrderedDict:
        """Serialize as OrderedDict"""
        return OrderedDict([("type", NodeType.Variable), ("value", self.value)])


NODES_DEFINITION = {
    NodeType.Unary: UnaryNode,
    NodeType.Binary: BinaryNode,
    NodeType.Constant: ConstantNode,
    NodeType.Variable: VariableNode,
}
