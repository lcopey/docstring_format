import re
from typing import TYPE_CHECKING

from .constants import SectionType
from .regex_utils import is_empty_line, DOCSTRING_TAGS

if TYPE_CHECKING:
    from .base import Section


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


def clean_section(section: 'Section'):
    """Main entry point to annotate function.

    It maps the section section_type to the correct annotation function. Sections are cleaned in-situ, result is
    saved in the corrected_lines attributes."""
    section.corrected_lines = sanitize(section.lines)
    if section.type in ANNOTATE_MAP.keys():
        return ANNOTATE_MAP[section.type](section)


def clean_summary_section(section: 'Section'):
    """Adjust the summary section by adding the docstring tag."""
    lines = [section.offset + line for line in section.corrected_lines]
    lines.insert(0, section.offset + '"""')
    lines.append('')
    section.corrected_lines = lines


def clean_parameter_section(section: 'Section'):
    offset = section.offset
    lines = [offset + 'Parameters', offset + '----------']
    section.corrected_lines = lines


def clean_argument_section(section: 'Section'):
    """Clean parameter section"""
    offset = section.offset
    # correct indentation
    lines = [offset + line for line in section.corrected_lines]
    if section.annotation:
        # no annotation discovered
        pattern = re.compile(f'{section.name}\s*:\s*{section.annotation}')  # match `arg_name : type`
        if not any([re.search(pattern, line) for line in lines]):
            # Are description and variable on the same line
            line = lines.pop(0)
            match = re.search(f'{section.name}\s*:\s*(.*)', line)  # match `arg_name : description`
            if match:
                description = match.groups()[0]
                lines = [offset + f'{section.name} : {section.annotation}',
                         offset * 2 + description.capitalize(),
                         *lines]
            else:
                lines = [offset + f'{section.name} : {section.annotation}', *lines]
    section.corrected_lines = lines


def clean_return_section(section: 'Section'):
    """Clean the return section."""
    lines = section.corrected_lines
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
             *lines,
             '', offset + '"""']

    section.corrected_lines = lines


ANNOTATE_MAP = {SectionType.SUMMARY: clean_summary_section,
                SectionType.PARAMETER_DELIMITER: clean_parameter_section,
                SectionType.ARG: clean_argument_section,
                SectionType.RETURNS: clean_return_section}
