"""Tarama profilleri — quick, deep, stealth."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScanProfile:
    name: str
    ports: str
    timeout: float
    workers: int
    grab_banners: bool
    delay: float
    rate: int
    ping: bool


PROFILES: dict[str, ScanProfile] = {
    "quick": ScanProfile(
        name="quick",
        ports="top",
        timeout=0.5,
        workers=200,
        grab_banners=False,
        delay=0.0,
        rate=0,
        ping=False,
    ),
    "deep": ScanProfile(
        name="deep",
        ports="1-1024",
        timeout=2.0,
        workers=300,
        grab_banners=True,
        delay=0.0,
        rate=0,
        ping=True,
    ),
    "stealth": ScanProfile(
        name="stealth",
        ports="top",
        timeout=3.0,
        workers=10,
        grab_banners=True,
        delay=0.5,
        rate=10,
        ping=True,
    ),
}


def get_profile(name: str) -> ScanProfile:
    """Profil adından ScanProfile döndürür."""
    key = name.lower().strip()
    if key not in PROFILES:
        available = ", ".join(PROFILES)
        raise ValueError(f"Bilinmeyen profil: {name!r}. Mevcut: {available}")
    return PROFILES[key]


def apply_profile(config_dict: dict[str, Any], profile_name: str) -> dict[str, Any]:
    """Profil ayarlarını config sözlüğüne uygular (CLI override'ları korur)."""
    profile = get_profile(profile_name)
    defaults = {
        "ports": profile.ports,
        "timeout": profile.timeout,
        "workers": profile.workers,
        "grab_banners": profile.grab_banners,
        "delay": profile.delay,
        "rate": profile.rate,
        "ping": profile.ping,
        "profile": profile.name,
    }
    merged = {**defaults, **{k: v for k, v in config_dict.items() if v is not None}}
    return merged
