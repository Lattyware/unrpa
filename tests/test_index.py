import contextlib
import io
import pickle
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

from unrpa import UnRPA
from unrpa.errors import InvalidArchiveIndexError
from unrpa.index import read_index
from unrpa.versions.official_rpa import RPA3


class ArchiveIndexTests(unittest.TestCase):
    def read(self, payload):
        return read_index(io.BytesIO(zlib.compress(payload)))

    def test_data_types_across_pickle_protocols(self):
        index = {b"one.txt": [(16, 8, b"\xff")], "two.txt": [(24, 0, b"")]}
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.subTest(protocol=protocol):
                self.assertEqual(self.read(pickle.dumps(index, protocol)), index)

    def test_python2_style_byte_string_index(self):
        payload = b"\x80\x02}U\x01\xff]K\x01K\x02U\x01\xfe\x87as."
        self.assertEqual(self.read(payload), {b"\xff": [(1, 2, b"\xfe")]})

    def test_unrecognized_global(self):
        with self.assertRaises(InvalidArchiveIndexError):
            self.read(b"cexample\nplaceholder\n.")

    def test_invalid_or_trailing_index(self):
        for payload in (b"", b"}..", pickle.dumps({"name": [(0, -1)]})):
            with self.subTest(payload=payload), self.assertRaises(InvalidArchiveIndexError):
                self.read(payload)

    def test_compressed_and_expanded_limits(self):
        with mock.patch("unrpa.index.MAX_INDEX_BYTES", 100):
            for payload in (b"z" * 101, zlib.compress(b"z" * 101)):
                with self.subTest(payload=payload), self.assertRaises(InvalidArchiveIndexError):
                    read_index(io.BytesIO(payload))

    def test_shared_index_for_list_and_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / "sample.rpa"
            content = b"test content"
            key = 0x42424242
            header_size = len(b"RPA-3.0 0000000000000000 00000000\n")
            header = f"RPA-3.0 {header_size + len(content):016x} {key:08x}\n"
            index = {"folder/member.txt": [(header_size ^ key, len(content) ^ key)]}
            archive.write_bytes(header.encode() + content + zlib.compress(pickle.dumps(index)))

            extractor = UnRPA(str(archive), path=str(root))
            with contextlib.redirect_stdout(io.StringIO()) as output:
                extractor.list_files()
            self.assertEqual(output.getvalue().strip().replace("\\", "/"), "folder/member.txt")
            extractor.extract_files()
            self.assertEqual((root / "folder" / "member.txt").read_bytes(), content)

            archive.write_bytes(header.encode() + content + zlib.compress(b"cexample\nplaceholder\n."))
            for version in (None, RPA3):
                extractor = UnRPA(str(archive), path=str(root), version=version)
                for operation in (extractor.list_files, extractor.tree, extractor.extract_files):
                    with self.subTest(version=version, operation=operation):
                        with self.assertRaises(InvalidArchiveIndexError):
                            operation()
