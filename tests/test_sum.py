"""Tests for gfal-sum (file checksum)."""

import hashlib
import zlib

import pytest

from helpers import run_gfal

DATA = b"hello world"


@pytest.fixture
def test_file(tmp_path):
    f = tmp_path / "test.bin"
    f.write_bytes(DATA)
    return f


# ---------------------------------------------------------------------------
# Supported algorithms
# ---------------------------------------------------------------------------


class TestSumAlgorithms:
    def test_adler32(self, test_file):
        expected = f"{zlib.adler32(DATA) & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal("sum", test_file.as_uri(), "ADLER32")

        assert rc == 0
        assert expected in out

    def test_crc32(self, test_file):
        expected = f"{zlib.crc32(DATA) & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal("sum", test_file.as_uri(), "CRC32")

        assert rc == 0
        assert expected in out

    def test_md5(self, test_file):
        expected = hashlib.md5(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "MD5")

        assert rc == 0
        assert expected in out

    def test_sha1(self, test_file):
        expected = hashlib.sha1(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "SHA1")

        assert rc == 0
        assert expected in out

    def test_sha256(self, test_file):
        expected = hashlib.sha256(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "SHA256")

        assert rc == 0
        assert expected in out

    def test_sha512(self, test_file):
        expected = hashlib.sha512(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "SHA512")

        assert rc == 0
        assert expected in out


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------


class TestSumOutput:
    def test_output_includes_uri(self, test_file):
        rc, out, err = run_gfal("sum", test_file.as_uri(), "ADLER32")

        assert rc == 0
        assert str(test_file.as_uri()) in out

    def test_output_single_line(self, test_file):
        rc, out, err = run_gfal("sum", test_file.as_uri(), "MD5")

        assert rc == 0
        lines = [ln for ln in out.strip().splitlines() if ln.strip()]
        assert len(lines) == 1

    def test_output_format_uri_space_checksum(self, test_file):
        """Output should be 'URI CHECKSUM\\n'."""
        expected = hashlib.md5(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "MD5")

        assert rc == 0
        parts = out.strip().split()
        assert len(parts) == 2
        assert parts[1] == expected


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------


