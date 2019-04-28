import io
import os
import re
import struct
import itertools
from typing import BinaryIO, Tuple, Optional, FrozenSet, Type

from unrpa.versions.errors import (
    VersionSpecificRequirementUnmetError,
    MissingPackageError,
)
from unrpa.versions.version import HeaderBasedVersion, Version
from unrpa.view import ArchiveView


class ZiX12B(HeaderBasedVersion):
    """A proprietary format with additional obfuscation."""

    name = "ZiX-12B"
    header = b"ZiX-12B"

    magic_constant = 102464652121606009
    magic_keys = (
        3621826839565189698,
        8167163782024462963,
        5643161164948769306,
        4940859562182903807,
        2672489546482320731,
        8917212212349173728,
        7093854916990953299,
    )

    loader = "loader.pyo"

    struct_format = "<QQQQQQQQ"
    obfuscated_amount = struct.calcsize(struct_format)

    def __init__(self) -> None:
        self.key: Optional[int] = None

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        path = os.path.join(os.path.dirname(archive.name), ZiX12B.loader)
        try:
            import uncompyle6  # type: ignore
        except ImportError as e:
            raise MissingPackageError("uncompyle6") from e
        try:
            with io.StringIO() as decompiled:
                uncompyle6.decompile_file(path, outstream=decompiled)
                match = re.search(
                    r"verificationcode = _string.sha1\('(.*)'\)", decompiled.getvalue()
                )
                if match:
                    verification_code = match.group(1)
                else:
                    raise IncorrectLoaderError()
        except ImportError as e:
            raise LoaderRequiredError(path) from e
        parts = archive.readline().split()
        self.key = ZiX12B.sha1(verification_code)
        return ZiX12B.offset(parts[-1]), self.key

    def postprocess(self, source: ArchiveView, sink: BinaryIO) -> None:
        """Allows postprocessing over the data extracted from the archive."""
        if self.key:
            parts = []
            amount = ZiX12B.obfuscated_amount
            while amount > 0:
                part = source.read(amount)
                amount -= len(part)
                parts.append(part)
            sink.write(ZiX12B.run(b"".join(parts), self.key))
        else:
            raise Exception("find_offset_and_key must be called before postprocess")
        for segment in iter(source.read1, b""):
            sink.write(segment)

    # The following code is reverse engineered from the cython "_string.pyd" file courtesy of omegalink12.
    # https://github.com/Lattyware/unrpa/issues/15#issuecomment-485014225

    @staticmethod
    def sha1(code: str) -> int:
        a = int("".join(filter(str.isdigit, code))) + ZiX12B.magic_constant
        b = round(a ** (1 / 3)) / 23 * 109
        return int(b)

    @staticmethod
    def offset(value: bytes) -> int:
        a = value[7:5:-1]
        b = value[:3]
        c = value[5:2:-1]
        return int(a + b + c, 16)

    @staticmethod
    def run(s: bytes, key: int) -> bytes:
        encoded = struct.unpack(ZiX12B.struct_format, s)
        decoded = (
            magic_key ^ key ^ part
            for (magic_key, part) in zip(itertools.cycle(ZiX12B.magic_keys), encoded)
        )
        return struct.pack(ZiX12B.struct_format, *decoded)


versions: FrozenSet[Type[Version]] = frozenset({ZiX12B})


class LoaderRequiredError(VersionSpecificRequirementUnmetError):
    """An error where the user needs to provide `loader.pyo` to extract this type of archive."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"To extract {ZiX12B.name} archives, the “{ZiX12B.loader}” file is required alongside the archive (we "
            f"looked for it at “{path}”). You can find this file in the game you got the archive from, in the “renpy” "
            f"directory.",
            f"Copy the “{ZiX12B.loader}” file next to the archive you are trying to extract.",
        )


class IncorrectLoaderError(VersionSpecificRequirementUnmetError):
    def __init__(self) -> None:
        super().__init__(
            "The provided “{ZiX12B.loader}” file does not appear to be the correct one. Please check it is from the "
            "game this archive came from."
        )
