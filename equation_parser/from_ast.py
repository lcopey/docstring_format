import ast
from typing import Union

from structlog import getLogger

from .base import BinaryNode, ConstantNode, Node, UnaryNode, VariableNode
from .constants import RESERVED_NAME, Operators

logger = getLogger()

OPERATORS_MAP = {
    ast.Add: Operators.ADD,
    ast.Sub: Operators.SUB,
    ast.Mult: Operators.MUL,
    ast.Div: Operators.DIV,
    ast.Pow: Operators.POW,
    ast.USub: Operators.NEG,
    ast.UAdd: Operators.ID,
    "sin": Operators.SIN,
    "cos": Operators.COS,
    "tan": Operators.TAN,
    "atan": Operators.ATAN,
    "arctan": Operators.ATAN,
    "arctan2": Operators.ATAN,
    "abs": Operators.ABS,
    "exp": Operators.EXP,
    "delta": Operators.DELTA,
    "b100": Operators.B100,
    "sqrt": Operators.SQRT,
}


def eval_node(ast_node: Union[ast.Constant, ast.Name, ast.BinOp, ast.UnaryOp]) -> Node:
    """Evaluate and dispatch to one of eval method depending on the type of ast_node"""
    log = logger.bind(func="eval node")
    log.debug(ast_node)
    func = AST_EVALUATORS[type(ast_node)]
    return func(ast_node)


def eval_binop(ast_node: ast.BinOp) -> BinaryNode:
    """Defines a binary node"""
    log = logger.bind(func="eval binop")
    log.debug(ast.dump(ast_node))
    op_type = OPERATORS_MAP[type(ast_node.op)]
    return BinaryNode(
        left=eval_node(ast_node.left),
        right=eval_node(ast_node.right),
        func_type=op_type,
    )


def eval_constant(ast_node: Union[ast.Constant, ast.Num]) -> ConstantNode:
    """Defines a constant node"""
    log = logger.bind(func="eval constant")
    log.debug(ast.dump(ast_node))
    if isinstance(ast_node, ast.Constant):
        return ConstantNode(value=ast_node.value)
    else:
        return ConstantNode(value=ast_node.n)


def eval_name(ast_node: ast.Name) -> Union[VariableNode, ConstantNode]:
    """Defines a variable node"""
    log = logger.bind(func="eval name")
    log.debug(ast.dump(ast_node))
    if ast_node.id in RESERVED_NAME.keys():
        return ConstantNode(value=ast_node.id)
    else:
        return VariableNode(value=ast_node.id)


def eval_unaryop(ast_node: ast.UnaryOp) -> UnaryNode:
    """Defines a unary operation node"""
    log = logger.bind(func="eval unary")
    log.debug(ast.dump(ast_node))
    op_type = OPERATORS_MAP[type(ast_node.op)]
    return UnaryNode(func_type=op_type, value=eval_node(ast_node.operand))


def eval_call(ast_node: ast.Call) -> UnaryNode:
    """Evaluate function call, mainly supports unary function such as sin and cos"""
    log = logger.bind(func="eval Call")
    log.debug(ast.dump(ast_node))
    op_type = OPERATORS_MAP[ast_node.func.id.lower()]
    arg = ast_node.args[0]
    return UnaryNode(func_type=op_type, value=eval_node(arg))


def from_string(equation_string: str) -> Node:
    """Build a tree starting from an equation string"""
    log = logger.bind(func="build tree")
    log.debug("Start building")
    ast_node = ast.parse(equation_string, "<string>", mode="eval")
    if isinstance(ast_node, ast.Expression):
        node_value = ast_node.body
    else:
        node_value = ast_node
    return eval_node(node_value)


AST_EVALUATORS = {
    ast.Constant: eval_constant,
    ast.Name: eval_name,
    ast.BinOp: eval_binop,
    ast.UnaryOp: eval_unaryop,
    ast.Call: eval_call,
    ast.Num: eval_constant,
}
