"""Tests for gfal-chmod."""

from helpers import run_gfal


def test_chmod_sets_permissions(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")

    rc, out, err = run_gfal("chmod", "600", f.as_uri())

    assert rc == 0
    assert (f.stat().st_mode & 0o777) == 0o600


def test_chmod_readable_permissions(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")

    rc, out, err = run_gfal("chmod", "644", f.as_uri())

    assert rc == 0
    assert (f.stat().st_mode & 0o777) == 0o644


def test_chmod_with_leading_zero(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")

    rc, out, err = run_gfal("chmod", "0755", f.as_uri())

    assert rc == 0
    assert (f.stat().st_mode & 0o777) == 0o755


def test_chmod_invalid_mode(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("x")

    rc, out, err = run_gfal("chmod", "XYZ", f.as_uri())

    assert rc != 0


def test_chmod_nonexistent_file(tmp_path):
    rc, out, err = run_gfal("chmod", "644", (tmp_path / "no_such.txt").as_uri())

    assert rc != 0
