"""NetRacoon komut satırı arayüzü."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from netracoon import __version__
from netracoon.config import load_config, merge_cli_config
from netracoon.profiles import apply_profile
from netracoon.scanner import ScanConfig, run_scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netracoon",
        description="NetRacoon — TCP port scanner, ping sweep & network discovery tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s 192.168.1.1
  %(prog)s 192.168.1.0/24 --ping
  %(prog)s scanme.nmap.org -p 22,80,443
  %(prog)s 10.0.0.1-50 --ping --profile stealth
  %(prog)s 192.168.1.1 --profile deep -o results.json --html report.html
  %(prog)s --config netracoon.yaml
  %(prog)s example.com --subdomains --os-fingerprint
""",
    )

    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target IP, hostname, CIDR (192.168.1.0/24) or range (192.168.1.1-50)",
    )
    parser.add_argument(
        "-p", "--ports",
        default=None,
        metavar="PORTS",
        help="Port list: 'top', '22,80,443' or '1-1024' (default: top)",
    )
    parser.add_argument(
        "--profile",
        choices=["quick", "deep", "stealth"],
        default=None,
        help="Scan profile: quick (fast), deep (thorough), stealth (slow/rate-limited)",
    )
    parser.add_argument(
        "--ping",
        action="store_true",
        default=None,
        help="Run ping sweep before port scan",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=None,
        metavar="SEC",
        help="Connection/ping timeout in seconds (default: 1.0)",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        metavar="N",
        help="Concurrent workers (default: 100)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=None,
        metavar="N",
        help="Max requests per second (0 = unlimited)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        metavar="SEC",
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_json",
        default=None,
        metavar="FILE",
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--csv",
        dest="output_csv",
        default=None,
        metavar="FILE",
        help="Save results to CSV file",
    )
    parser.add_argument(
        "--html",
        dest="output_html",
        default=None,
        metavar="FILE",
        help="Save results to HTML report",
    )
    parser.add_argument(
        "--config",
        dest="config_file",
        default=None,
        metavar="FILE",
        help="Load settings from YAML config file",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Disable banner grabbing",
    )
    parser.add_argument(
        "--no-dns",
        action="store_true",
        help="Disable hostname resolution",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Use thread-based scanner instead of asyncio",
    )
    parser.add_argument(
        "--os-fingerprint",
        action="store_true",
        default=None,
        help="Detect OS via TTL analysis",
    )
    parser.add_argument(
        "--traceroute",
        action="store_true",
        default=None,
        help="Run traceroute to target",
    )
    parser.add_argument(
        "--subdomains",
        action="store_true",
        default=None,
        help="Discover subdomains via wordlist",
    )
    parser.add_argument(
        "--log",
        dest="log_file",
        default=None,
        metavar="FILE",
        help="Write log to file",
    )
    parser.add_argument(
        "--save-history",
        action="store_true",
        default=None,
        help="Save scan to ~/.netracoon/history/",
    )
    parser.add_argument(
        "--diff",
        dest="diff_file",
        default=None,
        metavar="FILE",
        help="Compare results with a previous scan JSON",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output (line-by-line instead of progress bars)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"NetRacoon {__version__}",
    )

    return parser


def _build_config(args: argparse.Namespace) -> ScanConfig:
    file_config: dict[str, Any] = {}
    if args.config_file:
        file_config = load_config(args.config_file)

    cli_args: dict[str, Any] = {
        "target": args.target,
        "ports": args.ports,
        "timeout": args.timeout,
        "workers": args.workers,
        "ping": args.ping,
        "rate": args.rate,
        "delay": args.delay,
        "output_json": args.output_json or file_config.get("output"),
        "output_csv": args.output_csv or file_config.get("csv"),
        "output_html": args.output_html or file_config.get("html"),
        "verbose": args.verbose or file_config.get("verbose", False),
        "profile": args.profile or file_config.get("profile"),
        "os_fingerprint": args.os_fingerprint or file_config.get("os_fingerprint", False),
        "traceroute": args.traceroute or file_config.get("traceroute", False),
        "subdomains": args.subdomains or file_config.get("subdomains", False),
        "log_file": args.log_file or file_config.get("log", ""),
        "save_history": args.save_history or file_config.get("save_history", False),
        "diff_file": args.diff_file or file_config.get("diff", ""),
    }

    if args.no_banner:
        cli_args["grab_banners"] = False

    merged = merge_cli_config(cli_args, file_config)

    if merged.get("profile"):
        merged = apply_profile(merged, merged["profile"])

    merged.setdefault("grab_banners", True)

    target = merged.get("target")
    if not target:
        raise ValueError("Hedef belirtilmedi. target argümanı veya config dosyası gerekli.")

    return ScanConfig(
        target=str(target),
        ports=str(merged.get("ports", "top")),
        timeout=float(merged.get("timeout", 1.0)),
        workers=int(merged.get("workers", 100)),
        ping=bool(merged.get("ping", False)),
        grab_banners=bool(merged.get("grab_banners", True)),
        resolve_hostnames=not args.no_dns,
        output_json=str(merged.get("output_json", "") or ""),
        output_csv=str(merged.get("output_csv", "") or ""),
        output_html=str(merged.get("output_html", "") or ""),
        verbose=bool(merged.get("verbose", False)),
        profile=str(merged.get("profile", "") or ""),
        rate=int(merged.get("rate", 0) or 0),
        delay=float(merged.get("delay", 0.0) or 0.0),
        use_async=not args.sync,
        os_fingerprint=bool(merged.get("os_fingerprint", False)),
        traceroute=bool(merged.get("traceroute", False)),
        subdomains=bool(merged.get("subdomains", False)),
        log_file=str(merged.get("log_file", "") or ""),
        save_history=bool(merged.get("save_history", False)),
        diff_file=str(merged.get("diff_file", "") or ""),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.target and not args.config_file:
        from netracoon import display

        display.print_banner()
        parser.print_help()
        return 1

    try:
        config = _build_config(args)
        run_scan(config)
        return 0
    except KeyboardInterrupt:
        print("\nScan cancelled.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
