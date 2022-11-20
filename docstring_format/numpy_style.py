"""Apply formatting of numpy style to docstring"""
import re
from typing import TYPE_CHECKING

from .utils import SectionType, is_empty_line, DOCSTRING_TAGS

if TYPE_CHECKING:
    from .base import DocstringSection


def sanitize(lines: list[str]):
    """Remove docstring tags and empty lines at the beggining and the end of the docstring."""

    def remove_tags(line, tag):
        """Remove docstring tags from the lines."""
        match = re.search(tag, line)
        if match:
            return ''.join(match.groups())
        return line

    def pop_empty_lines(lines_w_void: list[str], index):
        """Remove empty lines."""
        for _ in range(len(lines_w_void)):
            if is_empty_line(lines_w_void[index]):
                lines_w_void.pop(index)
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


def apply_numpy_style(section: 'DocstringSection') -> list[str]:
    """Main entry point to annotate function.

    It maps the section section_type to the correct annotation function. Sections are cleaned in-situ, result is
    saved in the cleaned_lines attributes."""
    lines = sanitize(section.lines)
    if section.type in NUMPY_ANNOTATE_MAP.keys():
        return NUMPY_ANNOTATE_MAP[section.type](section, lines)


def clean_summary_section(section: 'DocstringSection', lines: list[str]):
    """Adjust the summary section."""
    # remove consecutive blank lines
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [section.offset + line for line in text.splitlines()]
    return lines


def clean_parameter_section(section: 'DocstringSection', lines: list[str]):
    """Clean parameter section."""
    offset = section.offset
    lines = ['', offset + 'Parameters', offset + '----------']
    return lines


def clean_argument_section(section: 'DocstringSection', lines: list[str]):
    """Clean parameter section"""
    offset = section.offset
    # correct indentation
    annotated_argument = offset + f'{section.name} : {section.annotation}'

    if section.annotation:
        # one liner, param_name param_type param_description
        line = lines.pop(0)
        # check for description on the same line that the parameter name
        description = None
        pattern = re.compile(rf'{section.name}.*{section.annotation}[():\s_]*(.*)')
        match = re.search(pattern, line)
        if match:
            description = match.groups()[0]
        else:
            pattern = re.compile(rf'{section.name}[():\s_]*(.*)')
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

    return lines


def clean_return_section(section: 'DocstringSection', lines: list[str]):
    """Clean the return section."""
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
    lines = ['',
             offset + 'Returns',
             offset + '-------',
             *lines]

    return lines


NUMPY_ANNOTATE_MAP = {SectionType.SUMMARY: clean_summary_section,
                      SectionType.PARAMETER_DELIMITER: clean_parameter_section,
                      SectionType.ARG: clean_argument_section,
                      SectionType.RETURNS: clean_return_section}
