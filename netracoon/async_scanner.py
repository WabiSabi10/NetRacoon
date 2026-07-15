"""Asyncio tabanlı TCP port tarayıcı."""

from __future__ import annotations

import asyncio
from typing import Callable

from netracoon.port_scanner import PortResult
from netracoon.rate_limiter import RateLimiter, apply_delay


async def scan_port_async(
    host: str,
    port: int,
    timeout: float,
    limiter: RateLimiter | None = None,
    delay: float = 0.0,
) -> PortResult:
    """Tek bir TCP portunu asyncio ile tarar."""
    if limiter:
        await limiter.acquire()
    await apply_delay(delay)

    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return PortResult(host=host, port=port, state="open")
    except asyncio.TimeoutError:
        return PortResult(host=host, port=port, state="filtered")
    except (ConnectionRefusedError, OSError):
        return PortResult(host=host, port=port, state="closed")
    except Exception:
        return PortResult(host=host, port=port, state="filtered")


async def scan_ports_async(
    host: str,
    ports: list[int],
    timeout: float = 1.0,
    workers: int = 100,
    rate: int = 0,
    delay: float = 0.0,
    on_result: Callable[[PortResult], None] | None = None,
) -> list[PortResult]:
    """Bir host üzerindeki portları asyncio ile eşzamanlı tarar."""
    semaphore = asyncio.Semaphore(workers)
    limiter = RateLimiter(rate) if rate > 0 else None
    open_ports: list[PortResult] = []

    async def _scan(port: int) -> PortResult:
        async with semaphore:
            return await scan_port_async(host, port, timeout, limiter, delay)

    tasks = [asyncio.create_task(_scan(port)) for port in ports]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        if on_result:
            on_result(result)
        if result.state == "open":
            open_ports.append(result)

    return sorted(open_ports, key=lambda r: r.port)
