"""Tests for services module."""

from unittest.mock import patch

from netracoon.services import WELL_KNOWN, get_service_name


class TestGetServiceName:
    def test_well_known_port(self):
        assert get_service_name(22) == "ssh" or get_service_name(22) == WELL_KNOWN.get(22, "ssh")

    def test_unknown_port(self):
        with patch("netracoon.services.socket.getservbyport", side_effect=OSError):
            assert get_service_name(9999) == "unknown"

    def test_http_port(self):
        name = get_service_name(80)
        assert name in ("http", "www", "www-http")
