import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .annotation_parser import parse_annotation, parse_returns
from .annotations import clean_section
from .constants import DELIMITERS, DocstringStyle, SectionType


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

    def annotate(self):
        clean_section(self)


@dataclass
class Docstring:
    function: ast.FunctionDef
    lines: list[str]
    start: int
    length: int
    offset: str = field(init=False)
    sections: list[Section] = field(init=False)

    @classmethod
    def from_ast(cls, func: ast.FunctionDef, raw_text: list[str]):
        start, length = get_docstring_start_and_length(func, raw_text)
        # TODO change one for getter instead
        docstring_lines = raw_text[start:start + length]
        return cls(func, docstring_lines, start, length)

    def __post_init__(self):
        self.offset = re.search('(\s*)', self.lines[0]).group()
        self.sections = parse_sections(self.function, self.lines)

    def annotate(self):
        for section in self.sections:
            section.annotate()

    @property
    def corrected_lines(self):
        self.annotate()
        return [line for section in self.sections for line in section.corrected_lines]


def get_docstring_start_and_length(func: ast.FunctionDef, raw_text: list[str]) -> tuple[int, int]:
    """Get the start and the length of the docstring associated with function."""
    docstring = ast.get_docstring(func)
    tag_search = re.compile('["\']{3}')  # match """

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


def detect_section(token_name: str, raw_text: list[str], section_type: SectionType) -> Optional[Section]:
    pattern = re.compile(f'^(\s*)({token_name})')
    for n, line in enumerate(raw_text):
        match = re.search(pattern, line)
        if match:
            offset, _ = match.groups()
            section = Section(name=token_name,
                              start=n,
                              offset=offset,
                              type=section_type)
            return section


def detect_summary_section(raw_text: list[str]) -> Section:
    match = re.search(f'^(\s*)', raw_text[0])  # match whitespace
    offset = match.group() if match else None
    return Section(name='Summary', type=SectionType.SUMMARY, start=0, offset=offset)


def detect_param_delimiter_section(raw_text: list[str]):
    delimiter = DELIMITERS[DocstringStyle.NUMPY]['param']
    return detect_section(delimiter, raw_text, SectionType.PARAMETER_DELIMITER)


def detect_return_section(function: ast.FunctionDef, raw_text: list[str]) -> Optional[Section]:
    delimiter = DELIMITERS[DocstringStyle.NUMPY]['returns']
    section = detect_section(delimiter, raw_text, SectionType.RETURNS)
    if section is not None:
        section.annotation = parse_returns(function)
        return section


def detect_argument_section(item: ast.arg, raw_text: list[str]) -> Optional[Section]:
    token_name = item.arg
    section = detect_section(token_name, raw_text, SectionType.ARG)
    if section is not None:
        section.annotation = parse_annotation(item)
        return section


def parse_sections(function: ast.FunctionDef, raw_text: list[str]) -> list[Section]:
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
