import os
import pickle
import tempfile
import unittest
import zlib
from pathlib import Path

from unrpa import UnRPA
from unrpa.errors import ErrorExtractingFile


class ExtractionPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "output"
        self.output.mkdir()
        self.archive = self.root / "test.rpa"

    def write_archive(self, names):
        header_size = len(b"RPA-2.0 0000000000000000\n")
        contents = b"archive contents"
        index = {name: [(header_size, len(contents))] for name in names}
        header = b"RPA-2.0 %016x\n" % (header_size + len(contents))
        self.archive.write_bytes(
            header + contents + zlib.compress(pickle.dumps(index, protocol=2))
        )

    def extract(self, **options):
        UnRPA(str(self.archive), path=str(self.output), **options).extract_files()

    def assert_rejected(self, name, outside):
        outside.parent.mkdir(parents=True, exist_ok=True)
        outside.write_bytes(b"original contents")
        self.write_archive([name])
        with self.assertRaises(ErrorExtractingFile):
            self.extract()
        self.assertEqual(outside.read_bytes(), b"original contents")

    def test_extracts_relative_paths(self):
        self.write_archive(["plain.txt", "nested/file.txt", b"bytes.txt"])
        self.extract()
        for name in ["plain.txt", "nested/file.txt", "bytes.txt"]:
            self.assertEqual((self.output / name).read_bytes(), b"archive contents")

    def test_rejects_parent_traversal(self):
        self.assert_rejected("../outside.txt", self.root / "outside.txt")

    def test_rejects_absolute_paths(self):
        outside = self.root / "outside.txt"
        self.assert_rejected(str(outside), outside)

    def test_rejects_sibling_with_shared_prefix(self):
        outside = self.root / "output-other" / "outside.txt"
        self.assert_rejected("../output-other/outside.txt", outside)

    def test_does_not_create_outside_directories(self):
        self.write_archive(["../outside/nested/file.txt"])
        with self.assertRaises(ErrorExtractingFile):
            self.extract()
        self.assertFalse((self.root / "outside").exists())

    def symlink(self, link, target, directory=False):
        try:
            os.symlink(str(target), str(link), target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlinks unavailable: {}".format(error))

    def test_rejects_directory_symlink_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.symlink(self.output / "link", outside, directory=True)
        self.assert_rejected("link/file.txt", outside / "file.txt")

    def test_rejects_file_symlink_escape(self):
        outside = self.root / "outside.txt"
        self.symlink(self.output / "link.txt", outside)
        self.assert_rejected("link.txt", outside)

    def test_rejects_dangling_file_symlink_escape(self):
        outside = self.root / "outside.txt"
        self.symlink(self.output / "link.txt", outside)
        self.write_archive(["link.txt"])
        with self.assertRaises(ErrorExtractingFile):
            self.extract()
        self.assertFalse(outside.exists())

    def test_allows_directory_symlink_within_output(self):
        target = self.output / "nested"
        target.mkdir()
        self.symlink(self.output / "link", target, directory=True)
        self.write_archive(["link/file.txt"])
        self.extract()
        self.assertEqual((target / "file.txt").read_bytes(), b"archive contents")

    def test_allows_output_directory_symlink(self):
        target = self.output
        self.output = self.root / "output-link"
        self.symlink(self.output, target, directory=True)
        self.write_archive(["nested/file.txt"])
        self.extract()
        self.assertEqual((target / "nested/file.txt").read_bytes(), b"archive contents")

    def test_continue_on_error_skips_unsafe_member(self):
        self.write_archive(["../outside.txt", "nested/file.txt"])
        self.extract(continue_on_error=True)
        self.assertFalse((self.root / "outside.txt").exists())
        self.assertEqual(
            (self.output / "nested/file.txt").read_bytes(), b"archive contents"
        )


if __name__ == "__main__":
    unittest.main()
