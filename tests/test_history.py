"""Tests for history module."""

from netracoon.history import compare_scans

SAMPLE_PREVIOUS = {
    "hosts": [
        {"host": "10.0.0.1", "open_ports": [{"port": 22}, {"port": 80}]},
        {"host": "10.0.0.2", "open_ports": [{"port": 443}]},
    ]
}

SAMPLE_CURRENT = {
    "hosts": [
        {"host": "10.0.0.1", "open_ports": [{"port": 22}, {"port": 443}]},
        {"host": "10.0.0.3", "open_ports": [{"port": 80}]},
    ]
}


class TestCompareScans:
    def test_new_ports(self):
        diff = compare_scans(SAMPLE_CURRENT, SAMPLE_PREVIOUS)
        assert 443 in diff["new_ports"]["10.0.0.1"]
        assert 80 in diff["closed_ports"]["10.0.0.1"]

    def test_new_hosts(self):
        diff = compare_scans(SAMPLE_CURRENT, SAMPLE_PREVIOUS)
        assert "10.0.0.3" in diff["new_hosts"]
        assert "10.0.0.2" in diff["removed_hosts"]

    def test_no_diff(self):
        diff = compare_scans(SAMPLE_PREVIOUS, SAMPLE_PREVIOUS)
        assert diff["new_hosts"] == []
        assert diff["removed_hosts"] == []
        assert diff["new_ports"] == {}
        assert diff["closed_ports"] == {}
