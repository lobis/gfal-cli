"""Tests for gfal-mkdir."""

from helpers import run_gfal


def test_mkdir_basic(tmp_path):
    d = tmp_path / "newdir"

    rc, out, err = run_gfal("mkdir", d.as_uri())

    assert rc == 0
    assert d.is_dir()


def test_mkdir_mode(tmp_path):
    d = tmp_path / "modedir"

    rc, out, err = run_gfal("mkdir", "-m", "700", d.as_uri())

    assert rc == 0
    assert d.is_dir()


def test_mkdir_multiple(tmp_path):
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir2"

    rc, out, err = run_gfal("mkdir", d1.as_uri(), d2.as_uri())

    assert rc == 0
    assert d1.is_dir()
    assert d2.is_dir()


def test_mkdir_parents(tmp_path):
    d = tmp_path / "a" / "b" / "c"

    rc, out, err = run_gfal("mkdir", "-p", d.as_uri())

    assert rc == 0
    assert d.is_dir()


def test_mkdir_already_exists_fails(tmp_path):
    d = tmp_path / "existing"
    d.mkdir()

    rc, out, err = run_gfal("mkdir", d.as_uri())

    assert rc != 0


def test_mkdir_already_exists_with_parents_ok(tmp_path):
    """-p must not error on an already-existing directory."""
    d = tmp_path / "existing"
    d.mkdir()

    rc, out, err = run_gfal("mkdir", "-p", d.as_uri())

    assert rc == 0
    assert d.is_dir()


def test_mkdir_invalid_mode(tmp_path):
    """Argparse rejects non-integer mode values."""
    d = tmp_path / "badmode"

    rc, out, err = run_gfal("mkdir", "-m", "ABC", d.as_uri())

    assert rc != 0
    assert not d.exists()
