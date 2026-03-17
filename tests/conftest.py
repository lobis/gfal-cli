"""Shared pytest fixtures for gfal-cli tests."""

import os

import pytest

# ---------------------------------------------------------------------------
# Basic file fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def data_file(tmp_path):
    """A 1025-byte binary test file (matches reference gfal2-util test size)."""
    f = tmp_path / "data.bin"
    f.write_bytes(os.urandom(1025))
    return f


@pytest.fixture
def text_file(tmp_path):
    """A small text file."""
    f = tmp_path / "hello.txt"
    f.write_text("hello world\n")
    return f


@pytest.fixture
def empty_file(tmp_path):
    """A zero-byte file."""
    f = tmp_path / "empty.bin"
    f.write_bytes(b"")
    return f


@pytest.fixture
def large_file(tmp_path):
    """A 5 MiB file (larger than CHUNK_SIZE = 4 MiB)."""
    f = tmp_path / "large.bin"
    f.write_bytes(b"X" * (5 * 1024 * 1024))
    return f


# ---------------------------------------------------------------------------
# Directory fixtures (mirrors gfal2-util's TestBase setUp)
# ---------------------------------------------------------------------------


@pytest.fixture
def populated_dir(tmp_path):
    """
    A directory containing two files and a subdirectory.

    Mirrors the reference gfal2-util test setup:
      dirname/
        f1.bin   (1025 bytes)
        f2.bin   (1025 bytes)
        subdir/
    """
    d = tmp_path / "testdir"
    d.mkdir()
    f1 = d / "f1.bin"
    f2 = d / "f2.bin"
    f1.write_bytes(os.urandom(1025))
    f2.write_bytes(os.urandom(1025))
    sub = d / "subdir"
    sub.mkdir()
    return d


@pytest.fixture
def nested_dir(tmp_path):
    """
    A deeper directory tree for recursive operations.

      tree/
        a.txt
        sub1/
          b.txt
          sub2/
            c.txt
    """
    root = tmp_path / "tree"
    root.mkdir()
    (root / "a.txt").write_text("a")
    sub1 = root / "sub1"
    sub1.mkdir()
    (sub1 / "b.txt").write_text("b")
    sub2 = sub1 / "sub2"
    sub2.mkdir()
    (sub2 / "c.txt").write_text("c")
    return root


@pytest.fixture
def hidden_dir(tmp_path):
    """A directory with hidden and visible files."""
    d = tmp_path / "hidden_test"
    d.mkdir()
    (d / ".hidden1").write_text("h1")
    (d / ".hidden2").write_text("h2")
    (d / "visible1").write_text("v1")
    (d / "visible2").write_text("v2")
    return d


@pytest.fixture
def permission_file(tmp_path):
    """A file with known permissions (644)."""
    f = tmp_path / "perm.txt"
    f.write_text("content")
    f.chmod(0o644)
    return f
