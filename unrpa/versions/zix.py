import ast
import io
import itertools
import os
import re
import struct
from typing import BinaryIO, Tuple, Optional, Type

from unrpa.versions.errors import (
    VersionSpecificRequirementUnmetError,
    MissingPackageError,
)
from unrpa.versions.version import HeaderBasedVersion, Version
from unrpa.view import ArchiveView

loader_name = "loader.pyo"


def get_loader(archive: BinaryIO) -> str:
    path = os.path.join(os.path.dirname(archive.name), loader_name)
    try:
        import uncompyle6  # type: ignore
    except ImportError as e:
        raise MissingPackageError("uncompyle6") from e
    try:
        with io.StringIO() as decompiled:
            uncompyle6.decompile_file(path, outstream=decompiled)
            return decompiled.getvalue()
    except ImportError as e:
        raise LoaderRequiredError(path) from e


def find_key(loader: str) -> int:
    vc_match = re.search(r"verificationcode = _string.sha1\('(.*?)'\)", loader)
    if not vc_match:
        raise IncorrectLoaderError()
    else:
        return obfuscation_sha1(vc_match.group(1))


def find_offset(archive: BinaryIO) -> int:
    return obfuscation_offset(archive.readline().split()[-1])


class ZiX12A(HeaderBasedVersion):
    """A proprietary format with additional obfuscation."""

    name = "ZiX-12A"
    header = b"ZiX-12A"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        loader = get_loader(archive)
        key = find_key(loader)
        return find_offset(archive), key


class ZiX12B(HeaderBasedVersion):
    """A proprietary format with additional obfuscation."""

    name = "ZiX-12B"
    header = b"ZiX-12B"

    def __init__(self) -> None:
        self.details: Optional[Tuple[int, int]] = None

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        loader = get_loader(archive)
        key = find_key(loader)
        oa_match = re.search(
            r"_string.run\(rv.read\(([0-9]*?)\), verificationcode\)", loader
        )
        if not oa_match:
            raise IncorrectLoaderError()
        else:
            self.details = (key, ast.literal_eval(oa_match.group(1)))
        return find_offset(archive), key

    def postprocess(self, source: ArchiveView, sink: BinaryIO) -> None:
        if self.details:
            key, amount = self.details
            parts = []
            while amount > 0:
                part = source.read(amount)
                amount -= len(part)
                parts.append(part)
            sink.write(obfuscation_run(b"".join(parts), key))
        else:
            raise Exception("find_offset_and_key must be called before postprocess")
        for segment in iter(source.read1, b""):
            sink.write(segment)


versions: Tuple[Type[Version], ...] = (ZiX12A, ZiX12B)


class LoaderRequiredError(VersionSpecificRequirementUnmetError):
    """An error where the user needs to provide `loader.pyo` to extract this type of archive."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"To extract ZiX archives, the “{loader_name}” file is required alongside the archive (we looked for it at "
            f"“{path}”). You can find this file in the game you got the archive from, in the “renpy” directory.",
            f"Copy the “{loader_name}” file next to the archive you are trying to extract.",
        )


class IncorrectLoaderError(VersionSpecificRequirementUnmetError):
    def __init__(self) -> None:
        super().__init__(
            f"The provided “{loader_name}” file does not appear to be the correct one. Please check it is from the "
            "game this archive came from."
        )


# The following code is reverse engineered from the cython "_string.pyd" file courtesy of omegalink12.
# https://github.com/Lattyware/unrpa/issues/15#issuecomment-485014225
# They are somewhat misleadingly named.

magic_keys = (
    3621826839565189698,
    8167163782024462963,
    5643161164948769306,
    4940859562182903807,
    2672489546482320731,
    8917212212349173728,
    7093854916990953299,
)


def obfuscation_sha1(code: str) -> int:
    a = int("".join(filter(str.isdigit, code))) + 102464652121606009
    b = round(a ** (1 / 3)) / 23 * 109
    return int(b)


def obfuscation_offset(value: bytes) -> int:
    a = value[7:5:-1]
    b = value[:3]
    c = value[5:2:-1]
    return int(a + b + c, 16)


def obfuscation_run(s: bytes, key: int) -> bytes:
    count = len(s) // 8
    struct_format = f"<{'Q'*count}"
    encoded = struct.unpack(struct_format, s)
    decoded = (
        magic_key ^ key ^ part
        for (magic_key, part) in zip(itertools.cycle(magic_keys), encoded)
    )
    return struct.pack(struct_format, *decoded)
