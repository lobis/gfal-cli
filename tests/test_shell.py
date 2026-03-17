"""Tests for shell.py: dispatch, aliases, and error handling."""

import pytest

from gfal_cli.shell import _command_from_argv0, _find_command

# ---------------------------------------------------------------------------
# _command_from_argv0
# ---------------------------------------------------------------------------


class TestCommandFromArgv0:
    def test_gfal_ls(self):
        assert _command_from_argv0("gfal-ls") == "ls"

    def test_gfal_copy(self):
        assert _command_from_argv0("gfal-copy") == "copy"

    def test_gfal_cp_alias(self):
        assert _command_from_argv0("gfal-cp") == "copy"

    def test_gfal_rm(self):
        assert _command_from_argv0("gfal-rm") == "rm"

    def test_gfal_mkdir(self):
        assert _command_from_argv0("gfal-mkdir") == "mkdir"

    def test_gfal_stat(self):
        assert _command_from_argv0("gfal-stat") == "stat"

    def test_gfal_cat(self):
        assert _command_from_argv0("gfal-cat") == "cat"

    def test_gfal_save(self):
        assert _command_from_argv0("gfal-save") == "save"

    def test_gfal_rename(self):
        assert _command_from_argv0("gfal-rename") == "rename"

    def test_gfal_chmod(self):
        assert _command_from_argv0("gfal-chmod") == "chmod"

    def test_gfal_sum(self):
        assert _command_from_argv0("gfal-sum") == "sum"

    def test_gfal_xattr(self):
        assert _command_from_argv0("gfal-xattr") == "xattr"

    def test_full_path(self):
        """Full path like /usr/local/bin/gfal-ls should still work."""
        assert _command_from_argv0("/usr/local/bin/gfal-ls") == "ls"

    def test_case_insensitive(self):
        assert _command_from_argv0("gfal-LS") == "ls"


# ---------------------------------------------------------------------------
# _find_command
# ---------------------------------------------------------------------------


class TestFindCommand:
    def test_known_command(self):
        cls, method = _find_command("ls")
        assert method.__name__ == "execute_ls"

    def test_copy_command(self):
        cls, method = _find_command("copy")
        assert method.__name__ == "execute_copy"

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown command"):
            _find_command("nonexistent_command")


# ---------------------------------------------------------------------------
# main() via subprocess
# ---------------------------------------------------------------------------


class TestMainEntrypoint:
    def test_version_flag(self):
        from helpers import run_gfal

        # --version exits with 0 and prints version info
        rc, out, err = run_gfal("ls", "--version")
        assert rc == 0
        assert "gfal-cli" in out or "gfal-cli" in err

    def test_unknown_command(self):
        import subprocess
        import sys

        script = (
            "import sys; sys.argv=['gfal-unknown_cmd_xyz']+sys.argv[1:];"
            "from gfal_cli.shell import main; main()"
        )
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "Unknown command" in proc.stderr
