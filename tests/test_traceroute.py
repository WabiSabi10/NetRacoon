"""Tests for traceroute module."""

from netracoon.traceroute import _parse_traceroute_output


class TestParseTraceroute:
    def test_linux_output(self):
        output = """
traceroute to 8.8.8.8 (8.8.8.8), 30 hops max
 1  192.168.1.1  1.234 ms
 2  10.0.0.1  5.678 ms
 3  8.8.8.8  15.432 ms
"""
        hops = _parse_traceroute_output(output, "linux")
        assert hops == ["192.168.1.1", "10.0.0.1", "8.8.8.8"]

    def test_empty_output(self):
        assert _parse_traceroute_output("", "linux") == []

    def test_windows_output(self):
        output = """
Tracing route to 8.8.8.8
  1     1 ms     1 ms     1 ms  192.168.1.1
  2     5 ms     5 ms     5 ms  10.0.0.1
"""
        hops = _parse_traceroute_output(output, "windows")
        assert "192.168.1.1" in hops
