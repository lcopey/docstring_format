import re
from typing import TYPE_CHECKING

from .constants import SectionType

if TYPE_CHECKING:
    from .base import Section


def clean_lines_section(lines: list[str]):
    # remove docstring tag at the first and last line
    lines = lines.copy()
    first_line = lines[0]
    match = re.search('\s*["\']{3}(.*)', first_line)
    if match:
        lines[0] = match.groups()[0]

    last_line = lines[-1]
    match = re.search('\s*(.*)["\']{3}', last_line)
    if match:
        lines[-1] = match.groups()[0]

    # remove trailing empty lines
    for _ in range(len(lines)):
        match = re.search('^\s*$', lines[0])
        if match:
            lines.pop(0)
        else:
            break

    for _ in range(len(lines)):
        match = re.search('^\s*$', lines[-1])
        if match:
            lines.pop(-1)
        else:
            break
    return lines


def annotate_section(section: 'Section'):
    section.corrected_lines = clean_lines_section(section.lines)
    if section.type in ANNOTATE_MAP.keys():
        return ANNOTATE_MAP[section.type](section)
    return section


def annotate_arg_section(section: 'Section'):
    lines = section.corrected_lines.copy() if section.corrected_lines is not None else section.lines.copy()
    pattern = re.compile(f'{section.name}\s*:\s*{section.annotation}')
    offset = section.offset
    # no annotation discovered
    if not any([re.search(pattern, line) for line in lines]):
        # Are description and variable on the same line
        line = lines.pop(0)
        match = re.search(f'\s*{section.name}\s*:\s*(.*)', line)
        if match:
            description = match.groups()[0]
            lines = [offset + f'{section.name} : {section.annotation}',
                     offset * 2 + description.capitalize()] + lines
        else:
            lines = [offset + f'{section.name} : {section.annotation}'] + lines
    section.corrected_lines = lines
    return section


def annotate_returns(section: 'Section'):
    lines = section.corrected_lines.copy() if section.corrected_lines is not None else section.lines.copy()
    offset = section.offset

    # remove first line delimiters
    for _ in range(len(lines)):
        line = lines[0]
        if (re.search('[Rr]eturns?', line) or
                re.search('-+', line)):
            lines.pop(0)

    # remove whitespaces and add twice the offset
    lines = [offset * 2 + re.search('\s(.*)', line).group() for line in lines]
    if section.annotation:
        pattern = re.compile(f'{section.annotation}')
        if not any([re.search(pattern, line) for line in lines]):
            lines.insert(0, offset + section.annotation)

    # add return delimiter
    lines = [offset + 'Returns', offset + '-------'] + lines

    section.corrected_lines = lines
    return section


ANNOTATE_MAP = {SectionType.ARG: annotate_arg_section,
                SectionType.RETURNS: annotate_returns}
