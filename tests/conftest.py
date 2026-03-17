"""Shared pytest fixtures for gfal-cli tests."""

import pytest


@pytest.fixture
def data_file(tmp_path):
    """A 1025-byte binary test file."""
    f = tmp_path / "data.bin"
    f.write_bytes(b"x" * 1025)
    return f


@pytest.fixture
def text_file(tmp_path):
    """A small text file."""
    f = tmp_path / "hello.txt"
    f.write_text("hello world\n")
    return f
