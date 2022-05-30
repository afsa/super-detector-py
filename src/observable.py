from enum import Enum
from typing import Sequence


class Observable(Enum):
    COMPLEX_FIELD = 'Complex field'
    PHASE = 'Phase'
    SUPERCURRENT = 'Supercurrent density'
    NORMAL_CURRENT = 'Normal current density'
    SCALAR_POTENTIAL = 'Scalar potential'
    VECTOR_POTENTIAL = 'Vector potential'
    ALPHA = 'Alpha'

    @classmethod
    def get_keys(cls) -> Sequence[str]:
        return list(item.name for item in Observable)

    @classmethod
    def from_key(cls, key: str) -> 'Observable':
        return Observable[key]
