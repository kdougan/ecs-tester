from enum import Enum
import functools
char_widths = {
    '0': 3,
    '1': 2,
    '2': 3,
    '3': 3,
    '4': 3,
    '5': 3,
    '6': 3,
    '7': 3,
    '8': 3,
    '9': 3,
    'A': 3,
    'B': 3,
    'C': 3,
    'D': 3,
    'E': 3,
    'F': 3,
    'G': 4,
    'H': 3,
    'I': 3,
    'J': 3,
    'K': 3,
    'L': 3,
    'M': 5,
    'N': 4,
    'O': 4,
    'P': 3,
    'Q': 4,
    'R': 3,
    'S': 3,
    'T': 3,
    'U': 3,
    'V': 3,
    'W': 5,
    'X': 3,
    'Y': 3,
    'Z': 3,
    'a': 3,
    'b': 3,
    'c': 3,
    'd': 3,
    'e': 3,
    'f': 3,
    'g': 3,
    'h': 3,
    'i': 2,
    'j': 3,
    'k': 3,
    'l': 2,
    'm': 5,
    'n': 3,
    'o': 3,
    'p': 3,
    'q': 3,
    'r': 3,
    's': 3,
    't': 3,
    'u': 3,
    'v': 3,
    'w': 5,
    'x': 3,
    'y': 3,
    'z': 3,
    '.': 1,
    ',': 1,
    '_': 3,
    '<': 2,
    '>': 2,
    '=': 2,
    '/': 3,
    '\\': 3,
    ':': 1,
    ';': 1,
    '+': 3,
    '-': 3,
}


@functools.total_ordering
class OrderedEnum(Enum):
    @classmethod
    @functools.lru_cache(None)
    def _member_list(cls):
        return list(cls)

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            member_list = self.__class__._member_list()
            return member_list.index(self) < member_list.index(other)
        return NotImplemented


@functools.total_ordering
class ValueOrderedEnum(Enum):
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
