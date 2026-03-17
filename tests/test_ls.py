"""Tests for gfal-ls — mirrors reference gfal2-util/test/functional/test_ls.py."""

import pytest

from helpers import run_gfal

# ---------------------------------------------------------------------------
# Basic listing
# ---------------------------------------------------------------------------


class TestLsBasic:
    def test_list_directory(self, tmp_path):
        (tmp_path / "alpha.txt").write_text("a")
        (tmp_path / "beta.txt").write_text("b")

        rc, out, err = run_gfal("ls", tmp_path.as_uri())

        assert rc == 0
        assert "alpha.txt" in out
        assert "beta.txt" in out

    def test_list_counts_match(self, tmp_path):
        """Output line count should equal the number of entries (ref: test_basic)."""
        (tmp_path / "f1.bin").write_bytes(b"x")
        (tmp_path / "f2.bin").write_bytes(b"y")
        sub = tmp_path / "subdir"
        sub.mkdir()

        rc, out, err = run_gfal("ls", tmp_path.as_uri())

        assert rc == 0
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == len(list(tmp_path.iterdir()))

    def test_list_single_file(self, tmp_path):
        f = tmp_path / "solo.txt"
        f.write_text("content")

        rc, out, err = run_gfal("ls", f.as_uri())

        assert rc == 0
        assert "solo.txt" in out

    def test_list_empty_directory(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()

        rc, out, err = run_gfal("ls", d.as_uri())

        assert rc == 0
        assert out.strip() == ""

    def test_list_nonexistent(self, tmp_path):
        rc, out, err = run_gfal("ls", (tmp_path / "no_such_path").as_uri())
        assert rc != 0


# ---------------------------------------------------------------------------
# Long format (-l)
# ---------------------------------------------------------------------------


class TestLsLongFormat:
    def test_long_format_shows_size(self, tmp_path):
        """Reference: test_size — '-l' shows raw byte count."""
        f = tmp_path / "file.txt"
        f.write_bytes(b"x" * 1025)

        rc, out, err = run_gfal("ls", "-l", tmp_path.as_uri())

        assert rc == 0
        assert "1025" in out
        assert "file.txt" in out

    def test_long_format_human_readable(self, tmp_path):
        """Reference: test_size — '-lH' shows human-readable size."""
        f = tmp_path / "file.txt"
        f.write_bytes(b"x" * 1025)

        rc, out, err = run_gfal("ls", "-lH", tmp_path.as_uri())

        assert rc == 0
        assert "1.1K" in out

    def test_long_format_single_file(self, tmp_path):
        f = tmp_path / "solo.txt"
        f.write_bytes(b"y" * 42)

        rc, out, err = run_gfal("ls", "-l", f.as_uri())

        assert rc == 0
        assert "42" in out

    def test_long_format_shows_name(self, tmp_path):
        """Reference: test_name — long format includes the URI."""
        f = tmp_path / "myfile.txt"
        f.write_text("x")

        rc, out, err = run_gfal("ls", "-l", f.as_uri())

        assert rc == 0
        assert f.as_uri() in out

    def test_long_format_permissions_string(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")

        rc, out, err = run_gfal("ls", "-l", tmp_path.as_uri())

        assert rc == 0
        # Should contain something like "-rw-r--r--" or similar
        assert "rw" in out

    def test_long_format_invalid_file(self, tmp_path):
        """Reference: test_invalid — nonexistent file returns errno 2."""
        inv = tmp_path / "INVALID"
        rc, out, err = run_gfal("ls", "-lH", inv.as_uri())

        assert rc != 0
        assert len(out) == 0 or "No such file" in err


# ---------------------------------------------------------------------------
# -d directory flag
# ---------------------------------------------------------------------------


class TestLsDirectoryFlag:
    def test_directory_flag_shows_single_entry(self, tmp_path):
        """Reference: test_directory — '-d' gives one line, not contents."""
        (tmp_path / "child.txt").write_text("c")

        rc, out, err = run_gfal("ls", "-d", tmp_path.as_uri())

        assert rc == 0
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 1
        assert "child.txt" not in out

    def test_directory_flag_long_format(self, tmp_path):
        """Reference: test_name — '-dl' includes the URI."""
        f = tmp_path / "myfile.txt"
        f.write_text("x")

        rc, out, err = run_gfal("ls", "-dl", f.as_uri())

        assert rc == 0
        assert f.as_uri() in out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 1


# ---------------------------------------------------------------------------
# Hidden files
# ---------------------------------------------------------------------------


class TestLsHiddenFiles:
    def test_hidden_files_hidden_by_default(self, hidden_dir):
        rc, out, err = run_gfal("ls", hidden_dir.as_uri())

        assert rc == 0
        assert ".hidden1" not in out
        assert ".hidden2" not in out
        assert "visible1" in out
        assert "visible2" in out

    def test_hidden_files_shown_with_all(self, hidden_dir):
        rc, out, err = run_gfal("ls", "-a", hidden_dir.as_uri())

        assert rc == 0
        assert ".hidden1" in out
        assert ".hidden2" in out
        assert "visible1" in out
        assert "visible2" in out


# ---------------------------------------------------------------------------
# Time styles
# ---------------------------------------------------------------------------


class TestLsTimeStyles:
    @pytest.mark.parametrize("style", ["full-iso", "long-iso", "iso", "locale"])
    def test_time_style(self, tmp_path, style):
        (tmp_path / "f.txt").write_text("x")

        rc, out, err = run_gfal("ls", "-l", f"--time-style={style}", tmp_path.as_uri())

        assert rc == 0
        assert "f.txt" in out

    def test_full_time(self, tmp_path):
        (tmp_path / "f.txt").write_text("x")

        rc, out, err = run_gfal("ls", "-l", "--full-time", tmp_path.as_uri())

        assert rc == 0
        assert "f.txt" in out


# ---------------------------------------------------------------------------
# Color output
# ---------------------------------------------------------------------------


class TestLsColor:
    def test_color_never(self, tmp_path):
        (tmp_path / "f.txt").write_text("x")

        rc, out, err = run_gfal("ls", "--color=never", tmp_path.as_uri())

        assert rc == 0
        assert "\033[" not in out

    def test_color_always(self, tmp_path):
        (tmp_path / "f.txt").write_text("x")

        rc, out, err = run_gfal("ls", "--color=always", tmp_path.as_uri())

        assert rc == 0
        assert "\033[" in out

    def test_color_always_directory(self, tmp_path):
        """Directories should be colorised differently from files."""
        sub = tmp_path / "mysubdir"
        sub.mkdir()

        rc, out, err = run_gfal("ls", "--color=always", tmp_path.as_uri())

        assert rc == 0
        assert "\033[" in out


# ---------------------------------------------------------------------------
# Human-readable sizes
# ---------------------------------------------------------------------------


class TestLsHumanReadable:
    @pytest.mark.parametrize(
        "size, expected",
        [
            (0, "0"),
            (512, "512"),
            (1024, "1.0K"),
            (1025, "1.1K"),
            (1048576, "1.0M"),
            (1073741824, "1.0G"),
        ],
    )
    def test_human_size_values(self, tmp_path, size, expected):
        """Verify -lH produces expected human-readable values."""
        f = tmp_path / "test.bin"
        f.write_bytes(b"\x00" * size)

        rc, out, err = run_gfal("ls", "-lH", f.as_uri())

        assert rc == 0
        assert expected in out


# ---------------------------------------------------------------------------
# Multiple files / subdirectories
# ---------------------------------------------------------------------------


class TestLsPopulatedDir:
    def test_list_populated_dir(self, populated_dir):
        rc, out, err = run_gfal("ls", populated_dir.as_uri())

        assert rc == 0
        assert "f1.bin" in out
        assert "f2.bin" in out
        assert "subdir" in out

    def test_list_long_populated_dir(self, populated_dir):
        rc, out, err = run_gfal("ls", "-l", populated_dir.as_uri())

        assert rc == 0
        assert "1025" in out  # file size
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 3  # f1.bin, f2.bin, subdir
