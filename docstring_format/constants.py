from enum import Enum, auto


class DocstringStyle(Enum):
    NUMPY = auto()
    RST = auto()
    GOOGLE = auto()


PARAMETERS_DELIMITERS_REGEX = {DocstringStyle.NUMPY: 'Parameters\n\s*-+\n'}
RETURNS_DELIMITERS_REGEX = {DocstringStyle.NUMPY: 'Returns\s*-+\n'}
