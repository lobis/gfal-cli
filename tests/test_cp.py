"""Tests for gfal-cp / gfal-copy — mirrors reference gfal2-util/test/functional/test_copy.py."""

import hashlib
import os
import zlib

from helpers import run_gfal

# ---------------------------------------------------------------------------
# Basic copy
# ---------------------------------------------------------------------------


class TestCopyBasic:
    def test_copy_basic(self, tmp_path):
        """Reference: test_copy."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello world")

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"hello world"

    def test_copy_preserves_content(self, tmp_path):
        """Random binary data is preserved exactly."""
        data = os.urandom(2048)
        src = tmp_path / "src.bin"
        dst = tmp_path / "dst.bin"
        src.write_bytes(data)

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == data

    def test_copy_empty_file(self, tmp_path):
        src = tmp_path / "empty.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"")

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b""

    def test_copy_missing_source(self, tmp_path):
        src = tmp_path / "no_such_file.txt"
        dst = tmp_path / "dst.txt"

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc != 0
        assert not dst.exists()


# ---------------------------------------------------------------------------
# Copy to directory
# ---------------------------------------------------------------------------


class TestCopyToDirectory:
    def test_copy_to_directory(self, tmp_path):
        """Reference: test_copy_no_basename / test_copy_dst_dir."""
        src = tmp_path / "src.txt"
        dstdir = tmp_path / "dstdir"
        src.write_bytes(b"hello")
        dstdir.mkdir()

        rc, out, err = run_gfal("cp", src.as_uri(), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "src.txt").read_bytes() == b"hello"

    def test_copy_to_directory_trailing_slash(self, tmp_path):
        """Destination with trailing slash is a directory."""
        src = tmp_path / "src.txt"
        dstdir = tmp_path / "dstdir"
        src.write_bytes(b"data")
        dstdir.mkdir()

        rc, out, err = run_gfal("cp", src.as_uri(), dstdir.as_uri() + "/")

        assert rc == 0
        assert (dstdir / "src.txt").read_bytes() == b"data"


# ---------------------------------------------------------------------------
# Overwrite / --force
# ---------------------------------------------------------------------------


class TestCopyOverwrite:
    def test_no_overwrite_by_default(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"new content")
        dst.write_bytes(b"old content")

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc != 0
        assert dst.read_bytes() == b"old content"

    def test_force_overwrite(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"new content")
        dst.write_bytes(b"old content")

        rc, out, err = run_gfal("cp", "-f", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"new content"


# ---------------------------------------------------------------------------
# Chained copy (src→dst1, dst1→dst2)
# ---------------------------------------------------------------------------


class TestCopyChain:
    def test_chain_two_destinations(self, tmp_path):
        """Reference: test_chain_copy."""
        src = tmp_path / "src.txt"
        dst1 = tmp_path / "dst1.txt"
        dst2 = tmp_path / "dst2.txt"
        src.write_bytes(b"chained data")

        rc, out, err = run_gfal("cp", src.as_uri(), dst1.as_uri(), dst2.as_uri())

        assert rc == 0
        assert dst1.read_bytes() == b"chained data"
        assert dst2.read_bytes() == b"chained data"

    def test_chain_to_directory(self, tmp_path):
        """Last destination is a directory."""
        src = tmp_path / "src.txt"
        dstdir = tmp_path / "dstdir"
        dstdir.mkdir()
        src.write_bytes(b"data")

        rc, out, err = run_gfal("cp", src.as_uri(), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "src.txt").read_bytes() == b"data"


# ---------------------------------------------------------------------------
# Recursive copy (-r)
# ---------------------------------------------------------------------------


class TestCopyRecursive:
    def test_recursive(self, tmp_path):
        srcdir = tmp_path / "srcdir"
        srcdir.mkdir()
        (srcdir / "file1.txt").write_bytes(b"f1")
        (srcdir / "file2.txt").write_bytes(b"f2")
        dstdir = tmp_path / "dstdir"

        rc, out, err = run_gfal("cp", "-r", srcdir.as_uri(), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "file1.txt").read_bytes() == b"f1"
        assert (dstdir / "file2.txt").read_bytes() == b"f2"

    def test_recursive_nested(self, nested_dir, tmp_path):
        dstdir = tmp_path / "copy"

        rc, out, err = run_gfal("cp", "-r", nested_dir.as_uri(), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "a.txt").read_text() == "a"
        assert (dstdir / "sub1" / "b.txt").read_text() == "b"
        assert (dstdir / "sub1" / "sub2" / "c.txt").read_text() == "c"

    def test_dir_skipped_without_recursive(self, tmp_path):
        """Reference: test_copy_dir — copying a directory without -r is skipped."""
        srcdir = tmp_path / "srcdir"
        srcdir.mkdir()
        dstdir = tmp_path / "dstdir"

        rc, out, err = run_gfal("cp", srcdir.as_uri(), dstdir.as_uri())

        assert rc == 0
        assert not dstdir.exists()
        assert "Skipping directory" in out or "skip" in out.lower()


# ---------------------------------------------------------------------------
# Parent directory creation (-p)
# ---------------------------------------------------------------------------


class TestCopyParent:
    def test_parent_creates_dirs(self, tmp_path):
        """Reference: test_copy_parent_mkdir."""
        src = tmp_path / "src.txt"
        src.write_bytes(b"data")
        dst = tmp_path / "nested" / "deep" / "dst.txt"

        rc, out, err = run_gfal("cp", "-p", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"data"

    def test_parent_fails_without_flag(self, tmp_path):
        """Reference: test_copy_parent_enoent."""
        src = tmp_path / "src.txt"
        src.write_bytes(b"data")
        dst = tmp_path / "nested" / "deep" / "dst.txt"

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc != 0
        assert not dst.exists()


# ---------------------------------------------------------------------------
# Checksum (-K)
# ---------------------------------------------------------------------------


class TestCopyChecksum:
    def test_checksum_adler32(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello world")

        rc, out, err = run_gfal("cp", "-K", "ADLER32", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"hello world"

    def test_checksum_md5(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello world")

        rc, out, err = run_gfal("cp", "-K", "MD5", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"hello world"

    def test_checksum_sha256(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello world")

        rc, out, err = run_gfal("cp", "-K", "SHA256", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"hello world"

    def test_checksum_with_expected_value(self, tmp_path):
        data = b"hello world"
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(data)
        expected = f"{zlib.adler32(data) & 0xFFFFFFFF:08x}"

        rc, out, err = run_gfal(
            "cp", "-K", f"ADLER32:{expected}", src.as_uri(), dst.as_uri()
        )

        assert rc == 0
        assert dst.read_bytes() == data

    def test_checksum_wrong_expected_value(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello world")

        rc, out, err = run_gfal(
            "cp", "-K", "ADLER32:00000000", src.as_uri(), dst.as_uri()
        )

        assert rc != 0

    def test_checksum_md5_expected_value(self, tmp_path):
        data = b"test data for md5"
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(data)
        expected = hashlib.md5(data).hexdigest()

        rc, out, err = run_gfal(
            "cp", "-K", f"MD5:{expected}", src.as_uri(), dst.as_uri()
        )

        assert rc == 0

    def test_checksum_mode_source(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"data")

        rc, out, err = run_gfal(
            "cp",
            "-K",
            "ADLER32",
            "--checksum-mode",
            "source",
            src.as_uri(),
            dst.as_uri(),
        )

        assert rc == 0
        assert dst.read_bytes() == b"data"

    def test_checksum_mode_target(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"data")

        rc, out, err = run_gfal(
            "cp",
            "-K",
            "ADLER32",
            "--checksum-mode",
            "target",
            src.as_uri(),
            dst.as_uri(),
        )

        assert rc == 0
        assert dst.read_bytes() == b"data"


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


class TestCopyDryRun:
    def test_dry_run(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello")

        rc, out, err = run_gfal("cp", "--dry-run", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert not dst.exists()
        assert "Copy" in out

    def test_dry_run_recursive(self, nested_dir, tmp_path):
        dstdir = tmp_path / "copy"

        rc, out, err = run_gfal(
            "cp", "-r", "--dry-run", nested_dir.as_uri(), dstdir.as_uri()
        )

        assert rc == 0
        assert not dstdir.exists()


# ---------------------------------------------------------------------------
# --from-file
# ---------------------------------------------------------------------------


class TestCopyFromFile:
    def test_from_file(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_bytes(b"from-file content")
        dstdir = tmp_path / "dstdir"
        dstdir.mkdir()

        sources_file = tmp_path / "sources.txt"
        sources_file.write_text(f"{src.as_uri()}\n")

        rc, out, err = run_gfal("cp", "--from-file", str(sources_file), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "src.txt").read_bytes() == b"from-file content"

    def test_from_file_multiple_sources(self, tmp_path):
        src1 = tmp_path / "s1.txt"
        src2 = tmp_path / "s2.txt"
        src1.write_bytes(b"one")
        src2.write_bytes(b"two")
        dstdir = tmp_path / "dstdir"
        dstdir.mkdir()

        sources_file = tmp_path / "sources.txt"
        sources_file.write_text(f"{src1.as_uri()}\n{src2.as_uri()}\n")

        rc, out, err = run_gfal("cp", "--from-file", str(sources_file), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "s1.txt").read_bytes() == b"one"
        assert (dstdir / "s2.txt").read_bytes() == b"two"

    def test_from_file_cannot_combine_with_src(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("x")
        dst = tmp_path / "dst.txt"
        sources_file = tmp_path / "srcs.txt"
        sources_file.write_text(src.as_uri())

        rc, out, err = run_gfal(
            "cp", "--from-file", str(sources_file), src.as_uri(), dst.as_uri()
        )

        assert rc != 0

    def test_from_file_blank_lines_ignored(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_bytes(b"data")
        dstdir = tmp_path / "dstdir"
        dstdir.mkdir()

        sources_file = tmp_path / "sources.txt"
        sources_file.write_text(f"\n{src.as_uri()}\n\n\n")

        rc, out, err = run_gfal("cp", "--from-file", str(sources_file), dstdir.as_uri())

        assert rc == 0
        assert (dstdir / "src.txt").read_bytes() == b"data"


# ---------------------------------------------------------------------------
# --abort-on-failure
# ---------------------------------------------------------------------------


class TestCopyAbortOnFailure:
    def test_abort_on_failure(self, tmp_path):
        """With --abort-on-failure the copy stops after the first error."""
        src = tmp_path / "src.txt"
        src.write_bytes(b"data")
        dst1 = tmp_path / "dst1.txt"
        dst1.write_bytes(b"old")

        rc, out, err = run_gfal("cp", "--abort-on-failure", src.as_uri(), dst1.as_uri())

        assert rc != 0
        assert dst1.read_bytes() == b"old"


# ---------------------------------------------------------------------------
# Large files
# ---------------------------------------------------------------------------


class TestCopyLargeFile:
    def test_large_file(self, tmp_path):
        """Copy a file larger than CHUNK_SIZE (4 MiB)."""
        src = tmp_path / "large.bin"
        data = b"A" * (5 * 1024 * 1024)
        src.write_bytes(data)
        dst = tmp_path / "large_dst.bin"

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == data

    def test_large_file_with_checksum(self, tmp_path):
        src = tmp_path / "large.bin"
        data = b"B" * (5 * 1024 * 1024)
        src.write_bytes(data)
        dst = tmp_path / "large_dst.bin"

        rc, out, err = run_gfal("cp", "-K", "MD5", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == data


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------


class TestCopyAlias:
    def test_cp_alias(self, tmp_path):
        """gfal-cp is an alias for gfal-copy."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"alias test")

        rc, out, err = run_gfal("cp", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"alias test"

    def test_copy_command(self, tmp_path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"copy test")

        rc, out, err = run_gfal("copy", src.as_uri(), dst.as_uri())

        assert rc == 0
        assert dst.read_bytes() == b"copy test"


# ---------------------------------------------------------------------------
# --transfer-timeout
# ---------------------------------------------------------------------------


class TestCopyTransferTimeout:
    def test_transfer_timeout_zero_succeeds(self, tmp_path):
        """--transfer-timeout=0 means no per-file timeout; copy should succeed."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"hello")

        rc, out, err = run_gfal(
            "cp", "--transfer-timeout", "0", src.as_uri(), dst.as_uri()
        )

        assert rc == 0
        assert dst.read_bytes() == b"hello"

    def test_transfer_timeout_generous_succeeds(self, tmp_path):
        """A generous timeout (600s) should not interfere with a normal copy."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_bytes(b"data" * 100)

        rc, out, err = run_gfal(
            "cp", "--transfer-timeout", "600", src.as_uri(), dst.as_uri()
        )

        assert rc == 0
        assert dst.read_bytes() == b"data" * 100

    def test_transfer_timeout_appears_in_help(self):
        rc, out, err = run_gfal("cp", "--help")
        assert "transfer-timeout" in out or "transfer-timeout" in err
