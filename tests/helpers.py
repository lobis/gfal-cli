"""Shared test helpers for gfal-cli tests."""

import subprocess
import sys


def run_gfal(cmd, *args, input=None):
    """
    Run ``gfal-<cmd>`` in a subprocess via the current Python interpreter.

    Returns ``(returncode, stdout, stderr)`` as strings.

    Args are passed as separate argv elements so paths with spaces are safe.
    ``input`` may be a str piped to stdin (useful for gfal-save).
    """
    script = (
        f"import sys; sys.argv=['gfal-{cmd}']+sys.argv[1:];"
        "from gfal_cli.shell import main; main()"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, *[str(a) for a in args]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        input=input,
    )
    return proc.returncode, proc.stdout, proc.stderr
