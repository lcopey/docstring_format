import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .annotations import parse_annotation
from .constants import PARAMETERS_DELIMITERS_REGEX, RETURNS_DELIMITERS_REGEX, DocstringStyle


@dataclass
class DocstringSection:
    """Base structure describing a docstring"""
    summary: str
    param_delimiter: str
    parameters: str
    return_delimiter: str
    returns: str

    def values(self) -> tuple[str, str, str, str, str]:
        """Returns attributes as tuple"""
        return self.summary, self.param_delimiter, self.parameters, self.return_delimiter, self.returns

    @staticmethod
    def keys() -> tuple[str, str, str, str, str]:
        """Returns attributes as key"""
        return 'summary', 'param_delimiter', 'parameters', 'return_delimiter', 'returns'

    def to_string(self) -> str:
        """Returns the docstring as string"""
        return ''.join(self.values())

    def to_dict(self):
        """Returns the docstring as dictionary"""
        return dict(zip(self.keys(), self.values()))


def get_docstring_lines(func: ast.FunctionDef, lines: list[str]) -> tuple[int, int]:
    """Get the start and the length of the docstring associated with func."""
    docstring = ast.get_docstring(func)
    tag_search = re.compile('["\']{3}')

    start = func.lineno - 1
    match = re.search(tag_search, lines[start])
    while not match:
        start += 1
        match = re.search(tag_search, lines[start])

    tag = match.group()
    length = len(docstring.splitlines())
    match = re.search(tag, lines[start + length - 1])
    while not match:
        length += 1
        match = re.search(tag, lines[start + length - 1])

    return start, length


def get_docstring(func: ast.FunctionDef, lines: list[str]) -> str:
    """Get docstring from function and lines read from the file."""
    start, length = get_docstring_lines(func, lines)
    docstring = get_docstring_from_position(lines, start, length)
    return docstring


def get_docstring_from_position(lines: list[str], start: int, length: int) -> str:
    """Get the docstring as string from the list of lines read in the file."""
    return '\n'.join(lines[start:start + length])


def get_docstring_sections(docstring, style: DocstringStyle = DocstringStyle.NUMPY) -> Optional[DocstringSection]:
    """Parse the docstring to get sections.

    Sections are defined as :
     - summary (everything until the parameters definition).
     - a parameter param_delimiter (depending of the writing style of the docstring)
     - the parameters"""
    param_token = PARAMETERS_DELIMITERS_REGEX[style]
    return_token = RETURNS_DELIMITERS_REGEX[style]
    pattern = re.compile('(?P<summary_text>.*)'
                         f'(?P<param_delimiter>{param_token})'
                         f'(?P<parameters_text>((?!{return_token}).)*)'  # negative lookahead of return token
                         f'(?P<return_delimiter>{return_token})?'
                         f'(?P<returns_text>.*)?',
                         flags=re.S)
    match = re.search(pattern, docstring)
    if match:
        return DocstringSection(**match.groupdict())


def correct_lines(dirty_lines: list[str], start: int, length: int, corrected_docstring) -> list[str]:
    """Apply corrected docstring in the lines read from the file."""
    corrected_lines = dirty_lines.copy()
    [corrected_lines.pop(start) for _ in range(length)]
    [corrected_lines.insert(start, line) for line in corrected_docstring.splitlines()[::-1]]

    return corrected_lines


def annotate_args(func: ast.FunctionDef,
                  lines: list[str],
                  sections: DocstringSection,
                  start: int,
                  length: int) -> list[str]:
    """Annotate arguments from a function definition"""
    for item in func.args.args:
        arg_name = item.arg
        annotation = parse_annotation(item)

        if annotation:
            pattern = re.compile(f"{arg_name}.*:")
            match = re.search(pattern, sections.parameters)

            if match:
                corrected = f'{item.arg} ({annotation}):'
                sections.parameters = re.sub(match.group(), corrected, sections.parameters, 1)

        corrected_docstring = sections.to_string()
        lines = correct_lines(lines, start, length, corrected_docstring)
    return lines


def annotate_returns(func: ast.FunctionDef,
                     lines: list[str],
                     sections: DocstringSection,
                     start: int,
                     length: int) -> list[str]:
    raise NotImplementedError


def annotate_function(func: ast.FunctionDef, lines: list[str]) -> list[str]:
    """Annotate function"""
    start, length = get_docstring_lines(func, lines)
    docstring = get_docstring_from_position(lines, start, length)
    sections = get_docstring_sections(docstring)

    if sections:
        lines = annotate_args(func, lines, sections, start, length)

    return lines


def annotate_file(file_path: str):
    file = Path(file_path)
    raw_text = file.read_text()
    dirty_lines = raw_text.splitlines()
    parsed_file = ast.parse(raw_text)

    classes = [item for item in parsed_file.body if isinstance(item, ast.ClassDef)]
    class_methods = [func for item in classes for func in item.body if isinstance(func, ast.FunctionDef)]
    functions = [item for item in parsed_file.body if isinstance(item, ast.FunctionDef)]
    raise NotImplementedError
