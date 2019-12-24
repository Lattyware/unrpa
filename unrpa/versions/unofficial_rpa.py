from typing import Tuple, Type

from unrpa.versions.version import Version
from unrpa.versions.official_rpa import RPA3


class RPA32(RPA3):
    """A slightly custom variant of RPA-3.0."""

    name = "RPA-3.2"
    header = b"RPA-3.2"

class RPA40(RPA3):
    """A slightly custom variant of RPA-3.0."""

    name = "RPA-4.0"
    header = b"RPA-4.0"


versions: Tuple[Type[Version], ...] = (RPA32, RPA40,)
