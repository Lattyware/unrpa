"""Decode the data-only subset of pickle used by RPA archive indexes."""

import pickletools
import zlib
from typing import Any, BinaryIO, Dict, List, Union

from unrpa.errors import InvalidArchiveIndexError


MAX_INDEX_BYTES = 64 * 1024 * 1024
MAX_INDEX_OPERATIONS = 8_000_000
MAX_INDEX_PARTS = 1_000_000

INTEGER_OPS = {"INT", "BININT", "BININT1", "BININT2", "LONG", "LONG1", "LONG4"}
STRING_OPS = {"UNICODE", "BINUNICODE", "SHORT_BINUNICODE", "BINUNICODE8"}
LEGACY_STRING_OPS = {"STRING", "BINSTRING", "SHORT_BINSTRING"}
BYTES_OPS = {"BINBYTES", "SHORT_BINBYTES", "BINBYTES8"}
EMPTY_CONTAINERS = {"EMPTY_DICT": dict, "EMPTY_LIST": list, "EMPTY_TUPLE": tuple}
TUPLE_SIZES = {"TUPLE1": 1, "TUPLE2": 2, "TUPLE3": 3}
LEGACY_GLOBALS = {"_codecs encode": object(), "__builtin__ bytes": object()}


def assign_items(mapping: Any, items: List[Any]) -> None:
    if type(mapping) is not dict or len(items) % 2:
        raise ValueError("Invalid dictionary")
    for i in range(0, len(items), 2):
        key = items[i]
        if type(key) not in (str, bytes):
            raise ValueError("Invalid dictionary key")
        mapping[key] = items[i + 1]


def decode_legacy_bytes(marker: object, args: Any) -> bytes:
    # Python 3 writes these reductions for bytes before protocol 3.
    if type(args) is tuple:
        if marker is LEGACY_GLOBALS["__builtin__ bytes"] and not args:
            return b""
        if marker is LEGACY_GLOBALS["_codecs encode"] and len(args) == 2:
            value, encoding = args
            if type(value) is str and type(encoding) is str and encoding == "latin1":
                return value.encode("latin1")
    raise ValueError("Invalid legacy byte string")


def decode_index(data: bytes) -> Any:
    # genops describes the stream. The operations below manipulate data directly
    # and never invoke a pickle unpickler or resolve an imported object.
    stack: List[Any] = []
    marks: List[int] = []
    memo: Dict[int, Any] = {}

    for count, (operation, argument, position) in enumerate(pickletools.genops(data), 1):
        if count > MAX_INDEX_OPERATIONS:
            raise InvalidArchiveIndexError("Index exceeds the operation limit.")
        name = operation.name
        floor = marks[-1] if marks else 0

        if name == "STOP":
            if len(stack) != 1 or marks or position != len(data) - 1:
                raise ValueError("Invalid end of index")
            return stack[0]
        if name == "PROTO" or name == "FRAME":
            continue
        if name == "MARK":
            marks.append(len(stack))
        elif name in INTEGER_OPS or name in STRING_OPS or name in BYTES_OPS:
            stack.append(argument)
        elif name in LEGACY_STRING_OPS and isinstance(argument, str):
            stack.append(argument.encode("latin1"))
        elif name in EMPTY_CONTAINERS:
            stack.append(EMPTY_CONTAINERS[name]())
        elif name == "MEMOIZE" and len(stack) > floor:
            memo[len(memo)] = stack[-1]
        elif name in {"PUT", "BINPUT", "LONG_BINPUT"} and isinstance(argument, int) and len(stack) > floor:
            memo[argument] = stack[-1]
        elif name in {"GET", "BINGET", "LONG_BINGET"} and isinstance(argument, int):
            stack.append(memo[argument])
        elif name in TUPLE_SIZES and len(stack) - floor >= TUPLE_SIZES[name]:
            start = len(stack) - TUPLE_SIZES[name]
            stack[start:] = [tuple(stack[start:])]
        elif name in {"DICT", "LIST", "TUPLE", "SETITEMS", "APPENDS"} and marks:
            start = marks.pop()
            items = stack[start:]
            del stack[start:]
            if name == "DICT":
                mapping: Dict[Union[str, bytes], Any] = {}
                assign_items(mapping, items)
                stack.append(mapping)
            elif name == "LIST":
                stack.append(items)
            elif name == "TUPLE":
                stack.append(tuple(items))
            elif start <= (marks[-1] if marks else 0):
                raise ValueError("Missing container")
            elif name == "SETITEMS":
                assign_items(stack[-1], items)
            elif type(stack[-1]) is list:
                stack[-1].extend(items)
            else:
                raise ValueError("Invalid list")
        elif name == "SETITEM" and len(stack) - floor >= 3:
            assign_items(stack[-3], stack[-2:])
            del stack[-2:]
        elif name == "APPEND" and len(stack) - floor >= 2 and type(stack[-2]) is list:
            item = stack.pop()
            stack[-1].append(item)
        elif name == "GLOBAL" and isinstance(argument, str) and argument in LEGACY_GLOBALS:
            stack.append(LEGACY_GLOBALS[argument])
        elif name == "REDUCE" and len(stack) - floor >= 2:
            stack[-2:] = [decode_legacy_bytes(stack[-2], stack[-1])]
        else:
            raise InvalidArchiveIndexError("Unsupported archive index operation.")
    raise ValueError("Missing end of index")


def read_index(archive: BinaryIO) -> Any:
    compressed = archive.read(MAX_INDEX_BYTES + 1)
    if len(compressed) > MAX_INDEX_BYTES:
        raise InvalidArchiveIndexError("Compressed index exceeds the size limit.")

    try:
        decompressor = zlib.decompressobj()
        data = decompressor.decompress(compressed, MAX_INDEX_BYTES + 1)
        if len(data) > MAX_INDEX_BYTES:
            raise InvalidArchiveIndexError("Decompressed index exceeds the size limit.")
        if not decompressor.eof:
            raise InvalidArchiveIndexError("Compressed index is incomplete.")
        index = decode_index(data)
    except (zlib.error, ValueError, KeyError, OverflowError) as error:
        raise InvalidArchiveIndexError("Invalid compressed archive index.") from error

    if type(index) is not dict:
        raise InvalidArchiveIndexError("Expected an index of filenames.")
    part_count = 0
    for name, entries in index.items():
        if type(name) not in (str, bytes) or type(entries) not in (list, tuple) or not entries:
            raise InvalidArchiveIndexError("Invalid filename or archive entry.")
        part_count += len(entries)
        if part_count > MAX_INDEX_PARTS:
            raise InvalidArchiveIndexError("Index contains too many archive entries.")
        for entry in entries:
            if (
                type(entry) is not tuple
                or len(entry) not in (2, 3)
                or any(type(value) is not int or not 0 <= value < 2**64 for value in entry[:2])
                or (len(entry) == 3 and type(entry[2]) is not bytes)
            ):
                raise InvalidArchiveIndexError("Invalid offset, length or prefix.")
    return index
