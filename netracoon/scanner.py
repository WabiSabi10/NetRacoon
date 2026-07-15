"""Ana tarama orkestrasyonu."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from netracoon import banner as banner_mod
from netracoon import display
from netracoon.async_scanner import scan_ports_async
from netracoon.dns_resolver import resolve_reverse, resolve_target
from netracoon.exporter import save_csv, save_json
from netracoon.history import compare_scans, load_history, save_to_history
from netracoon.html_exporter import save_html
from netracoon.logging_config import setup_logging
from netracoon.os_fingerprint import fingerprint_os
from netracoon.ping_sweep import ping_sweep
from netracoon.port_scanner import PortResult, ScanResult, scan_ports
from netracoon.services import get_service_name
from netracoon.subdomain import discover_subdomains
from netracoon.traceroute import traceroute as run_traceroute
from netracoon.utils import expand_targets, parse_ports

logger = logging.getLogger("netracoon")


@dataclass
class ScanConfig:
    target: str
    ports: str = "top"
    timeout: float = 1.0
    workers: int = 100
    ping: bool = False
    grab_banners: bool = True
    resolve_hostnames: bool = True
    output_json: str = ""
    output_csv: str = ""
    output_html: str = ""
    verbose: bool = False
    profile: str = ""
    rate: int = 0
    delay: float = 0.0
    use_async: bool = True
    os_fingerprint: bool = False
    traceroute: bool = False
    subdomains: bool = False
    log_file: str = ""
    save_history: bool = False
    diff_file: str = ""


@dataclass
class ScanReport:
    results: list[ScanResult] = field(default_factory=list)
    alive_hosts: list[str] = field(default_factory=list)
    elapsed: float = 0.0


def run_scan(config: ScanConfig) -> ScanReport:
    """Tam tarama akışını çalıştırır."""
    setup_logging(config.log_file, config.verbose)
    start = time.monotonic()
    display.print_banner()

    targets = expand_targets(config.target)
    port_list = parse_ports(config.ports)
    logger.info("Starting scan: target=%s ports=%d", config.target, len(port_list))

    if config.ping or len(targets) > 1:
        hosts = _run_ping_sweep(targets, config)
    else:
        hosts = targets

    results = _run_port_scans(hosts, port_list, config)

    elapsed = time.monotonic() - start
    report = ScanReport(results=results, alive_hosts=hosts, elapsed=elapsed)

    display.print_scan_results(results)

    open_count = sum(len(r.ports) for r in results)
    display.print_summary(
        alive_count=len(hosts),
        total_hosts=len(targets),
        open_ports=open_count,
        elapsed=elapsed,
    )

    _export_results(results, config, elapsed)

    if config.save_history:
        from netracoon.exporter import _serialize_results
        path = save_to_history(_serialize_results(results))
        display.console.print(f"[green]✓[/green] Geçmişe kaydedildi: [cyan]{path}[/cyan]")

    if config.diff_file:
        _show_diff(results, config.diff_file)

    return report


def _export_results(results: list[ScanResult], config: ScanConfig, elapsed: float) -> None:
    if config.output_json:
        path = save_json(results, config.output_json)
        display.console.print(f"[green]✓[/green] JSON kaydedildi: [cyan]{path}[/cyan]")
    if config.output_csv:
        path = save_csv(results, config.output_csv)
        display.console.print(f"[green]✓[/green] CSV kaydedildi: [cyan]{path}[/cyan]")
    if config.output_html:
        path = save_html(results, config.output_html, elapsed)
        display.console.print(f"[green]✓[/green] HTML rapor kaydedildi: [cyan]{path}[/cyan]")


def _show_diff(results: list[ScanResult], diff_file: str) -> None:
    from netracoon.exporter import _serialize_results

    try:
        previous = load_history(diff_file)
        current = _serialize_results(results)
        diff = compare_scans(current, previous)
        display.print_diff(diff)
    except FileNotFoundError:
        display.console.print(f"[yellow]Diff dosyası bulunamadı: {diff_file}[/yellow]")


def _run_ping_sweep(targets: list[str], config: ScanConfig) -> list[str]:
    display.console.print(f"\n[bold]Ping Sweep[/bold] — {len(targets)} hedef taranıyor...\n")
    alive: list[str] = []

    if config.verbose:
        def on_result(host: str, is_alive: bool) -> None:
            display.print_ping_result(host, is_alive)
            if is_alive:
                alive.append(host)

        ping_sweep(targets, timeout=config.timeout, workers=config.workers, on_result=on_result)
        display.console.print()
        return sorted(alive)

    progress = display.make_ping_progress(len(targets))

    with progress:
        task = progress.add_task("ping", total=len(targets))

        def on_result(host: str, is_alive: bool) -> None:
            if is_alive:
                alive.append(host)
            progress.advance(task)

        ping_sweep(targets, timeout=config.timeout, workers=config.workers, on_result=on_result)

    display.print_alive_hosts(sorted(alive))
    return sorted(alive)


def _run_port_scans(
    hosts: list[str],
    ports: list[int],
    config: ScanConfig,
) -> list[ScanResult]:
    results: list[ScanResult] = []

    for host in hosts:
        ip, hostname = resolve_target(host) if config.resolve_hostnames else (host, "")
        if not ip:
            ip = host

        if config.resolve_hostnames and not hostname:
            hostname = resolve_reverse(ip)

        display.console.print(
            f"\n[bold]Port Tarama[/bold] — [cyan]{ip}[/cyan]"
            + (f" ({hostname})" if hostname else "")
            + f" — {len(ports)} port"
            + (" [dim](async)[/dim]" if config.use_async else "")
            + "\n"
        )

        open_ports = _scan_host_ports(ip, ports, config)

        for port_result in open_ports:
            port_result.service = get_service_name(port_result.port)
            if config.grab_banners:
                port_result.banner = banner_mod.grab_banner(
                    ip, port_result.port, timeout=config.timeout * 2
                )

        os_guess = ""
        if config.os_fingerprint:
            os_guess = fingerprint_os(ip, config.timeout)
            logger.info("OS fingerprint %s: %s", ip, os_guess)

        hops: list[str] = []
        if config.traceroute:
            display.console.print(f"  [dim]Traceroute {ip}...[/dim]")
            hops = run_traceroute(ip)
            logger.info("Traceroute %s: %d hops", ip, len(hops))

        subs: list[str] = []
        if config.subdomains and hostname:
            domain = _extract_domain(hostname)
            if domain:
                display.console.print(f"  [dim]Subdomain keşfi: {domain}...[/dim]")
                subs = discover_subdomains(domain, workers=min(config.workers, 30))
                logger.info("Subdomains for %s: %d found", domain, len(subs))

        results.append(ScanResult(
            host=ip,
            hostname=hostname,
            ports=open_ports,
            alive=True,
            os_guess=os_guess,
            traceroute=hops,
            subdomains=subs,
        ))

    return results


def _scan_host_ports(host: str, ports: list[int], config: ScanConfig) -> list[PortResult]:
    open_ports: list[PortResult] = []

    if config.use_async:
        if config.verbose:
            def on_port(result: PortResult) -> None:
                display.print_port_found(result)

            open_ports = asyncio.run(scan_ports_async(
                host, ports,
                timeout=config.timeout,
                workers=config.workers,
                rate=config.rate,
                delay=config.delay,
                on_result=on_port,
            ))
        else:
            progress = display.make_port_progress(host, len(ports))
            with progress:
                task = progress.add_task("scan", total=len(ports))

                def on_port(result: PortResult) -> None:
                    progress.advance(task)

                open_ports = asyncio.run(scan_ports_async(
                    host, ports,
                    timeout=config.timeout,
                    workers=config.workers,
                    rate=config.rate,
                    delay=config.delay,
                    on_result=on_port,
                ))
    else:
        if config.verbose:
            def on_port(result: PortResult) -> None:
                display.print_port_found(result)

            open_ports = scan_ports(
                host, ports, timeout=config.timeout, workers=config.workers, on_result=on_port
            )
        else:
            progress = display.make_port_progress(host, len(ports))
            with progress:
                task = progress.add_task("scan", total=len(ports))

                def on_port(result: PortResult) -> None:
                    progress.advance(task)

                open_ports = scan_ports(
                    host, ports, timeout=config.timeout, workers=config.workers, on_result=on_port
                )

    return open_ports


def _extract_domain(hostname: str) -> str:
    """Hostname'den kök domain çıkarır."""
    parts = hostname.rstrip(".").split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return hostname
