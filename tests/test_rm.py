"""Tests for gfal-rm."""

from helpers import run_gfal


def test_rm_single_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("content")

    rc, out, err = run_gfal("rm", f.as_uri())

    assert rc == 0
    assert not f.exists()
    assert "DELETED" in out


def test_rm_multiple_files(tmp_path):
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f1.write_text("a")
    f2.write_text("b")

    rc, out, err = run_gfal("rm", f1.as_uri(), f2.as_uri())

    assert rc == 0
    assert not f1.exists()
    assert not f2.exists()
    assert out.count("DELETED") == 2


def test_rm_nonexistent_file(tmp_path):
    f = tmp_path / "no_such_file.txt"

    rc, out, err = run_gfal("rm", f.as_uri())

    assert rc != 0
    assert "MISSING" in out


def test_rm_directory_without_recursive(tmp_path):
    """Removing a directory without -r must fail."""
    d = tmp_path / "mydir"
    d.mkdir()

    rc, out, err = run_gfal("rm", d.as_uri())

    assert rc != 0
    assert d.is_dir()
    assert "directory" in err.lower()


def test_rm_directory_recursive(tmp_path):
    d = tmp_path / "mydir"
    d.mkdir()
    (d / "file.txt").write_text("x")
    (d / "sub").mkdir()
    (d / "sub" / "nested.txt").write_text("y")

    rc, out, err = run_gfal("rm", "-r", d.as_uri())

    assert rc == 0
    assert not d.exists()
    assert "RMDIR" in out


def test_rm_recursive_short_flag(tmp_path):
    """-R is also accepted."""
    d = tmp_path / "mydir"
    d.mkdir()
    (d / "f.txt").write_text("x")

    rc, out, err = run_gfal("rm", "-R", d.as_uri())

    assert rc == 0
    assert not d.exists()


def test_rm_dry_run_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x")

    rc, out, err = run_gfal("rm", "--dry-run", f.as_uri())

    assert rc == 0
    assert f.exists()
    assert "SKIP" in out


def test_rm_dry_run_directory(tmp_path):
    d = tmp_path / "mydir"
    d.mkdir()
    (d / "f.txt").write_text("x")

    rc, out, err = run_gfal("rm", "-r", "--dry-run", d.as_uri())

    assert rc == 0
    assert d.exists()
    assert "SKIP DIR" in out


def test_rm_from_file(tmp_path):
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f1.write_text("a")
    f2.write_text("b")

    list_file = tmp_path / "to_delete.txt"
    list_file.write_text(f"{f1.as_uri()}\n{f2.as_uri()}\n")

    rc, out, err = run_gfal("rm", "--from-file", str(list_file))

    assert rc == 0
    assert not f1.exists()
    assert not f2.exists()


def test_rm_from_file_cannot_combine_with_positional(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("x")
    list_file = tmp_path / "list.txt"
    list_file.write_text(f.as_uri())

    rc, out, err = run_gfal("rm", "--from-file", str(list_file), f.as_uri())

    assert rc != 0


def test_rm_no_args(tmp_path):
    rc, out, err = run_gfal("rm")
    assert rc != 0


def test_rm_just_delete(tmp_path):
    """--just-delete skips the stat check and deletes directly."""
    f = tmp_path / "file.txt"
    f.write_text("x")

    rc, out, err = run_gfal("rm", "--just-delete", f.as_uri())

    assert rc == 0
    assert not f.exists()
    assert "DELETED" in out
