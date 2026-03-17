"""Tests for gfal-ls."""

import pytest

from helpers import run_gfal


def test_list_directory(tmp_path):
    (tmp_path / "alpha.txt").write_text("a")
    (tmp_path / "beta.txt").write_text("b")

    rc, out, err = run_gfal("ls", tmp_path.as_uri())

    assert rc == 0
    assert "alpha.txt" in out
    assert "beta.txt" in out


def test_list_long_format(tmp_path):
    f = tmp_path / "file.txt"
    f.write_bytes(b"x" * 1025)

    rc, out, err = run_gfal("ls", "-l", tmp_path.as_uri())

    assert rc == 0
    assert "1025" in out
    assert "file.txt" in out


def test_list_human_readable(tmp_path):
    f = tmp_path / "file.txt"
    f.write_bytes(b"x" * 1025)

    rc, out, err = run_gfal("ls", "-lH", tmp_path.as_uri())

    assert rc == 0
    # 1025 bytes → 1.1K (ceiling division)
    assert "1.1K" in out


def test_list_single_file(tmp_path):
    f = tmp_path / "solo.txt"
    f.write_text("content")

    rc, out, err = run_gfal("ls", f.as_uri())

    assert rc == 0
    assert "solo.txt" in out


def test_list_single_file_long(tmp_path):
    f = tmp_path / "solo.txt"
    f.write_bytes(b"y" * 42)

    rc, out, err = run_gfal("ls", "-l", f.as_uri())

    assert rc == 0
    assert "42" in out


def test_list_directory_flag(tmp_path):
    """``-d`` shows the directory entry itself, not its contents."""
    (tmp_path / "child.txt").write_text("c")

    rc, out, err = run_gfal("ls", "-d", tmp_path.as_uri())

    assert rc == 0
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "child.txt" not in out


def test_list_hidden_files_hidden_by_default(tmp_path):
    (tmp_path / ".hidden").write_text("h")
    (tmp_path / "visible").write_text("v")

    rc, out, err = run_gfal("ls", tmp_path.as_uri())

    assert rc == 0
    assert ".hidden" not in out
    assert "visible" in out


def test_list_hidden_files_shown_with_all(tmp_path):
    (tmp_path / ".hidden").write_text("h")
    (tmp_path / "visible").write_text("v")

    rc, out, err = run_gfal("ls", "-a", tmp_path.as_uri())

    assert rc == 0
    assert ".hidden" in out


def test_list_nonexistent(tmp_path):
    rc, out, err = run_gfal("ls", (tmp_path / "no_such_path").as_uri())
    assert rc != 0


def test_list_empty_directory(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()

    rc, out, err = run_gfal("ls", d.as_uri())

    assert rc == 0
    assert out.strip() == ""


@pytest.mark.parametrize("style", ["full-iso", "long-iso", "iso", "locale"])
def test_list_time_styles(tmp_path, style):
    (tmp_path / "f.txt").write_text("x")

    rc, out, err = run_gfal("ls", "-l", f"--time-style={style}", tmp_path.as_uri())

    assert rc == 0
    assert "f.txt" in out


def test_list_full_time(tmp_path):
    (tmp_path / "f.txt").write_text("x")

    rc, out, err = run_gfal("ls", "-l", "--full-time", tmp_path.as_uri())

    assert rc == 0
    assert "f.txt" in out


def test_list_color_never(tmp_path):
    (tmp_path / "f.txt").write_text("x")

    rc, out, err = run_gfal("ls", "--color=never", tmp_path.as_uri())

    assert rc == 0
    # No ANSI escape codes
    assert "\033[" not in out


def test_list_color_always(tmp_path):
    (tmp_path / "f.txt").write_text("x")

    rc, out, err = run_gfal("ls", "--color=always", tmp_path.as_uri())

    assert rc == 0
    assert "\033[" in out
