"""Test module"""
import json
from dataclasses import asdict
from pathlib import Path
from unittest import TestCase

from docstring_format import Docstring, ScriptFile, SectionType
from docstring_format.base import (get_docstring_start_and_length,
                                   get_functions, parse_sections)


def load_test_results():
    """Convenience function load test results."""
    with open('./dummy_test_functions_results.json', mode='r') as f:
        results = json.load(f)

    section_map = {str(item): item for item in SectionType}
    for item in results['parse_sections']:
        item['type'] = section_map[item['type']]  # SectionType are enum stored as string

    for item in results['docstrings']:
        for section in item['sections']:
            section['type'] = section_map[section['type']]  # as above, SectionType are enum stored as string

    return results


class TestFunctions(TestCase):
    def setUp(self) -> None:
        with open('./dummy_test_functions_results.json', mode='r') as f:
            self.results = json.load(f)

    def test_functions(self):
        """Check if functions are correctly loaded"""
        file_path = './dummy_tests_functions.py'
        file = Path(file_path)
        raw_text = file.read_text()
        functions = get_functions(raw_text)
        self.assertEqual([func.name for func in functions], self.results['get_functions'])


class TestDocstring(TestCase):
    def setUp(self) -> None:
        self.results = load_test_results()
        file_path = './dummy_tests_functions.py'
        file = Path(file_path)
        self.raw_text = file.read_text()
        self.lines = self.raw_text.splitlines()
        self.functions = get_functions(self.raw_text)

    def test_docstring_start_and_length(self):
        start_and_length = [list(get_docstring_start_and_length(func, self.lines)) for func in self.functions]
        self.assertEqual(start_and_length, self.results['get_docstring_start_and_length'])

    def test_parse_sections(self):
        sections = [parse_sections(func, self.lines) for func in self.functions]
        sections = [asdict(section) for item in sections for section in item]
        self.assertEqual(sections, self.results['parse_sections'])

    def test_sections_cleaned(self):
        sections = [parse_sections(func, self.lines) for func in self.functions]
        cleaned = [section.cleaned for item in sections for section in item]
        self.assertEqual(cleaned, self.results['sections_cleaned'])

    def test_init_docstrings(self):
        docstrings = [Docstring.from_ast(func, self.lines) for func in self.functions]
        docstrings = [{k: v for k, v in asdict(docstring).items() if k != 'function'}
                      for docstring in docstrings]
        self.assertEqual(docstrings, self.results['docstrings'])

    def test_docstrings_cleaned(self):
        docstrings = [Docstring.from_ast(func, self.lines) for func in self.functions]
        cleaned = [docstring.cleaned for docstring in docstrings]
        self.assertEqual(cleaned, self.results['docstrings_cleaned'])


class TestScriptFile(TestCase):
    def setUp(self) -> None:
        self.results = load_test_results()
        self.file_path = './dummy_tests_functions.py'

    def test_init(self):
        script = ScriptFile(self.file_path)

    def test_cleaned(self):
        script = ScriptFile(self.file_path)
        cleaned = script.cleaned
        self.assertEqual(cleaned, self.results['script_cleaned'])
