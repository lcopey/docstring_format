from enum import Enum, auto


class DocstringStyle(Enum):
    NUMPY = auto()
    RST = auto()
    GOOGLE = auto()


DOCSTRING_DELIMITER = {DocstringStyle.NUMPY: 'Parameters\n\s*-+\n'}
