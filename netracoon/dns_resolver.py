"""Hostname çözümleme (DNS)."""

from __future__ import annotations

import ipaddress
import socket


def resolve_forward(hostname: str) -> str:
    """Hostname → IP (A kaydı)."""
    try:
        return socket.gethostbyname(hostname)
    except (socket.gaierror, OSError):
        return ""


def resolve_reverse(ip: str) -> str:
    """IP → hostname (PTR kaydı)."""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror, OSError):
        return ""


def resolve_target(target: str) -> tuple[str, str]:
    """Hedefi IP ve hostname olarak çözümler.

    Returns:
        (ip, hostname) — çözümlenemeyen alan boş string olur.
    """
    try:
        ipaddress.ip_address(target)
        ip = target
        hostname = resolve_reverse(ip)
        return ip, hostname
    except ValueError:
        ip = resolve_forward(target)
        return ip, target if ip else ""
