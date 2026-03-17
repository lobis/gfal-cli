"""Tests for gfal_cli.progress — Progress bar unit tests."""

from gfal_cli.progress import Progress


class TestProgressInit:
    def test_initial_state(self):
        p = Progress("test")
        assert p.label == "test"
        assert not p.started
        assert not p.stopped
        assert p.status is None

    def test_update_sets_status(self):
        p = Progress("test")
        p.update(curr_size=1024, total_size=2048)
        assert p.status is not None
        assert p.status["curr_size"] == 1024
        assert p.status["total_size"] == 2048

    def test_update_computes_percentage(self):
        p = Progress("test")
        p.update(curr_size=500, total_size=1000, elapsed=1.0)
        assert p.status["percentage"] == 50.0
        assert p.status["rate"] == 500.0

    def test_update_zero_elapsed(self):
        p = Progress("test")
        p.update(curr_size=500, total_size=1000, elapsed=0)
        assert "percentage" not in p.status

    def test_stop_without_start(self):
        """stop() on never-started Progress should be harmless."""
        p = Progress("test")
        p.stop(True)  # Should not raise


class TestProgressRateStr:
    def test_bytes_per_second(self):
        assert Progress._rate_str(100) == "100B/s"

    def test_kilobytes(self):
        result = Progress._rate_str(1024)
        assert "K" in result
        assert "/s" in result

    def test_megabytes(self):
        result = Progress._rate_str(1024 * 1024)
        assert "M" in result

    def test_gigabytes(self):
        result = Progress._rate_str(1024**3)
        assert "G" in result


class TestProgressSizeStr:
    def test_bytes(self):
        result = Progress._size_str(100)
        assert "B" in result
        assert "/s" not in result

    def test_kilobytes(self):
        result = Progress._size_str(1024)
        assert "KB" in result or "K" in result
