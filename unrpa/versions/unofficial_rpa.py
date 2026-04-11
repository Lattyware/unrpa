import re
from typing import BinaryIO, Tuple, Type, Optional

from unrpa.versions.version import HeaderBasedVersion, Version
from unrpa.versions.official_rpa import RPA3


class RPA32(RPA3):
    """A slightly custom variant of RPA-3.0."""

    name = "RPA-3.2"
    header = b"RPA-3.2"

class RPA40(RPA3):
    """A slightly custom variant of RPA-3.0."""

    name = "RPA-4.0"
    header = b"RPA-4.0"

class JAS16(HeaderBasedVersion):
    """Unofficial JAS+1.6 archive used by some Ren'Py builds."""
    name = "JAS+1.6"
    header = b"JAS+1.6"
    extension = ".jas"

    # Examples:
    # JAS+1.6 0000000001dbd9d3XXX8e9e5e20XXXXX
    # JAS+1.6 0000000066a56c68XXX8e9e5e20XXXXX
    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        line = archive.readline().decode(errors='ignore')[len("JAS+1.6"):].lstrip()

        # find contiguous hex runs; the first one is the table offset
        hex_runs = re.findall(r'[0-9A-Fa-f]+', line)

        if not hex_runs:
            return 0, None
        offset = int(hex_runs[0], 16)
        # optional: if a second hex run exists and seems small, treat as key
        key = int(hex_runs[1], 16) if len(hex_runs) > 1 and len(hex_runs[1]) <= 8 else None
        return offset, key

versions: Tuple[Type[Version], ...] = (RPA32, RPA40, JAS16)
