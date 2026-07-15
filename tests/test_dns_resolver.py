"""Tests for DNS resolver."""

from unittest.mock import patch

from netracoon.dns_resolver import resolve_forward, resolve_reverse, resolve_target


class TestResolveForward:
    @patch("netracoon.dns_resolver.socket.gethostbyname", return_value="93.184.216.34")
    def test_success(self, mock_gethost):
        assert resolve_forward("example.com") == "93.184.216.34"

    @patch("netracoon.dns_resolver.socket.gethostbyname", side_effect=OSError("fail"))
    def test_failure(self, mock_gethost):
        assert resolve_forward("invalid.invalid") == ""


class TestResolveReverse:
    @patch("netracoon.dns_resolver.socket.gethostbyaddr", return_value=("example.com", [], []))
    def test_success(self, mock_gethost):
        assert resolve_reverse("93.184.216.34") == "example.com"

    @patch("netracoon.dns_resolver.socket.gethostbyaddr", side_effect=OSError("fail"))
    def test_failure(self, mock_gethost):
        assert resolve_reverse("1.2.3.4") == ""


class TestResolveTarget:
    @patch("netracoon.dns_resolver.resolve_reverse", return_value="host.example.com")
    def test_ip_target(self, mock_reverse):
        ip, hostname = resolve_target("192.168.1.1")
        assert ip == "192.168.1.1"
        assert hostname == "host.example.com"

    @patch("netracoon.dns_resolver.resolve_forward", return_value="93.184.216.34")
    def test_hostname_target(self, mock_forward):
        ip, hostname = resolve_target("example.com")
        assert ip == "93.184.216.34"
        assert hostname == "example.com"
