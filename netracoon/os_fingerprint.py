"""OS fingerprinting — TTL tabanlı işletim sistemi tahmini."""

from __future__ import annotations

import platform
import re
import subprocess

TTL_OS_MAP: list[tuple[tuple[int, int], str]] = [
    ((240, 255), "Cisco IOS / Network Device"),
    ((120, 140), "Windows"),
    ((60, 70), "Linux / Unix / macOS"),
    ((200, 220), "Solaris / AIX"),
]


def guess_os_from_ttl(ttl: int) -> str:
    """TTL değerinden işletim sistemi tahmini."""
    for (low, high), os_name in TTL_OS_MAP:
        if low <= ttl <= high:
            return os_name
    return "Unknown"


def get_ttl(host: str, timeout: float = 2.0) -> int | None:
    """Ping çıktısından TTL değerini okur."""
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), host]
    elif system == "darwin":
        cmd = ["ping", "-c", "1", "-W", str(max(int(timeout * 1000), 1000)), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(int(timeout), 1)), host]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 1,
        )
        if result.returncode != 0:
            return None

        output = result.stdout
        patterns = [
            r"ttl=(\d+)",
            r"TTL=(\d+)",
            r"ttl\s*=\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None

    return None


def fingerprint_os(host: str, timeout: float = 2.0) -> str:
    """Host için OS fingerprint döndürür."""
    ttl = get_ttl(host, timeout)
    if ttl is None:
        return "Unknown"
    return f"{guess_os_from_ttl(ttl)} (TTL={ttl})"
