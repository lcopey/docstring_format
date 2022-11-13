from unittest import TestCase
import json
import ast
from pathlib import Path
from docstring_format.base import get_docstring_lines, get_docstring_sections, annotate_function


class TestBase(TestCase):
    def setUp(self) -> None:
        with open('./dummy_results.json', mode='r') as f:
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
            assert start == result['start'] and length == result['length']

    def test_docstring_section(self):
        for func in self.functions:
            result = self.results[func.name]
            start, length = get_docstring_lines(func, self.dirty_lines)
            docstring = '\n'.join(self.dirty_lines[start:start + length])
            sections = get_docstring_sections(docstring)
            assert result['sections'] == sections.to_dict()

    def test_annotate_function(self):
        for func in self.functions:
            result = self.results[func.name]
            docstring = annotate_function(func, self.dirty_lines)

            assert result['docstring'] == docstring
