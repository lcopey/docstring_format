from enum import Enum, auto


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
