import ast


def eval_str(node) -> str:
    return node.s


def eval_name(node) -> str:
    return node.id


def eval_index(node) -> str:
    return eval_node(node.value)


def eval_tuple(node) -> str:
    return ', '.join((eval_node(item) for item in node.elts))


def eval_attribute(node) -> str:
    return f'{eval_node(node.value)}.{node.attr}'


def eval_constant(node) -> str:
    return node.value


def eval_node(node) -> str:
    node_class = type(node)
    return EVAL_MAP[node_class](node)


def eval_subscript(node) -> str:
    return f'{eval_node(node.value)}[{eval_node(node.slice)}]'


def parse_annotation(item: ast.arg):
    return eval_node(item.annotation)


EVAL_MAP = {ast.Name: eval_name,
            ast.Constant: eval_constant,
            ast.Index: eval_index,
            ast.Tuple: eval_tuple,
            ast.Attribute: eval_attribute,
            ast.Subscript: eval_subscript,
            ast.Str: eval_str}
