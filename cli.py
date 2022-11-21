import json
from pathlib import Path
from dataclasses import asdict

from typer import Typer
from docstring_format.base import get_functions, parse_sections, Docstring, ScriptFile

app = Typer()


@app.command()
def generate_functions_tests():
    file_path = './tests/dummy_tests_functions.py'
    file = Path(file_path)
    raw_text = file.read_text()
    lines = raw_text.splitlines()

    results = {}

    functions = get_functions(raw_text)
    results['get_functions'] = [func.name for func in functions]

    docstrings = [Docstring.from_ast(func, lines) for func in functions]
    results['get_docstring_start_and_length'] = [(docstring.start, docstring.length)
                                                 for docstring in docstrings]

    sections = [parse_sections(func, lines) for func in functions]
    results['parse_sections'] = [asdict(section) for item in sections for section in item]

    # remove function attribute from test
    results['docstrings'] = [{k: v for k, v in asdict(docstring).items() if k != 'function'}
                             for docstring in docstrings]

    results['sections_cleaned'] = [section.cleaned for item in sections for section in item]

    results['docstrings_cleaned'] = [docstring.cleaned for docstring in docstrings]

    script = ScriptFile(file_path)
    results['script_cleaned'] = script.cleaned

    with open('./tests/dummy_test_functions_results.json', mode='w') as f:
        json.dump(results, f, indent=4, default=str)


if __name__ == '__main__':
    app()
