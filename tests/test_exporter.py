"""Tests for exporter."""

import csv
import json

import pytest

from netracoon.exporter import save_csv, save_json
from netracoon.port_scanner import PortResult, ScanResult


@pytest.fixture
def sample_results():
    return [
        ScanResult(
            host="192.168.1.1",
            hostname="router.local",
            alive=True,
            os_guess="Linux (TTL=64)",
            ports=[
                PortResult(host="192.168.1.1", port=22, state="open", service="ssh", banner="SSH-2.0"),
                PortResult(host="192.168.1.1", port=80, state="open", service="http", banner="Apache"),
            ],
        ),
        ScanResult(host="192.168.1.2", hostname="", alive=True, ports=[]),
    ]


class TestSaveJson:
    def test_creates_file(self, sample_results, tmp_path):
        path = save_json(sample_results, tmp_path / "out.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["host_count"] == 2
        assert len(data["hosts"][0]["open_ports"]) == 2

    def test_includes_os_guess(self, sample_results, tmp_path):
        path = save_json(sample_results, tmp_path / "out.json")
        data = json.loads(path.read_text())
        assert data["hosts"][0]["os_guess"] == "Linux (TTL=64)"


class TestSaveCsv:
    def test_creates_file(self, sample_results, tmp_path):
        path = save_csv(sample_results, tmp_path / "out.csv")
        assert path.exists()
        with path.open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 3  # 2 ports + 1 empty host

    def test_headers(self, sample_results, tmp_path):
        path = save_csv(sample_results, tmp_path / "out.csv")
        with path.open() as f:
            reader = csv.DictReader(f)
            assert "os_guess" in reader.fieldnames
