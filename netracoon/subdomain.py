"""Subdomain keşfi — wordlist ile DNS brute-force."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

DEFAULT_WORDLIST = Path(__file__).parent / "data" / "subdomains.txt"


def load_wordlist(path: str | Path | None = None) -> list[str]:
    """Subdomain wordlist dosyasını yükler."""
    wordlist_path = Path(path) if path else DEFAULT_WORDLIST
    if not wordlist_path.exists():
        return _builtin_wordlist()

    with wordlist_path.open(encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def _builtin_wordlist() -> list[str]:
    return [
        "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
        "dns", "dns1", "dns2", "api", "dev", "staging", "test", "admin", "portal",
        "vpn", "remote", "blog", "shop", "store", "cdn", "static", "media", "img",
        "images", "secure", "login", "auth", "sso", "git", "gitlab", "jenkins",
        "ci", "db", "mysql", "postgres", "redis", "mongo", "elastic", "kibana",
        "grafana", "prometheus", "monitor", "status", "support", "help", "docs",
        "wiki", "beta", "alpha", "demo", "sandbox", "m", "mobile", "app", "apps",
    ]


def discover_subdomains(
    domain: str,
    wordlist: list[str] | None = None,
    workers: int = 20,
    on_result: Callable[[str, str], None] | None = None,
) -> list[str]:
    """Wordlist kullanarak subdomain keşfi yapar."""
    words = wordlist or load_wordlist()
    found: list[str] = []

    def _check(word: str) -> tuple[str, str] | None:
        subdomain = f"{word}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            return subdomain, ip
        except socket.gaierror:
            return None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_check, w): w for w in words}
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception:
                continue
            if result:
                subdomain, ip = result
                if on_result:
                    on_result(subdomain, ip)
                found.append(subdomain)

    return sorted(found)
