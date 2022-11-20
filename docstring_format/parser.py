"""Module implementing the conversion of annotations ast object into string."""
import ast
from typing import Any, Optional


def eval_str(node) -> str:
    """Evaluate string node"""
    return node.s


def eval_name(node) -> str:
    """Evaluate name node"""
    return node.id


def eval_index(node) -> str:
    """Evaluate index node"""
    return eval_node(node.value)


def eval_tuple(node) -> str:
    """"Evaluate tuple node"""
    return ', '.join((eval_node(item) for item in node.elts))


def eval_attribute(node) -> str:
    """Evaluate attribute node"""
    return f'{eval_node(node.value)}.{node.attr}'


def eval_constant(node) -> str:
    """Evaluate constant node"""
    return node.value


def eval_subscript(node) -> str:
    """Evaluate subscript node"""
    return f'{eval_node(node.value)}[{eval_node(node.slice)}]'


def eval_node(node: Any) -> str:
    """Entry point for the graph walk"""
    node_class = type(node)
    return EVAL_MAP[node_class](node)


def parse_annotation(item: ast.arg) -> Optional[str]:
    """Parse annotations from an argument"""
    if hasattr(item, 'annotation') and item.annotation:
        return eval_node(item.annotation)


def parse_returns(item: ast.FunctionDef) -> Optional[str]:
    """Parse the return item from the function definition"""
    if hasattr(item, 'returns') and item.returns:
        return eval_node(item.returns)


EVAL_MAP = {ast.Name: eval_name,
            ast.Constant: eval_constant,
            ast.Index: eval_index,
            ast.Tuple: eval_tuple,
            ast.Attribute: eval_attribute,
            ast.Subscript: eval_subscript,
            ast.Str: eval_str}
