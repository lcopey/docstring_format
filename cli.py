import ast
import json
from pathlib import Path

from typer import Typer

from docstring_format.base import (annotate_function, get_docstring_lines,
                                   get_docstring_sections)

app = Typer()


@app.command()
def generate_functions_tests():
    file = Path('./tests/dummy_tests_functions.py')

    raw_text = file.read_text()
    dirty_lines = raw_text.splitlines()
    tree = ast.parse(raw_text)

    # classes = [item for item in tree.body if isinstance(item, ast.ClassDef)]
    # class_methods = [func for item in classes for func in item.body if isinstance(func, ast.FunctionDef)]

    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef)]

    results = {}
    for func in functions:
        start, length = get_docstring_lines(func, dirty_lines)
        results[func.name] = dict(zip(('start', 'length'), (start, length)))

        docstring = '\n'.join(dirty_lines[start:start + length])
        results[func.name]['sections'] = get_docstring_sections(docstring).to_dict()

        results[func.name]['docstring'] = annotate_function(func, dirty_lines)

    with open('./tests/dummy_test_functions_results.json', mode='w') as f:
        json.dump(results, f, indent=4)


if __name__ == '__main__':
    app()
