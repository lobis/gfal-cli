"""Unit tests for gfal_cli.utils helper functions."""

import stat

from gfal_cli.utils import file_mode_str, file_type_str


class TestFileTypeStr:
    def test_regular_file(self):
        assert file_type_str(stat.S_IFREG) == "regular file"

    def test_directory(self):
        assert file_type_str(stat.S_IFDIR) == "directory"

    def test_symlink(self):
        assert file_type_str(stat.S_IFLNK) == "symbolic link"

    def test_block_device(self):
        assert file_type_str(stat.S_IFBLK) == "block device"

    def test_char_device(self):
        assert file_type_str(stat.S_IFCHR) == "character device"

    def test_fifo(self):
        assert file_type_str(stat.S_IFIFO) == "fifo"

    def test_socket(self):
        assert file_type_str(stat.S_IFSOCK) == "socket"

    def test_unknown(self):
        assert file_type_str(0) == "unknown"


class TestFileModeStr:
    def test_regular_644(self):
        assert file_mode_str(stat.S_IFREG | 0o644) == "-rw-r--r--"

    def test_regular_755(self):
        assert file_mode_str(stat.S_IFREG | 0o755) == "-rwxr-xr-x"

    def test_regular_600(self):
        assert file_mode_str(stat.S_IFREG | 0o600) == "-rw-------"

    def test_directory_755(self):
        assert file_mode_str(stat.S_IFDIR | 0o755) == "drwxr-xr-x"

    def test_directory_700(self):
        assert file_mode_str(stat.S_IFDIR | 0o700) == "drwx------"

    def test_regular_000(self):
        assert file_mode_str(stat.S_IFREG | 0o000) == "----------"

    def test_regular_777(self):
        assert file_mode_str(stat.S_IFREG | 0o777) == "-rwxrwxrwx"

    def test_prefix_block_device(self):
        assert file_mode_str(stat.S_IFBLK | 0o660).startswith("b")

    def test_prefix_char_device(self):
        assert file_mode_str(stat.S_IFCHR | 0o660).startswith("c")

    def test_prefix_fifo(self):
        assert file_mode_str(stat.S_IFIFO | 0o660).startswith("f")

    def test_prefix_socket(self):
        assert file_mode_str(stat.S_IFSOCK | 0o660).startswith("s")

    def test_length_always_ten(self):
        for mode in (0o644, 0o755, 0o700, 0o777, 0o000):
            assert len(file_mode_str(stat.S_IFREG | mode)) == 10
