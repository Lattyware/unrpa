from typing import BinaryIO, Tuple, Optional, Type

from unrpa.versions.version import ExtensionBasedVersion, HeaderBasedVersion, Version


class RPA1(ExtensionBasedVersion):
    """The first official version of the RPA format."""

    name = "RPA-1.0"
    extension = ".rpi"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        return 0, None


class RPA2(HeaderBasedVersion):
    """The second official version of the RPA format."""

    name = "RPA-2.0"
    header = b"RPA-2.0"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        offset = int(archive.readline()[8:], 16)
        return offset, None


class RPA3(HeaderBasedVersion):
    """The third official version of the RPA format."""

    name = "RPA-3.0"
    header = b"RPA-3.0"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        line = archive.readline()
        parts = line.split()
        offset = int(parts[1], 16)
        key = int(parts[2], 16)
        return offset, key


versions: Tuple[Type[Version], ...] = (RPA1, RPA2, RPA3)
