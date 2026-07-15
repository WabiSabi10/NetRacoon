"""Sonuçları JSON/CSV olarak kaydetme."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from netracoon.port_scanner import ScanResult


def _serialize_results(results: list[ScanResult]) -> dict[str, Any]:
    return {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "host_count": len(results),
        "hosts": [
            {
                "host": r.host,
                "hostname": r.hostname,
                "alive": r.alive,
                "os_guess": r.os_guess,
                "traceroute": r.traceroute,
                "subdomains": r.subdomains,
                "open_ports": [
                    {
                        "port": p.port,
                        "state": p.state,
                        "service": p.service,
                        "banner": p.banner,
                    }
                    for p in r.ports
                ],
            }
            for r in results
        ],
    }


def save_json(results: list[ScanResult], path: str | Path) -> Path:
    """Tarama sonuçlarını JSON dosyasına yazar."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(_serialize_results(results), f, indent=2, ensure_ascii=False)
    return output


def save_csv(results: list[ScanResult], path: str | Path) -> Path:
    """Tarama sonuçlarını CSV dosyasına yazar."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "host", "hostname", "alive", "os_guess",
        "port", "state", "service", "banner",
    ]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            if not result.ports:
                writer.writerow({
                    "host": result.host,
                    "hostname": result.hostname,
                    "alive": result.alive,
                    "os_guess": result.os_guess,
                    "port": "",
                    "state": "",
                    "service": "",
                    "banner": "",
                })
            else:
                for port in result.ports:
                    writer.writerow({
                        "host": result.host,
                        "hostname": result.hostname,
                        "alive": result.alive,
                        "os_guess": result.os_guess,
                        "port": port.port,
                        "state": port.state,
                        "service": port.service,
                        "banner": port.banner,
                    })
    return output
