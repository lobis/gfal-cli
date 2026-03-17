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


def test_sum_adler32(test_file):
    expected = f"{zlib.adler32(DATA) & 0xFFFFFFFF:08x}"

    rc, out, err = run_gfal("sum", test_file.as_uri(), "ADLER32")

    assert rc == 0
    assert expected in out


def test_sum_crc32(test_file):
    expected = f"{zlib.crc32(DATA) & 0xFFFFFFFF:08x}"

    rc, out, err = run_gfal("sum", test_file.as_uri(), "CRC32")

    assert rc == 0
    assert expected in out


def test_sum_md5(test_file):
    expected = hashlib.md5(DATA).hexdigest()

    rc, out, err = run_gfal("sum", test_file.as_uri(), "MD5")

    assert rc == 0
    assert expected in out


def test_sum_sha1(test_file):
    expected = hashlib.sha1(DATA).hexdigest()

    rc, out, err = run_gfal("sum", test_file.as_uri(), "SHA1")

    assert rc == 0
    assert expected in out


def test_sum_sha256(test_file):
    expected = hashlib.sha256(DATA).hexdigest()

    rc, out, err = run_gfal("sum", test_file.as_uri(), "SHA256")

    assert rc == 0
    assert expected in out


def test_sum_output_includes_uri(test_file):
    rc, out, err = run_gfal("sum", test_file.as_uri(), "ADLER32")

    assert rc == 0
    assert str(test_file.as_uri()) in out


def test_sum_case_insensitive_algorithm(test_file):
    """Algorithm name should be accepted in any case."""
    expected = f"{zlib.adler32(DATA) & 0xFFFFFFFF:08x}"

    rc, out, err = run_gfal("sum", test_file.as_uri(), "adler32")

    assert rc == 0
    assert expected in out


def test_sum_unknown_algorithm(tmp_path):
    f = tmp_path / "f.txt"
    f.write_bytes(DATA)

    rc, out, err = run_gfal("sum", f.as_uri(), "NOTANALGORITHM")

    assert rc != 0


def test_sum_nonexistent_file(tmp_path):
    rc, out, err = run_gfal("sum", (tmp_path / "no_such.txt").as_uri(), "MD5")

    assert rc != 0


def test_sum_empty_file(tmp_path):
    f = tmp_path / "empty.bin"
    f.write_bytes(b"")
    expected = f"{zlib.adler32(b'') & 0xFFFFFFFF:08x}"

    rc, out, err = run_gfal("sum", f.as_uri(), "ADLER32")

    assert rc == 0
    assert expected in out


def test_sum_large_file(tmp_path):
    """Checksum of a file spanning multiple read chunks (> 4 MiB)."""
    data = b"X" * (5 * 1024 * 1024)
    f = tmp_path / "large.bin"
    f.write_bytes(data)
    expected = hashlib.md5(data).hexdigest()

    rc, out, err = run_gfal("sum", f.as_uri(), "MD5")

    assert rc == 0
    assert expected in out
