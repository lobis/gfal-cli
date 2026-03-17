"""Tests for gfal-stat."""

from helpers import run_gfal

# ---------------------------------------------------------------------------
# Regular files
# ---------------------------------------------------------------------------


class TestStatRegularFile:
    def test_regular_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        assert "File:" in out
        assert "Size:" in out
        assert "11" in out
        assert "Access:" in out
        assert "Modify:" in out
        assert "Change:" in out

    def test_shows_file_type(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        assert "regular file" in out

    def test_shows_size_zero(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        assert "Size: 0" in out

    def test_shows_uri_in_output(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")
        uri = f.as_uri()

        rc, out, err = run_gfal("stat", uri)

        assert rc == 0
        assert uri in out

    def test_shows_permissions(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        # Should show something like (0644/-rw-r--r--)
        assert "/" in out  # The mode string like "0644/-rw-r--r--"

    def test_various_sizes(self, tmp_path):
        for size in [1, 100, 1025, 65536]:
            f = tmp_path / f"file_{size}.bin"
            f.write_bytes(b"x" * size)

            rc, out, err = run_gfal("stat", f.as_uri())

            assert rc == 0
            assert str(size) in out


# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------


class TestStatDirectory:
    def test_directory(self, tmp_path):
        rc, out, err = run_gfal("stat", tmp_path.as_uri())

        assert rc == 0
        assert "directory" in out

    def test_subdirectory(self, tmp_path):
        d = tmp_path / "sub"
        d.mkdir()

        rc, out, err = run_gfal("stat", d.as_uri())

        assert rc == 0
        assert "directory" in out


# ---------------------------------------------------------------------------
# Nonexistent
# ---------------------------------------------------------------------------


class TestStatNonexistent:
    def test_nonexistent_file(self, tmp_path):
        rc, out, err = run_gfal("stat", (tmp_path / "no_such_file").as_uri())

        assert rc != 0

    def test_nonexistent_nested(self, tmp_path):
        rc, out, err = run_gfal(
            "stat", (tmp_path / "a" / "b" / "c" / "no_such").as_uri()
        )

        assert rc != 0


# ---------------------------------------------------------------------------
# Timestamps
# ---------------------------------------------------------------------------


class TestStatTimestamps:
    def test_timestamps_present(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        # Should have Access:, Modify:, Change: timestamps
        assert out.count("Access:") == 2  # permission + timestamp
        assert "Modify:" in out
        assert "Change:" in out

    def test_timestamp_format(self, tmp_path):
        """Timestamps should be in YYYY-MM-DD HH:MM:SS format."""
        f = tmp_path / "test.txt"
        f.write_text("x")

        rc, out, err = run_gfal("stat", f.as_uri())

        assert rc == 0
        # Look for a timestamp-like pattern
        import re

        assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", out)
