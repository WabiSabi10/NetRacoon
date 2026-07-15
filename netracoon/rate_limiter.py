"""Rate limiting — etik tarama için hız sınırlama."""

from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    """Saniye başına maksimum istek sayısını sınırlar."""

    def __init__(self, rate: int) -> None:
        self.rate = rate
        self._timestamps: deque[float] = deque()

    async def acquire(self) -> None:
        if self.rate <= 0:
            return

        now = time.monotonic()
        window_start = now - 1.0

        while self._timestamps and self._timestamps[0] < window_start:
            self._timestamps.popleft()

        if len(self._timestamps) >= self.rate:
            sleep_time = self._timestamps[0] + 1.0 - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        self._timestamps.append(time.monotonic())


async def apply_delay(delay: float) -> None:
    """İstekler arası sabit gecikme."""
    if delay > 0:
        await asyncio.sleep(delay)
