"""Apply formatting of numpy style to docstring"""
import re
from typing import TYPE_CHECKING

from .utils import SectionType, is_empty_line, DOCSTRING_TAGS

if TYPE_CHECKING:
    from .base import DocstringSection


def sanitize(lines: list[str]):
    """Remove docstring tags and empty lines at the beggining and the end of the docstring."""

    def remove_tags(line, tag):
        match = re.search(tag, line)
        if match:
            return ''.join(match.groups())
        return line

    def pop_empty_lines(lines, index):
        for _ in range(len(lines)):
            if is_empty_line(lines[index]):
                lines.pop(index)
            else:
                break

    # remove docstring tag at the first and last line
    lines = [line.strip() for line in lines]
    lines[0] = remove_tags(lines[0], DOCSTRING_TAGS['first'])
    lines[-1] = remove_tags(lines[-1], DOCSTRING_TAGS['last'])

    # remove trailing empty lines
    pop_empty_lines(lines, 0)
    pop_empty_lines(lines, -1)
    return lines


def apply_numpy_style(section: 'DocstringSection'):
    """Main entry point to annotate function.

    It maps the section section_type to the correct annotation function. Sections are cleaned in-situ, result is
    saved in the cleaned_lines attributes."""
    section.cleaned_lines = sanitize(section.lines)
    if section.type in NUMPY_ANNOTATE_MAP.keys():
        return NUMPY_ANNOTATE_MAP[section.type](section)


def clean_summary_section(section: 'DocstringSection'):
    """Adjust the summary section."""
    # remove consecutive blank lines
    text = '\n'.join(section.cleaned_lines)
    text = re.sub('\n{3,}', '\n\n', text)
    lines = [section.offset + line for line in text.splitlines()]
    section.cleaned_lines = lines


def clean_parameter_section(section: 'DocstringSection'):
    """Clean parameter section."""
    offset = section.offset
    lines = ['', offset + 'Parameters', offset + '----------']
    section.cleaned_lines = lines


def clean_argument_section(section: 'DocstringSection'):
    """Clean parameter section"""
    offset = section.offset
    # correct indentation
    lines = section.cleaned_lines
    annotated_argument = offset + f'{section.name} : {section.annotation}'

    if section.annotation:
        # one liner, param_name param_type param_description
        line = lines.pop(0)
        # check for description on the same line that the parameter name
        description = None
        pattern = re.compile(f'{section.name}.*{section.annotation}[():\s_]*(.*)')
        match = re.search(pattern, line)
        if match:
            description = match.groups()[0]
        else:
            pattern = re.compile(f'{section.name}[():\s_]*(.*)')
            match = re.search(pattern, line)
            if match:
                description = match.groups()[0]

        # correct indentation
        lines = [offset * 2 + line for line in lines]
        if description:
            lines = [annotated_argument, offset * 2 + description.capitalize(), *lines]
        else:
            lines = [annotated_argument, *lines]
    else:
        lines = [offset * min(2, n + 1) + line for n, line in enumerate(lines)]

    section.cleaned_lines = lines


def clean_return_section(section: 'DocstringSection'):
    """Clean the return section."""
    lines = section.cleaned_lines
    offset = section.offset

    # remove first line delimiters
    for _ in range(len(lines)):
        line = lines[0]
        if (re.search('[Rr]eturns?', line) or
                re.search('-+', line) or
                is_empty_line(line)):
            lines.pop(0)

    # remove whitespaces and add twice the offset
    lines = [offset * 2 + line.strip() for line in lines]
    if section.annotation:
        pattern = re.compile(f'{section.annotation}')
        if not any([re.search(pattern, line) for line in lines]):
            lines.insert(0, offset + section.annotation)

    # add return delimiter
    lines = ['', offset + 'Returns', offset + '-------',
             *lines]

    section.cleaned_lines = lines


NUMPY_ANNOTATE_MAP = {SectionType.SUMMARY: clean_summary_section,
                      SectionType.PARAMETER_DELIMITER: clean_parameter_section,
                      SectionType.ARG: clean_argument_section,
                      SectionType.RETURNS: clean_return_section}
