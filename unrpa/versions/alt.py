from typing import BinaryIO, Tuple, Optional, Type

from unrpa.versions.version import HeaderBasedVersion, Version


class ALT1(HeaderBasedVersion):
    """A short-lived alternative version of RPA-3.0 from mainline Ren'Py."""

    name = "ALT-1.0"
    header = b"ALT-1.0"
    extra_key = 0xDABE8DF0

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        line = archive.readline()
        parts = line.split()
        key = int(parts[1], 16) ^ ALT1.extra_key
        offset = int(parts[2], 16)
        return offset, key


versions: Tuple[Type[Version], ...] = (ALT1,)
