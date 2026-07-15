"""Traceroute — ağ yolu keşfi."""

from __future__ import annotations

import platform
import re
import subprocess


def traceroute(host: str, max_hops: int = 30, timeout: float = 2.0) -> list[str]:
    """Hedefe giden ağ yolunu döndürür."""
    system = platform.system().lower()

    if system == "windows":
        cmd = ["tracert", "-d", "-h", str(max_hops), "-w", str(int(timeout * 1000)), host]
    else:
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", str(int(timeout)), host]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=max_hops * timeout + 10,
        )
        return _parse_traceroute_output(result.stdout, system)
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return []


def _parse_traceroute_output(output: str, system: str) -> list[str]:
    """Traceroute çıktısını hop listesine çevirir."""
    hops: list[str] = []

    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("traceroute") or line.startswith("Tracing"):
            continue

        if system == "windows":
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s*$", line)
            if match:
                hops.append(match.group(1))
        else:
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[1]
                if re.match(r"\d+\.\d+\.\d+\.\d+", ip):
                    hops.append(ip)

    return hops
