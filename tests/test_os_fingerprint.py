"""Tests for OS fingerprint."""

from unittest.mock import patch

from netracoon.os_fingerprint import fingerprint_os, get_ttl, guess_os_from_ttl


class TestGuessOsFromTtl:
    def test_linux(self):
        assert "Linux" in guess_os_from_ttl(64)

    def test_windows(self):
        assert "Windows" in guess_os_from_ttl(128)

    def test_cisco(self):
        assert "Cisco" in guess_os_from_ttl(255)

    def test_unknown(self):
        assert guess_os_from_ttl(42) == "Unknown"


class TestGetTtl:
    @patch("netracoon.os_fingerprint.subprocess.run")
    def test_parses_ttl(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "64 bytes from 8.8.8.8: ttl=64"
        assert get_ttl("8.8.8.8") == 64

    @patch("netracoon.os_fingerprint.subprocess.run")
    def test_failed_ping(self, mock_run):
        mock_run.return_value.returncode = 1
        assert get_ttl("8.8.8.8") is None


class TestFingerprintOs:
    @patch("netracoon.os_fingerprint.get_ttl", return_value=64)
    def test_with_ttl(self, mock_ttl):
        result = fingerprint_os("8.8.8.8")
        assert "Linux" in result
        assert "TTL=64" in result

    @patch("netracoon.os_fingerprint.get_ttl", return_value=None)
    def test_unknown(self, mock_ttl):
        assert fingerprint_os("8.8.8.8") == "Unknown"
