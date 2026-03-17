"""Tests for gfal-chmod."""

import sys

import pytest

from helpers import run_gfal

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX chmod semantics are not available on Windows",
)

# ---------------------------------------------------------------------------
# Setting permissions
# ---------------------------------------------------------------------------


class TestChmodPermissions:
    def test_set_600(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "600", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o600

    def test_set_644(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "644", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o644

    def test_set_755(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "755", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o755

    def test_set_444(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "444", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o444

    def test_set_000(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "000", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o000
        # Restore for cleanup
        f.chmod(0o644)

    def test_set_777(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "777", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o777


# ---------------------------------------------------------------------------
# Leading zero (octal notation)
# ---------------------------------------------------------------------------


class TestChmodLeadingZero:
    def test_with_leading_zero_0755(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "0755", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o755

    def test_with_leading_zero_0644(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "0644", f.as_uri())

        assert rc == 0
        assert (f.stat().st_mode & 0o777) == 0o644


# ---------------------------------------------------------------------------
# Directory permissions
# ---------------------------------------------------------------------------


class TestChmodDirectory:
    def test_chmod_directory(self, tmp_path):
        d = tmp_path / "testdir"
        d.mkdir()

        rc, out, err = run_gfal("chmod", "700", d.as_uri())

        assert rc == 0
        assert (d.stat().st_mode & 0o777) == 0o700
        # Restore for cleanup
        d.chmod(0o755)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestChmodErrors:
    def test_invalid_mode(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "XYZ", f.as_uri())

        assert rc != 0

    def test_invalid_mode_text(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("chmod", "abc", f.as_uri())

        assert rc != 0

    def test_nonexistent_file(self, tmp_path):
        rc, out, err = run_gfal("chmod", "644", (tmp_path / "no_such.txt").as_uri())

        assert rc != 0
