"""Tests for HTML exporter."""

from netracoon.html_exporter import save_html
from netracoon.port_scanner import PortResult, ScanResult


class TestSaveHtml:
    def test_creates_html_file(self, tmp_path):
        results = [
            ScanResult(
                host="10.0.0.1",
                hostname="test.local",
                os_guess="Linux (TTL=64)",
                traceroute=["10.0.0.1", "10.0.0.5"],
                subdomains=["www.test.local"],
                ports=[
                    PortResult(host="10.0.0.1", port=443, state="open", service="https", banner="nginx"),
                ],
            ),
        ]
        path = save_html(results, tmp_path / "report.html", elapsed=1.5)
        content = path.read_text()
        assert "NetRacoon Scan Report" in content
        assert "10.0.0.1" in content
        assert "443" in content
        assert "nginx" in content
        assert "www.test.local" in content
