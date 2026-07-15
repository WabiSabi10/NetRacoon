"""Tests for rate limiter."""

import time

import pytest

from netracoon.rate_limiter import RateLimiter, apply_delay


@pytest.mark.asyncio
class TestRateLimiter:
    async def test_no_limit_when_zero(self):
        limiter = RateLimiter(0)
        start = time.monotonic()
        await limiter.acquire()
        await limiter.acquire()
        assert time.monotonic() - start < 0.1

    async def test_delay_applied(self):
        start = time.monotonic()
        await apply_delay(0.05)
        assert time.monotonic() - start >= 0.04

    async def test_no_delay_when_zero(self):
        start = time.monotonic()
        await apply_delay(0)
        assert time.monotonic() - start < 0.05

    async def test_rate_limit_waits(self):
        limiter = RateLimiter(1)
        await limiter.acquire()
        start = time.monotonic()
        await limiter.acquire()
        assert time.monotonic() - start >= 0.5
