"""Implements base objects for docstring cleaning."""
import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .annotation_parser import parse_annotation, parse_returns
from .numpy_style import apply_numpy_style
from .utils import DELIMITERS, DocstringStyle, SectionType, DOCSTRING_TAGS


@dataclass
class DocstringSection:
    """Implements docstring section"""
    name: str
    type: SectionType
    start: Optional[int] = None
    length: Optional[int] = None
    offset: Optional[str] = None
    lines: Optional[list[str]] = None
    annotation: Optional[str] = None

    @property
    def cleaned(self):
        """Returns cleaned section."""
        return apply_numpy_style(self)


@dataclass
class Docstring:
    """Docstring base structure."""
    function: ast.FunctionDef
    lines: list[str]
    start: int
    length: int
    offset: str = field(init=False)
    sections: list[DocstringSection] = field(init=False)

    @classmethod
    def from_ast(cls, func: ast.FunctionDef, raw_text: list[str]):
        """Parse ast tree structure."""
        start, length = get_docstring_start_and_length(func, raw_text)
        docstring_lines = raw_text[start:start + length]
        return cls(func, docstring_lines, start, length)

    def __post_init__(self):
        self.offset = re.search(r'(\s*)', self.lines[0]).group()
        self.sections = parse_sections(self.function, self.lines)

    @property
    def cleaned(self):
        """Apply cleaning functions."""
        lines = [line for section in self.sections for line in section.cleaned]
        return [self.offset + '"""', *lines, '', self.offset + '"""']


def get_functions(raw_text: str):
    """Finds the functions in the script file provided as o long str."""
    # TODO walk the nodes ?
    tree = ast.parse(raw_text)

    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef)]
    classes = [item for item in tree.body if isinstance(item, ast.ClassDef)]
    class_methods = [func for item in classes for func in item.body if isinstance(func, ast.FunctionDef)]
    functions.extend(class_methods)
    return functions


class ScriptFile:
    """Base structure handling all functions found in a script file."""

    def __init__(self, file_path: str):
        """ScriptFile are usually initiated from python file."""

        self.file_path = file_path
        file = Path(file_path)
        assert file_path.endswith('.py'), f'{file.name} is not a python script'

        raw_text = file.read_text()
        functions = get_functions(raw_text)
        self.lines = raw_text.splitlines()
        self.docstrings = [Docstring.from_ast(func, self.lines) for func in functions]

    @property
    def cleaned(self):
        """Clean all docstring function found in script"""
        cleaned = self.lines.copy()
        offset = 0
        for docstring in self.docstrings:
            new_docstring = docstring.cleaned
            new_length = len(new_docstring)
            for _ in range(docstring.length):
                cleaned.pop(docstring.start + offset)
            for line in new_docstring[::-1]:
                cleaned.insert(docstring.start + offset, line)
            offset += new_length - docstring.length

        return cleaned

    def write_clean(self):
        """Write in edit file"""
        new_text = '\n'.join(self.cleaned)
        new_file_path = Path(re.sub(r'\.py$', '_edit.py', self.file_path))
        new_file_path.write_text(new_text)


def get_docstring_start_and_length(func: ast.FunctionDef, raw_text: list[str]) -> tuple[int, int]:
    """Get the start and the length of the docstring associated with function."""
    docstring = ast.get_docstring(func)
    tag_search = re.compile(DOCSTRING_TAGS['generic'])  # match """

    def get_tag_from(index, offset=0):
        """Adjust the index by searching triple quote tag."""
        match = re.search(tag_search, raw_text[index + offset])
        while not match:
            index += 1
            match = re.search(tag_search, raw_text[index + offset])

        return index

    # detect start
    start = func.lineno - 1
    start = get_tag_from(start)

    # detect end
    length = len(docstring.splitlines())
    length = get_tag_from(length, offset=start - 1)
    return start, length


def detect_section(token_name: str, raw_text: list[str], section_type: SectionType) -> Optional[DocstringSection]:
    """Generic method to detect a DocstringSection in the docstring."""
    pattern = re.compile(rf'^(\s*)({token_name})')
    for n, line in enumerate(raw_text):
        match = re.search(pattern, line)
        if match:
            offset, _ = match.groups()
            section = DocstringSection(name=token_name,
                                       start=n,
                                       offset=offset,
                                       type=section_type)
            return section


def detect_summary_section(raw_text: list[str]) -> DocstringSection:
    """Detect the Summary section."""
    match = re.search(rf'^(\s*)', raw_text[0])  # match whitespace
    offset = match.group() if match else None
    return DocstringSection(name='Summary', type=SectionType.SUMMARY, start=0, offset=offset)


def detect_param_delimiter_section(raw_text: list[str]):
    """Detect the parameters section."""
    delimiter = DELIMITERS[DocstringStyle.NUMPY]['param']
    return detect_section(delimiter, raw_text, SectionType.PARAMETER_DELIMITER)


def detect_return_section(function: ast.FunctionDef, raw_text: list[str]) -> Optional[DocstringSection]:
    """Detect the returns section."""
    delimiter = DELIMITERS[DocstringStyle.NUMPY]['returns']
    section = detect_section(delimiter, raw_text, SectionType.RETURNS)
    if section is not None:
        section.annotation = parse_returns(function)
        return section


def detect_argument_section(item: ast.arg, raw_text: list[str]) -> Optional[DocstringSection]:
    """"Detect the argument section."""
    token_name = item.arg
    section = detect_section(token_name, raw_text, SectionType.ARG)
    if section is not None:
        section.annotation = parse_annotation(item)
        return section


def parse_sections(function: ast.FunctionDef, raw_text: list[str]) -> list[DocstringSection]:
    """Split the docstring into multiple sections."""
    # TODO Auto detect docstring style
    sections = [detect_summary_section(raw_text)]
    for item in function.args.args:
        section = detect_argument_section(item, raw_text)
        if section is not None:
            sections.append(section)

    section = detect_param_delimiter_section(raw_text)
    if section is not None:
        sections.append(section)

    section = detect_return_section(function, raw_text)
    if section is not None:
        sections.append(section)

    # sort and define the length of each section
    sections.sort(key=lambda x: x.start)
    for n, item in enumerate(sections):
        if n < len(sections) - 1:
            item.length = sections[n + 1].start - item.start
        else:
            item.length = len(raw_text) - item.start
        item.lines = raw_text[item.start:item.start + item.length]

    return sections
