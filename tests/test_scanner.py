"""Tests for scanner orchestration."""

from unittest.mock import patch

from netracoon.port_scanner import PortResult, ScanResult
from netracoon.scanner import (
    ScanConfig,
    _export_results,
    _extract_domain,
    _run_ping_sweep,
    _run_port_scans,
    _show_diff,
    run_scan,
)


def _fake_ping_sweep(targets, timeout, workers, on_result):
    for host in targets:
        on_result(host, host == "192.168.1.1")


class TestExtractDomain:
    def test_subdomain(self):
        assert _extract_domain("www.example.com") == "example.com"

    def test_short(self):
        assert _extract_domain("localhost") == "localhost"


class TestRunPortScans:
    @patch("netracoon.scanner.get_service_name", return_value="http")
    @patch("netracoon.scanner.banner_mod.grab_banner", return_value="Apache")
    @patch("netracoon.scanner._scan_host_ports")
    @patch("netracoon.scanner.resolve_reverse", return_value="host.local")
    @patch("netracoon.scanner.resolve_target", return_value=("192.168.1.1", "host.local"))
    def test_basic_scan(self, mock_resolve, mock_reverse, mock_scan, mock_banner, mock_svc):
        mock_scan.return_value = [
            PortResult(host="192.168.1.1", port=80, state="open"),
        ]
        config = ScanConfig(target="192.168.1.1", grab_banners=True, use_async=True)
        results = _run_port_scans(["192.168.1.1"], [80], config)
        assert len(results) == 1
        assert results[0].ports[0].service == "http"
        assert results[0].ports[0].banner == "Apache"

    @patch("netracoon.scanner.discover_subdomains", return_value=["www.example.com"])
    @patch("netracoon.scanner.run_traceroute", return_value=["10.0.0.1", "8.8.8.8"])
    @patch("netracoon.scanner.fingerprint_os", return_value="Linux (TTL=64)")
    @patch("netracoon.scanner._scan_host_ports", return_value=[])
    @patch("netracoon.scanner.resolve_target", return_value=("8.8.8.8", "dns.google"))
    def test_advanced_modules(self, mock_resolve, mock_scan, mock_fp, mock_trace, mock_subs):
        config = ScanConfig(
            target="dns.google",
            os_fingerprint=True,
            traceroute=True,
            subdomains=True,
        )
        results = _run_port_scans(["dns.google"], [53], config)
        assert results[0].os_guess == "Linux (TTL=64)"
        assert len(results[0].traceroute) == 2
        assert "www.example.com" in results[0].subdomains


class TestPingSweep:
    @patch("netracoon.scanner.ping_sweep", side_effect=_fake_ping_sweep)
    @patch("netracoon.scanner.display.print_alive_hosts")
    def test_ping_sweep(self, mock_print, mock_ping):
        config = ScanConfig(target="192.168.1.0/24", verbose=False)
        alive = _run_ping_sweep(["192.168.1.1", "192.168.1.2"], config)
        assert alive == ["192.168.1.1"]


class TestExportAndDiff:
    def test_export_json(self, tmp_path):
        results = [ScanResult(host="10.0.0.1", ports=[])]
        config = ScanConfig(target="10.0.0.1", output_json=str(tmp_path / "out.json"))
        _export_results(results, config, 1.0)
        assert (tmp_path / "out.json").exists()

    @patch("netracoon.scanner.display.print_diff")
    @patch("netracoon.scanner.load_history", return_value={"hosts": []})
    def test_show_diff(self, mock_load, mock_print_diff):
        _show_diff([], "previous.json")
        mock_print_diff.assert_called_once()


class TestRunScan:
    @patch("netracoon.scanner._export_results")
    @patch("netracoon.scanner._run_port_scans")
    @patch("netracoon.scanner.expand_targets", return_value=["127.0.0.1"])
    @patch("netracoon.scanner.parse_ports", return_value=[80])
    @patch("netracoon.scanner.setup_logging")
    @patch("netracoon.scanner.display.print_banner")
    @patch("netracoon.scanner.display.print_scan_results")
    @patch("netracoon.scanner.display.print_summary")
    def test_full_scan_flow(
        self, mock_summary, mock_results, mock_banner, mock_log,
        mock_ports, mock_expand, mock_port_scans, mock_export,
    ):
        mock_port_scans.return_value = [
            ScanResult(host="127.0.0.1", ports=[
                PortResult(host="127.0.0.1", port=80, state="open", service="http"),
            ]),
        ]
        config = ScanConfig(target="127.0.0.1", ports="80")
        report = run_scan(config)
        assert report.elapsed >= 0
        assert len(report.results) == 1
