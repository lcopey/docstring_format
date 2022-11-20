import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .annotations import annotate_section
from .constants import DELIMITERS, DocstringStyle, SectionType
from .parser import parse_annotation, parse_returns


@dataclass
class Section:
    name: str
    type: SectionType
    # TODO useful ?
    start: Optional[int] = None
    length: Optional[int] = None
    offset: Optional[str] = None
    lines: Optional[list[str]] = None
    annotation: Optional[str] = None
    corrected_lines: list[str] = None


@dataclass
class Docstring:
    function: ast.FunctionDef
    lines: list[str]
    start: int
    length: int
    offset: str = field(init=False)
    sections: list[Section] = field(init=False)
    corrected_lines: list[str] = field(init=False, default_factory=list)

    @classmethod
    def from_ast(cls, func: ast.FunctionDef, raw_text: list[str]):
        start, length = get_docstring_start_and_length(func, raw_text)
        # TODO change one for getter instead
        docstring_lines = raw_text[start:start + length]
        return cls(func, docstring_lines, start, length)

    def __post_init__(self):
        self.offset = re.search('(\s*)', self.lines[0]).group()
        self.sections = parse_sections(self.function, self.lines)
        self.corrected_lines = []

    def annotate(self):
        for section in self.sections:
            annotate_section(section)


def get_docstring_start_and_length(func: ast.FunctionDef, raw_text: list[str]) -> tuple[int, int]:
    """Get the start and the length of the docstring associated with func."""
    docstring = ast.get_docstring(func)
    tag_search = re.compile('["\']{3}')

    start = func.lineno - 1
    match = re.search(tag_search, raw_text[start])
    while not match:
        start += 1
        match = re.search(tag_search, raw_text[start])

    tag = match.group()
    length = len(docstring.splitlines())
    match = re.search(tag, raw_text[start + length - 1])
    while not match:
        length += 1
        match = re.search(tag, raw_text[start + length - 1])

    return start, length


def detect_start_section(raw_text) -> Section:
    match = re.search(f'^(\s*)', raw_text[0])
    offset = match.group() if match else None
    section = Section(name='Start', type=SectionType.SUMMARY, start=0, offset=offset)
    return section


def detect_section(token_name: str, raw_text: list[str], type: SectionType) -> Optional[Section]:
    pattern = re.compile(f'^(\s*)({token_name})')
    for n, line in enumerate(raw_text):
        match = re.search(pattern, line)
        if match:
            offset, _ = match.groups()
            section = Section(name=token_name,
                              start=n,
                              offset=offset,
                              type=type)
            return section


def detect_param_section(raw_text: list[str]):
    param_delimiter = DELIMITERS[DocstringStyle.NUMPY]['param']
    return detect_section(param_delimiter, raw_text, SectionType.PARAMETER_DELIMITER)


def detect_return_section(function: ast.FunctionDef, raw_text: list[str]) -> Optional[Section]:
    token_name = DELIMITERS[DocstringStyle.NUMPY]['returns']
    section = detect_section(token_name, raw_text, SectionType.RETURNS)
    if section is not None:
        section.annotation = parse_returns(function)
        return section


def detect_arg_section(item: ast.arg, raw_text: list[str]) -> Optional[Section]:
    token_name = item.arg
    section = detect_section(token_name, raw_text, SectionType.ARG)
    if section is not None:
        section.annotation = parse_annotation(item)
        return section


def parse_sections(function: ast.FunctionDef, raw_text: list[str]) -> list[Section]:
    """Split the docstring into multiple sections."""
    # TODO Auto detect docstring style
    sections = [detect_start_section(raw_text)]
    for item in function.args.args:
        section = detect_arg_section(item, raw_text)
        if section is not None:
            sections.append(section)

    section = detect_param_section(raw_text)
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

# @dataclass
# class DocstringSection:
#     """Base structure describing a docstring"""
#     summary: str
#     param_delimiter: str
#     parameters: str
#     return_delimiter: str
#     returns: str
#
#     def values(self) -> tuple[str, str, str, str, str]:
#         """Returns attributes as tuple"""
#         return self.summary, self.param_delimiter, self.parameters, self.return_delimiter, self.returns
#
#     @staticmethod
#     def keys() -> tuple[str, str, str, str, str]:
#         """Returns attributes as key"""
#         return 'summary', 'param_delimiter', 'parameters', 'return_delimiter', 'returns'
#
#     def to_string(self) -> str:
#         """Returns the docstring as string"""
#         return ''.join(self.values())
#
#     def to_dict(self):
#         """Returns the docstring as dictionary"""
#         return dict(zip(self.keys(), self.values()))
#
# def correct_lines(dirty_lines: list[str], start: int, length: int, corrected_docstring) -> list[str]:
#     """Apply corrected docstring in the raw_text read from the file."""
#     corrected_lines = dirty_lines.copy()
#     [corrected_lines.pop(start) for _ in range(length)]
#     [corrected_lines.insert(start, line) for line in corrected_docstring.splitlines()[::-1]]
#
#     return corrected_lines
#
#
# def annotate_args(func: ast.FunctionDef,
#                   raw_text: list[str],
#                   sections: DocstringSection,
#                   start: int,
#                   length: int) -> list[str]:
#     """Annotate annotations from a function definition"""
#     for item in func.args.args:
#         arg_name = item.arg
#         annotations = parse_annotation(item)
#
#         if annotations:
#             pattern = re.compile(f"{arg_name}.*:")
#             match = re.search(pattern, sections.parameters)
#
#             if match:
#                 corrected = f'{item.arg} ({annotations}):'
#                 sections.parameters = re.sub(match.group(), corrected, sections.parameters, 1)
#
#         corrected_docstring = sections.to_string()
#         raw_text = correct_lines(raw_text, start, length, corrected_docstring)
#     return raw_text
#
#
# def annotate_returns(func: ast.FunctionDef,
#                      raw_text: list[str],
#                      sections: DocstringSection,
#                      start: int,
#                      length: int) -> list[str]:
#     raise NotImplementedError
#
#
# def annotate_function(func: ast.FunctionDef, raw_text: list[str]) -> list[str]:
#     """Annotate function"""
#     start, length = get_docstring_lines(func, raw_text)
#     docstring = get_docstring_from_position(raw_text, start, length)
#     sections = get_docstring_sections(docstring)
#
#     if sections:
#         raw_text = annotate_args(func, raw_text, sections, start, length)
#
#     return raw_text
#
#
# def annotate_file(file_path: str):
#     file = Path(file_path)
#     raw_text = file.read_text()
#     dirty_lines = raw_text.splitlines()
#     parsed_file = ast.parse(raw_text)
#
#     classes = [item for item in parsed_file.body if isinstance(item, ast.ClassDef)]
#     class_methods = [func for item in classes for func in item.body if isinstance(func, ast.FunctionDef)]
#     functions = [item for item in parsed_file.body if isinstance(item, ast.FunctionDef)]
#     raise NotImplementedError
