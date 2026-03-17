"""Tests for base.py: surl type converter, @arg decorator, CommandBase."""

from pathlib import Path
from urllib.parse import urlparse

from gfal_cli.base import CommandBase, arg, surl

# ---------------------------------------------------------------------------
# surl() type converter
# ---------------------------------------------------------------------------


class TestSurl:
    def test_bare_path_becomes_file_url(self, tmp_path):
        f = tmp_path / "foo.txt"
        result = surl(str(f))
        assert result.startswith("file://")
        assert str(f) in result

    def test_bare_relative_path_becomes_absolute(self):
        result = surl("some/relative/path.txt")
        parsed = urlparse(result)
        assert parsed.scheme == "file"
        assert Path(parsed.path).is_absolute()

    def test_file_url_unchanged(self):
        url = "file:///tmp/foo.txt"
        assert surl(url) == url

    def test_http_url_unchanged(self):
        url = "http://example.com/file"
        assert surl(url) == url

    def test_https_url_unchanged(self):
        url = "https://example.com/file"
        assert surl(url) == url

    def test_root_url_unchanged(self):
        url = "root://eosuser.cern.ch//eos/user/file"
        assert surl(url) == url

    def test_dash_sentinel_unchanged(self):
        assert surl("-") == "-"


# ---------------------------------------------------------------------------
# @arg decorator
# ---------------------------------------------------------------------------


class TestArgDecorator:
    def test_attaches_arguments(self):
        @arg("--foo", type=str)
        @arg("--bar", action="store_true")
        def my_func(self):
            pass

        assert hasattr(my_func, "arguments")
        assert len(my_func.arguments) == 2

    def test_argument_order_preserved(self):
        """Arguments are stored in the order decorators execute (outermost first)."""

        @arg("--second")
        @arg("--first")
        def my_func(self):
            pass

        # @arg("--first") runs first (inner), inserts at 0 → ["--first"]
        # @arg("--second") runs second (outer), inserts at 0 → ["--second", "--first"]
        args = [a[0][0] for a in my_func.arguments]
        assert args == ["--second", "--first"]

    def test_no_duplicate_arguments(self):
        @arg("--foo", type=str)
        @arg("--foo", type=str)
        def my_func(self):
            pass

        assert len(my_func.arguments) == 1


# ---------------------------------------------------------------------------
# CommandBase
# ---------------------------------------------------------------------------


class TestCommandBase:
    def test_initial_return_code(self):
        cb = CommandBase()
        assert cb.return_code == -1

    def test_get_subclasses_non_empty(self):
        """At least GfalCommands, CommandCopy, CommandLs, CommandRm exist."""
        subs = CommandBase.get_subclasses()
        assert len(subs) >= 4

    def test_common_args_present(self, tmp_path):
        """All commands should accept -v, -t, -E, --key, --log-file, --no-verify."""
        from helpers import run_gfal

        f = tmp_path / "test.txt"
        f.write_text("x")

        # -v should not cause an error
        rc, out, err = run_gfal("stat", "-v", f.as_uri())
        assert rc == 0

    def test_timeout_arg(self, tmp_path):
        from helpers import run_gfal

        f = tmp_path / "test.txt"
        f.write_text("x")
        rc, out, err = run_gfal("stat", "-t", "10", f.as_uri())
        assert rc == 0

    def test_verbose_levels(self, tmp_path):
        from helpers import run_gfal

        f = tmp_path / "test.txt"
        f.write_text("x")
        # -vvv should work (debug level)
        rc, out, err = run_gfal("stat", "-vvv", f.as_uri())
        assert rc == 0

    def test_log_file(self, tmp_path):
        from helpers import run_gfal

        f = tmp_path / "test.txt"
        f.write_text("x")
        log = tmp_path / "test.log"
        rc, out, err = run_gfal("stat", "-vvv", "--log-file", str(log), f.as_uri())
        assert rc == 0
        # Log file should exist (may or may not have content depending on log level)
        assert log.exists()
