"""Tests for async scanner."""

from unittest.mock import AsyncMock, patch

import pytest

from netracoon.async_scanner import scan_port_async, scan_ports_async
from netracoon.port_scanner import PortResult


@pytest.mark.asyncio
class TestScanPortAsync:
    async def test_open_port(self):
        mock_writer = AsyncMock()
        mock_writer.wait_closed = AsyncMock()

        with patch("netracoon.async_scanner.asyncio.open_connection", return_value=(None, mock_writer)):
            result = await scan_port_async("127.0.0.1", 80, timeout=1.0)
        assert result.state == "open"

    async def test_closed_port(self):
        with patch("netracoon.async_scanner.asyncio.open_connection", side_effect=ConnectionRefusedError):
            result = await scan_port_async("127.0.0.1", 9999, timeout=1.0)
        assert result.state == "closed"

    async def test_filtered_port(self):
        import asyncio

        with patch("netracoon.async_scanner.asyncio.open_connection", side_effect=asyncio.TimeoutError):
            result = await scan_port_async("127.0.0.1", 443, timeout=1.0)
        assert result.state == "filtered"


@pytest.mark.asyncio
class TestScanPortsAsync:
    async def test_scan_multiple(self):
        with patch("netracoon.async_scanner.scan_port_async") as mock_scan:
            mock_scan.side_effect = [
                PortResult(host="127.0.0.1", port=22, state="open"),
                PortResult(host="127.0.0.1", port=80, state="closed"),
            ]
            results = await scan_ports_async("127.0.0.1", [22, 80], workers=2)
        assert len(results) == 1
        assert results[0].port == 22
