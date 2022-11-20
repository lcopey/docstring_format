import ast
import json
from pathlib import Path
from unittest import TestCase

from docstring_format.base import (annotate_function, get_docstring,
                                   get_docstring_lines, get_docstring_sections)


class TestFunctions(TestCase):
    def setUp(self) -> None:
        with open('./dummy_test_functions_results.json', mode='r') as f:
            self.results = json.load(f)
        file = Path('./dummy_tests_functions.py')
        raw_text = file.read_text()
        self.dirty_lines = raw_text.splitlines()
        self.parsed = ast.parse(raw_text)
        self.functions = [item for item in self.parsed.body if isinstance(item, ast.FunctionDef)]

    def test_docstring_start_and_length(self):
        for func in self.functions:
            result = self.results[func.name]  # may fail if json file is not up to date
            start, length = get_docstring_lines(func, self.dirty_lines)
            self.assertEqual(start, result['start'])
            self.assertEqual(length, result['length'])

    def test_docstring_section(self):
        for func in self.functions:
            result = self.results[func.name]
            docstring = get_docstring(func, self.dirty_lines)
            sections = get_docstring_sections(docstring)
            self.assertEqual(result['sections'], sections.to_dict())

    def test_annotate_function(self):
        for func in self.functions:
            print(func.name)
            result = self.results[func.name]
            docstring = annotate_function(func, self.dirty_lines)

            self.assertEqual(result['docstring'], docstring)
