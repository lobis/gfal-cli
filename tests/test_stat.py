"""Tests for gfal-stat."""

from helpers import run_gfal


def test_stat_regular_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes(b"hello world")

    rc, out, err = run_gfal("stat", f.as_uri())

    assert rc == 0
    assert "File:" in out
    assert "Size:" in out
    assert "11" in out  # 11 bytes
    assert "Access:" in out
    assert "Modify:" in out
    assert "Change:" in out


def test_stat_shows_file_type(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")

    rc, out, err = run_gfal("stat", f.as_uri())

    assert rc == 0
    assert "regular file" in out


def test_stat_directory(tmp_path):
    rc, out, err = run_gfal("stat", tmp_path.as_uri())

    assert rc == 0
    assert "directory" in out


def test_stat_shows_size_zero(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")

    rc, out, err = run_gfal("stat", f.as_uri())

    assert rc == 0
    assert "0" in out


def test_stat_nonexistent(tmp_path):
    rc, out, err = run_gfal("stat", (tmp_path / "no_such_file").as_uri())

    assert rc != 0


def test_stat_shows_uri_in_output(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")
    uri = f.as_uri()

    rc, out, err = run_gfal("stat", uri)

    assert rc == 0
    assert uri in out
