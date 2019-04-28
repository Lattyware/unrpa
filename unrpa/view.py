import io
from typing import cast, Callable, BinaryIO


class ArchiveView:
    """A file-like object that just passes through to the underlying file."""

    def __init__(self, archive: BinaryIO, offset: int, length: int, prefix: bytes):
        archive.seek(offset)
        self.name = archive.name
        self.remaining = length
        self.sources = [cast(io.BufferedIOBase, archive)]
        if prefix:
            self.sources.insert(0, cast(io.BufferedIOBase, io.BytesIO(prefix)))

    def read(self, amount: int = -1) -> bytes:
        return self.base_read(lambda source: source.read, amount)

    def read1(self, amount: int = -1) -> bytes:
        return self.base_read(lambda source: source.read1, amount)

    def base_read(
        self, method: Callable[[io.BufferedIOBase], Callable[[int], bytes]], amount: int
    ) -> bytes:
        if amount < 0 or amount > self.remaining:
            amount = self.remaining
        if self.sources and self.remaining > 0:
            segment = method(self.sources[0])(amount)
            if segment:
                self.remaining -= len(segment)
                return segment
            else:
                self.sources.pop(0)
                return self.base_read(method, amount)
        else:
            if self.remaining != 0:
                raise Exception("End of archive reached before the file should end.")
            return b""
