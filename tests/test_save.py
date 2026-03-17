"""Tests for gfal-save (stdin → remote file)."""

import subprocess
import sys

from helpers import run_gfal


def test_save_text(tmp_path):
    f = tmp_path / "out.txt"
    content = "hello from stdin\n"

    rc, out, err = run_gfal("save", f.as_uri(), input=content)

    assert rc == 0
    assert f.read_text() == content


def test_save_binary(tmp_path):
    f = tmp_path / "out.bin"
    data = bytes(range(256))

    script = (
        "import sys; sys.argv=['gfal-save']+sys.argv[1:];"
        "from gfal_cli.shell import main; main()"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, f.as_uri()],
        input=data,
        capture_output=True,
    )

    assert proc.returncode == 0
    assert f.read_bytes() == data


def test_save_empty_stdin(tmp_path):
    f = tmp_path / "empty.txt"

    rc, out, err = run_gfal("save", f.as_uri(), input="")

    assert rc == 0
    assert f.read_bytes() == b""


def test_save_large_input(tmp_path):
    """Input larger than CHUNK_SIZE (4 MiB)."""
    f = tmp_path / "large.bin"
    data = b"B" * (5 * 1024 * 1024)

    script = (
        "import sys; sys.argv=['gfal-save']+sys.argv[1:];"
        "from gfal_cli.shell import main; main()"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, f.as_uri()],
        input=data,
        capture_output=True,
    )

    assert proc.returncode == 0
    assert f.read_bytes() == data


def test_save_overwrites_existing(tmp_path):
    f = tmp_path / "existing.txt"
    f.write_text("old content")

    rc, out, err = run_gfal("save", f.as_uri(), input="new content")

    assert rc == 0
    assert f.read_text() == "new content"
