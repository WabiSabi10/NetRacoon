"""Tests for port scanner."""

from unittest.mock import MagicMock, patch

from netracoon.port_scanner import PortResult, scan_port, scan_ports


class TestScanPort:
    @patch("netracoon.port_scanner.socket.socket")
    def test_open_port(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket_cls.return_value = mock_sock

        result = scan_port("127.0.0.1", 80)
        assert result.state == "open"
        assert result.port == 80

    @patch("netracoon.port_scanner.socket.socket")
    def test_closed_port(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 111
        mock_socket_cls.return_value = mock_sock

        result = scan_port("127.0.0.1", 9999)
        assert result.state == "closed"

    @patch("netracoon.port_scanner.socket.socket")
    def test_filtered_port(self, mock_socket_cls):
        import socket

        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = socket.timeout()
        mock_socket_cls.return_value = mock_sock

        result = scan_port("127.0.0.1", 443)
        assert result.state == "filtered"


class TestScanPorts:
    @patch("netracoon.port_scanner.scan_port")
    def test_returns_only_open(self, mock_scan):
        mock_scan.side_effect = [
            PortResult(host="127.0.0.1", port=22, state="open"),
            PortResult(host="127.0.0.1", port=80, state="closed"),
            PortResult(host="127.0.0.1", port=443, state="open"),
        ]
        results = scan_ports("127.0.0.1", [22, 80, 443], workers=3)
        assert len(results) == 2
        assert results[0].port == 22
        assert results[1].port == 443

    @patch("netracoon.port_scanner.scan_port")
    def test_callback(self, mock_scan):
        mock_scan.return_value = PortResult(host="127.0.0.1", port=22, state="open")
        seen = []
        scan_ports("127.0.0.1", [22], on_result=lambda r: seen.append(r))
        assert len(seen) == 1
