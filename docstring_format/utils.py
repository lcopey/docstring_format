from enum import Enum, auto
import re


class DocstringStyle(Enum):
    NUMPY = auto()
    RST = auto()
    GOOGLE = auto()


class SectionType(Enum):
    ARG = auto()
    SUMMARY = auto()
    RETURNS = auto()
    PARAMETER_DELIMITER = auto()


DELIMITERS = {DocstringStyle.NUMPY: {'param': 'Parameters', 'returns': 'Returns'}}


# PARAMETERS_DELIMITERS_REGEX = {DocstringStyle.NUMPY: 'Parameters\n\s*-+\n'}
# RETURNS_DELIMITERS_REGEX = {DocstringStyle.NUMPY: 'Returns\s*-+\n'}

def is_empty_line(line):
    match = re.search('^\s*$', line)  # match a line of whitespace
    return match


DOCSTRING_TAGS = {'first': '(\s*)["\']{3}(.*)',  # match `whitespaces"""description`
                  'last': '(\s*)(.*)["\']{3}',
                  'generic': '["\']{3}'}  # match `whitespaces description"""`
