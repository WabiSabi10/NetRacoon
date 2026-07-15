"""Tests for banner module."""

from unittest.mock import MagicMock, patch

from netracoon.banner import _clean_banner, grab_banner


class TestCleanBanner:
    def test_empty(self):
        assert _clean_banner(b"") == ""

    def test_strips_control_chars(self):
        assert _clean_banner(b"Hello\x00World") == "HelloWorld"

    def test_truncates_long(self):
        long_data = b"x" * 300
        assert len(_clean_banner(long_data)) == 200

    def test_normalizes_newlines(self):
        assert "line1 line2" in _clean_banner(b"line1\r\nline2")


class TestGrabBanner:
    def test_unsupported_port(self):
        assert grab_banner("127.0.0.1", 9999) == ""

    @patch("netracoon.banner._grab_plain", return_value="SSH-2.0")
    def test_ssh_port(self, mock_plain):
        assert grab_banner("127.0.0.1", 22) == "SSH-2.0"

    @patch("netracoon.banner._grab_tls", return_value="HTTP/1.1")
    def test_https_port(self, mock_tls):
        assert grab_banner("127.0.0.1", 443) == "HTTP/1.1"

    @patch("netracoon.banner.socket.socket")
    def test_grab_plain(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"220 mail.example.com"
        mock_socket_cls.return_value = mock_sock
        from netracoon.banner import _grab_plain

        result = _grab_plain("127.0.0.1", 25, 1.0)
        assert "mail.example.com" in result
