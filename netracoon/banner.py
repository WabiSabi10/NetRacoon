"""Banner grabbing — açık portlardan servis bilgisi okuma."""

from __future__ import annotations

import re
import socket
import ssl

BANNER_PORTS = {21, 22, 23, 25, 80, 110, 143, 443, 445, 587, 993, 995, 3306, 8080, 8443}

# Port bazlı probe mesajları
PROBES: dict[int, bytes] = {
    80: b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n",
    8080: b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n",
    25: b"EHLO scanner\r\n",
    587: b"EHLO scanner\r\n",
}


def grab_banner(host: str, port: int, timeout: float = 2.0) -> str:
    """Açık bir porttan banner okumaya çalışır."""
    if port not in BANNER_PORTS:
        return ""

    try:
        if port in (443, 8443, 993, 995, 465):
            return _grab_tls(host, port, timeout)
        return _grab_plain(host, port, timeout)
    except Exception:
        return ""


def _grab_plain(host: str, port: int, timeout: float) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        probe = PROBES.get(port)
        if probe:
            sock.sendall(probe)
        data = sock.recv(1024)
        return _clean_banner(data)
    finally:
        sock.close()


def _grab_tls(host: str, port: int, timeout: float) -> str:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        with context.wrap_socket(sock, server_hostname=host) as tls_sock:
            tls_sock.connect((host, port))
            if port in (443, 8443):
                tls_sock.sendall(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")
            data = tls_sock.recv(1024)
            return _clean_banner(data)
    finally:
        sock.close()


def _clean_banner(data: bytes) -> str:
    """Banner metnini temizler ve kısaltır."""
    if not data:
        return ""
    text = data.decode("utf-8", errors="replace")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = text.strip().replace("\r\n", " ").replace("\n", " ")
    return text[:200]
