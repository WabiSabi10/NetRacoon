"""TCP port tarayıcı."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PortResult:
    host: str
    port: int
    state: str  # "open" | "closed" | "filtered"
    service: str = ""
    banner: str = ""


@dataclass
class ScanResult:
    host: str
    hostname: str = ""
    ports: list[PortResult] = field(default_factory=list)
    alive: bool = True
    os_guess: str = ""
    traceroute: list[str] = field(default_factory=list)
    subdomains: list[str] = field(default_factory=list)


def scan_port(host: str, port: int, timeout: float = 1.0) -> PortResult:
    """Tek bir TCP portunu tarar."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            return PortResult(host=host, port=port, state="open")
        return PortResult(host=host, port=port, state="closed")
    except socket.timeout:
        return PortResult(host=host, port=port, state="filtered")
    except OSError:
        return PortResult(host=host, port=port, state="filtered")
    finally:
        sock.close()


def scan_ports(
    host: str,
    ports: list[int],
    timeout: float = 1.0,
    workers: int = 100,
    on_result: Callable[[PortResult], None] | None = None,
) -> list[PortResult]:
    """Bir host üzerindeki portları eşzamanlı tarar."""
    results: list[PortResult] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(scan_port, host, port, timeout): port for port in ports
        }
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception:
                port = futures[future]
                result = PortResult(host=host, port=port, state="filtered")

            if on_result:
                on_result(result)
            if result.state == "open":
                results.append(result)

    return sorted(results, key=lambda r: r.port)
