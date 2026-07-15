"""Tests for ping sweep."""

from unittest.mock import patch

from netracoon.ping_sweep import ping_host, ping_sweep


class TestPingHost:
    @patch("netracoon.ping_sweep.subprocess.run")
    def test_alive(self, mock_run):
        mock_run.return_value.returncode = 0
        assert ping_host("127.0.0.1") is True

    @patch("netracoon.ping_sweep.subprocess.run")
    def test_dead(self, mock_run):
        mock_run.return_value.returncode = 1
        assert ping_host("192.168.255.255") is False


class TestPingSweep:
    @patch("netracoon.ping_sweep.ping_host", return_value=True)
    def test_returns_alive(self, mock_ping):
        result = ping_sweep(["10.0.0.1", "10.0.0.2"], workers=2)
        assert len(result) == 2

    @patch("netracoon.ping_sweep.ping_host", return_value=False)
    def test_all_dead(self, mock_ping):
        result = ping_sweep(["10.0.0.1"], workers=1)
        assert result == []
