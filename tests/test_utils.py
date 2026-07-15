"""Tests for utils module."""


from netracoon.utils import TOP_PORTS, expand_targets, parse_ports


class TestExpandTargets:
    def test_single_ip(self):
        assert expand_targets("192.168.1.1") == ["192.168.1.1"]

    def test_single_hostname(self):
        assert expand_targets("example.com") == ["example.com"]

    def test_cidr_small(self):
        result = expand_targets("10.0.0.0/30")
        assert "10.0.0.1" in result
        assert "10.0.0.2" in result
        assert len(result) == 2

    def test_range_short(self):
        result = expand_targets("192.168.1.1-3")
        assert result == ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

    def test_range_full(self):
        result = expand_targets("192.168.1.10-192.168.1.12")
        assert len(result) == 3
        assert result[0] == "192.168.1.10"

    def test_range_reversed(self):
        result = expand_targets("192.168.1.5-3")
        assert result[0] == "192.168.1.3"
        assert result[-1] == "192.168.1.5"


class TestParsePorts:
    def test_top_ports(self):
        result = parse_ports("top")
        assert result == sorted(TOP_PORTS)

    def test_single_port(self):
        assert parse_ports("22") == [22]

    def test_multiple_ports(self):
        assert parse_ports("22,80,443") == [22, 80, 443]

    def test_port_range(self):
        result = parse_ports("20-22")
        assert result == [20, 21, 22]

    def test_mixed(self):
        result = parse_ports("22,80-82")
        assert 22 in result
        assert 80 in result
        assert 81 in result
        assert 82 in result
