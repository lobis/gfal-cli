"""Tests for gfal-rename."""

from helpers import run_gfal


def test_rename_file(tmp_path):
    src = tmp_path / "old.txt"
    dst = tmp_path / "new.txt"
    src.write_text("content")

    rc, out, err = run_gfal("rename", src.as_uri(), dst.as_uri())

    assert rc == 0
    assert not src.exists()
    assert dst.read_text() == "content"


def test_rename_directory(tmp_path):
    src = tmp_path / "olddir"
    dst = tmp_path / "newdir"
    src.mkdir()
    (src / "file.txt").write_text("x")

    rc, out, err = run_gfal("rename", src.as_uri(), dst.as_uri())

    assert rc == 0
    assert not src.exists()
    assert dst.is_dir()
    assert (dst / "file.txt").read_text() == "x"


def test_rename_nonexistent_source(tmp_path):
    src = tmp_path / "no_such.txt"
    dst = tmp_path / "dst.txt"

    rc, out, err = run_gfal("rename", src.as_uri(), dst.as_uri())

    assert rc != 0


def test_rename_overwrites_existing_destination(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("new")
    dst.write_text("old")

    rc, out, err = run_gfal("rename", src.as_uri(), dst.as_uri())

    assert rc == 0
    assert not src.exists()
    assert dst.read_text() == "new"
