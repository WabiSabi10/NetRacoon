"""Tarama geçmişi ve karşılaştırma."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

HISTORY_DIR = Path.home() / ".netracoon" / "history"


def save_to_history(results_data: dict[str, Any], scan_id: str | None = None) -> Path:
    """Tarama sonucunu geçmişe kaydeder."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    scan_id = scan_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = HISTORY_DIR / f"scan_{scan_id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    return path


def load_history(path: str | Path) -> dict[str, Any]:
    """Geçmiş tarama dosyasını yükler."""
    with Path(path).open(encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def list_history() -> list[Path]:
    """Kayıtlı tarama dosyalarını listeler."""
    if not HISTORY_DIR.exists():
        return []
    return sorted(HISTORY_DIR.glob("scan_*.json"), reverse=True)


def compare_scans(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    """İki tarama sonucunu karşılaştırır."""
    def _port_set(data: dict[str, Any]) -> dict[str, set[int]]:
        result: dict[str, set[int]] = {}
        for host in data.get("hosts", []):
            ip = host["host"]
            ports = {p["port"] for p in host.get("open_ports", [])}
            result[ip] = ports
        return result

    current_ports = _port_set(current)
    previous_ports = _port_set(previous)

    diff: dict[str, Any] = {
        "new_hosts": [],
        "removed_hosts": [],
        "new_ports": {},
        "closed_ports": {},
    }

    all_hosts = set(current_ports) | set(previous_ports)

    for host in all_hosts:
        curr = current_ports.get(host, set())
        prev = previous_ports.get(host, set())

        if host not in previous_ports:
            diff["new_hosts"].append(host)
        elif host not in current_ports:
            diff["removed_hosts"].append(host)

        new = curr - prev
        closed = prev - curr
        if new:
            diff["new_ports"][host] = sorted(new)
        if closed:
            diff["closed_ports"][host] = sorted(closed)

    return diff
