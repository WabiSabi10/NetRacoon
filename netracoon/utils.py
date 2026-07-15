"""IP aralığı yardımcıları."""

from __future__ import annotations

import ipaddress


def expand_targets(target: str) -> list[str]:
    """Tek IP, hostname, CIDR veya aralığı IP listesine çevirir."""
    target = target.strip()

    if "/" in target:
        network = ipaddress.ip_network(target, strict=False)
        return [str(host) for host in network.hosts()]

    if "-" in target and not target.startswith("-"):
        return _expand_range(target)

    return [target]


def _expand_range(target: str) -> list[str]:
    """192.168.1.1-50 veya 192.168.1.1-192.168.1.50 formatını genişletir."""
    start_str, end_str = target.split("-", 1)
    start_str = start_str.strip()
    end_str = end_str.strip()

    start_ip = ipaddress.ip_address(start_str)

    if "." in end_str:
        end_ip = ipaddress.ip_address(end_str)
    else:
        parts = start_str.rsplit(".", 1)
        end_ip = ipaddress.ip_address(f"{parts[0]}.{end_str}")

    if int(end_ip) < int(start_ip):
        start_ip, end_ip = end_ip, start_ip

    return [str(ipaddress.ip_address(i)) for i in range(int(start_ip), int(end_ip) + 1)]


def parse_ports(port_spec: str) -> list[int]:
    """'22,80,443' veya '1-1024' veya 'top' port listesini ayrıştırır."""
    port_spec = port_spec.strip().lower()

    if port_spec == "top":
        return sorted(TOP_PORTS)

    ports: set[int] = set()
    for part in port_spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))

    return sorted(ports)


TOP_PORTS = {
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1723, 3306, 3389, 5900, 8080, 8443,
}
