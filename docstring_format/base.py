import ast
import re
from dataclasses import dataclass
from .annotations import parse_annotation
from .constants import DocstringStyle, DOCSTRING_DELIMITER


@dataclass
class DocstringSection:
    """Base structure describing a docstring"""
    summary: str
    delimiter: str
    parameters: str

    def values(self) -> tuple[str, str, str]:
        """Returns attributes as tuple"""
        return self.summary, self.delimiter, self.parameters

    @staticmethod
    def keys() -> tuple[str, str, str]:
        """Returns attributes as key"""
        return 'summary', 'delimiter', 'parameters'

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


def get_docstring_sections(docstring, style: DocstringStyle = DocstringStyle.NUMPY) -> DocstringSection:
    delimiter_token = DOCSTRING_DELIMITER[style]
    sections_regex = re.compile(f'(?P<summary>.*)(?P<delimiter>{delimiter_token})(?P<parameters>.*)', flags=re.S)
    result = re.search(sections_regex, docstring).groupdict()
    return DocstringSection(**result)


def annotate_function(func: ast.FunctionDef, dirty_lines: list[str]) -> str:
    start, length = get_docstring_lines(func, dirty_lines)
    docstring = '\n'.join(dirty_lines[start:start + length])

    sections = get_docstring_sections(docstring)

    for item in func.args.args:
        arg_name = item.arg
        annotation = parse_annotation(item)
        arg_regex = re.compile(f'(?P<arg>{arg_name}).*(?P<annotation>{annotation})?.*:?.*\n')

        match = re.search(arg_regex, sections.parameters)
        if match:
            match = match.groupdict()
            if match['arg'] is not None and match['annotation'] is None:
                sections.parameters = re.sub(f'{arg_name}.*:?', f'{item.arg} ({annotation}):', sections.parameters)

    corrected_docstring = sections.to_string()
    return corrected_docstring
