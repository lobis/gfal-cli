"""Tests for gfal-cat."""

from helpers import run_gfal


def test_cat_single_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world\n")

    rc, out, err = run_gfal("cat", f.as_uri())

    assert rc == 0
    assert out == "hello world\n"


def test_cat_binary_content(tmp_path):
    """Content is passed through as-is; we check the byte count via len."""
    data = bytes(range(256))
    f = tmp_path / "binary.bin"
    f.write_bytes(data)

    # Run without text mode so we can compare raw bytes
    import subprocess
    import sys

    script = (
        "import sys; sys.argv=['gfal-cat']+sys.argv[1:];"
        "from gfal_cli.shell import main; main()"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, f.as_uri()],
        capture_output=True,
    )
    assert proc.returncode == 0
    assert proc.stdout == data


def test_cat_multiple_files(tmp_path):
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f1.write_text("part1")
    f2.write_text("part2")

    rc, out, err = run_gfal("cat", f1.as_uri(), f2.as_uri())

    assert rc == 0
    assert out == "part1part2"


def test_cat_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")

    rc, out, err = run_gfal("cat", f.as_uri())

    assert rc == 0
    assert out == ""


def test_cat_nonexistent(tmp_path):
    rc, out, err = run_gfal("cat", (tmp_path / "no_such_file.txt").as_uri())

    assert rc != 0


def test_cat_large_file(tmp_path):
    """Content across multiple read chunks (> 4 MiB)."""
    data = b"Z" * (5 * 1024 * 1024)
    f = tmp_path / "large.bin"
    f.write_bytes(data)

    import subprocess
    import sys

    script = (
        "import sys; sys.argv=['gfal-cat']+sys.argv[1:];"
        "from gfal_cli.shell import main; main()"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, f.as_uri()],
        capture_output=True,
    )
    assert proc.returncode == 0
    assert proc.stdout == data