class TestSumCaseInsensitive:
    def test_lowercase_algorithm(self, test_file):
        expected = f"{zlib.adler32(DATA) & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal("sum", test_file.as_uri(), "adler32")

        assert rc == 0
        assert expected in out

    def test_mixed_case(self, test_file):
        expected = hashlib.md5(DATA).hexdigest()

        rc, out, err = run_gfal("sum", test_file.as_uri(), "Md5")

        assert rc == 0
        assert expected in out


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestSumEdgeCases:
    def test_unknown_algorithm(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_bytes(DATA)

        rc, out, err = run_gfal("sum", f.as_uri(), "NOTANALGORITHM")

        assert rc != 0

    def test_nonexistent_file(self, tmp_path):
        rc, out, err = run_gfal("sum", (tmp_path / "no_such.txt").as_uri(), "MD5")

        assert rc != 0

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        expected = f"{zlib.adler32(b'') & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal("sum", f.as_uri(), "ADLER32")

        assert rc == 0
        assert expected in out

    def test_empty_file_md5(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        expected = hashlib.md5(b"").hexdigest()

        rc, out, err = run_gfal("sum", f.as_uri(), "MD5")

        assert rc == 0
        assert expected in out


# ---------------------------------------------------------------------------
# Large files
# ---------------------------------------------------------------------------


class TestSumLargeFile:
    def test_large_file_md5(self, tmp_path):
        """Checksum of a file spanning multiple read chunks (> 4 MiB)."""
        data = b"X" * (5 * 1024 * 1024)
        f = tmp_path / "large.bin"
        f.write_bytes(data)
        expected = hashlib.md5(data).hexdigest()

        rc, out, err = run_gfal("sum", f.as_uri(), "MD5")

        assert rc == 0
        assert expected in out

    def test_large_file_adler32(self, tmp_path):
        data = b"Y" * (5 * 1024 * 1024)
        f = tmp_path / "large.bin"
        f.write_bytes(data)
        expected = f"{zlib.adler32(data) & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal("sum", f.as_uri(), "ADLER32")

        assert rc == 0
        assert expected in out


# ---------------------------------------------------------------------------
# Known checksum values
# ---------------------------------------------------------------------------


class TestSumKnownValues:
    """Verify against well-known test vectors."""

    def test_md5_empty(self, tmp_path):
        f = tmp_path / "empty"
        f.write_bytes(b"")
        rc, out, err = run_gfal("sum", f.as_uri(), "MD5")
        assert "d41d8cd98f00b204e9800998ecf8427e" in out

    def test_md5_hello_world(self, tmp_path):
        f = tmp_path / "hw"
        f.write_bytes(b"hello world")
        rc, out, err = run_gfal("sum", f.as_uri(), "MD5")
        assert "5eb63bbbe01eeed093cb22bb8f5acdc3" in out

    def test_adler32_empty(self, tmp_path):
        f = tmp_path / "empty"
        f.write_bytes(b"")
        rc, out, err = run_gfal("sum", f.as_uri(), "ADLER32")
        assert "00000001" in out

    def test_crc32_empty(self, tmp_path):
        f = tmp_path / "empty"
        f.write_bytes(b"")
        rc, out, err = run_gfal("sum", f.as_uri(), "CRC32")
        assert "00000000" in out


# ---------------------------------------------------------------------------
# CRC32C
# ---------------------------------------------------------------------------


class TestSumCrc32c:
    def test_crc32c_empty(self, tmp_path):
        """CRC32C of empty file is 0x00000000."""
        f = tmp_path / "empty"
        f.write_bytes(b"")
        rc, out, err = run_gfal("sum", f.as_uri(), "CRC32C")
        assert rc == 0
        assert "00000000" in out

    def test_crc32c_known_value(self, tmp_path):
        """CRC32C of b'123456789' is 0xE3069283."""
        data = b"123456789"
        f = tmp_path / "data.bin"
        f.write_bytes(data)
        rc, out, err = run_gfal("sum", f.as_uri(), "CRC32C")
        assert rc == 0
        assert "e3069283" in out.lower()

    def test_crc32c_hello_world(self, tmp_path):
        """CRC32C of b'hello world' is 0xC99465AA."""
        data = b"hello world"
        f = tmp_path / "hw.bin"
        f.write_bytes(data)
        rc, out, err = run_gfal("sum", f.as_uri(), "CRC32C")
        assert rc == 0
        assert "c99465aa" in out.lower()

    def test_crc32c_lowercase_alias(self, tmp_path):
        data = b"test"
        f = tmp_path / "t.bin"
        f.write_bytes(data)
        rc, out, err = run_gfal("sum", f.as_uri(), "crc32c")
        assert rc == 0
        assert len(out.strip().split()) == 2

    def test_crc32c_output_format(self, tmp_path):
        f = tmp_path / "f.bin"
        f.write_bytes(b"abc")
        rc, out, err = run_gfal("sum", f.as_uri(), "CRC32C")
        assert rc == 0
        parts = out.strip().split()
        assert len(parts) == 2
        # Checksum should be 8 hex chars
        assert len(parts[1]) == 8


# ---------------------------------------------------------------------------
# Multiple files
# ---------------------------------------------------------------------------


class TestSumMultipleFiles:
    def test_two_files_separate_calls(self, tmp_path):
        """gfal-sum takes one file per invocation; verify both produce correct output."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"hello")
        f2.write_bytes(b"world")

        rc1, out1, _ = run_gfal("sum", f1.as_uri(), "MD5")
        rc2, out2, _ = run_gfal("sum", f2.as_uri(), "MD5")

        assert rc1 == 0
        assert rc2 == 0
        assert hashlib.md5(b"hello").hexdigest() in out1
        assert hashlib.md5(b"world").hexdigest() in out2

    def test_each_file_one_line(self, tmp_path):
        """Each separate gfal-sum call produces exactly one output line."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"x")
        f2.write_bytes(b"y")

        for f in (f1, f2):
            rc, out, _ = run_gfal("sum", f.as_uri(), "ADLER32")
            assert rc == 0
            lines = [ln for ln in out.strip().splitlines() if ln.strip()]
            assert len(lines) == 1

    def test_missing_file_fails(self, tmp_path):
        """A non-existent file produces a non-zero exit code."""
        missing = tmp_path / "no_such.txt"

        rc, out, err = run_gfal("sum", missing.as_uri(), "MD5")

        assert rc != 0


# ---------------------------------------------------------------------------
# Missing algorithm argument
# ---------------------------------------------------------------------------


class TestSumMissingAlgorithmArg:
    def test_no_algorithm_fails(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_bytes(b"data")

        rc, out, err = run_gfal("sum", f.as_uri())

        assert rc != 0

    def test_error_goes_to_stderr(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_bytes(b"x")

        rc, out, err = run_gfal("sum", f.as_uri(), "NOTREAL")

        assert rc != 0
        assert err.strip() != ""
