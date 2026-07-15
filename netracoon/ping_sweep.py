"""Ping sweep — canlı host keşfi."""

from __future__ import annotations

import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable


def ping_host(host: str, timeout: float = 1.0) -> bool:
    """Tek bir hosta ICMP ping gönderir."""
    system = platform.system().lower()
    timeout_ms = max(int(timeout * 1000), 500)

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
    elif system == "darwin":
        cmd = ["ping", "-c", "1", "-W", str(max(int(timeout * 1000), 1000)), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(int(timeout), 1)), host]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def ping_sweep(
    hosts: list[str],
    timeout: float = 1.0,
    workers: int = 50,
    on_result: Callable[[str, bool], None] | None = None,
) -> list[str]:
    """Verilen host listesinde ping sweep yapar, canlı olanları döndürür."""
    alive: list[str] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(ping_host, h, timeout): h for h in hosts}
        for future in as_completed(futures):
            host = futures[future]
            try:
                is_alive = future.result()
            except Exception:
                is_alive = False

            if on_result:
                on_result(host, is_alive)
            if is_alive:
                alive.append(host)

    return sorted(alive, key=_sort_key)


def _sort_key(host: str) -> tuple:
    """IP adreslerini sayısal sıralamak için."""
    try:
        parts = [int(p) for p in host.split(".")]
        return tuple(parts)
    except ValueError:
        return (999, 999, 999, 999, host)
