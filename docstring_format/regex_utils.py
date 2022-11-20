import re


def is_empty_line(line):
    match = re.search('^\s*$', line)  # match a line of whitespace
    return match


DOCSTRING_TAGS = {'first': '(\s*)["\']{3}(.*)',  # match `whitespaces"""description`
                  'last': '(\s*)(.*)["\']{3}'}  # match `whitespaces description"""`
