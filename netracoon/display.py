"""Rich ile renkli terminal çıktısı."""

from __future__ import annotations

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from netracoon import __version__
from netracoon.port_scanner import PortResult, ScanResult

console = Console()

# figlet "NetRacoon" -f standard
ASCII_BANNER = [
    " _   _      _   ____                             ",
    "| \\ | | ___| |_|  _ \\ __ _  ___ ___   ___  _ __  ",
    "|  \\| |/ _ \\ __| |_) / _` |/ __/ _ \\ / _ \\| '_ \\ ",
    "| |\\  |  __/ |_|  _ < (_| | (_| (_) | (_) | | | |",
    "|_| \\_|\\___|\\__|_| \\_\\__,_|\\___\\___/ \\___/|_| |_|",
]

def _rgb_at(
    t: float,
    start: tuple[int, int, int],
    end: tuple[int, int, int],
) -> tuple[int, int, int]:
    """İki renk arasında t (0-1) konumunda RGB döndürür."""
    return (
        int(start[0] + (end[0] - start[0]) * t),
        int(start[1] + (end[1] - start[1]) * t),
        int(start[2] + (end[2] - start[2]) * t),
    )


def _gradient_text(text: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> Text:
    """Metne RGB gradient uygular."""
    result = Text()
    letters = [c for c in text if c not in " "]
    if not letters:
        return result.append(text)

    step = max(len(letters) - 1, 1)
    color_idx = 0
    for char in text:
        if char == " ":
            result.append(char)
            continue
        t = color_idx / step
        r, g, b = _rgb_at(t, start, end)
        result.append(char, style=f"bold rgb({r},{g},{b})")
        color_idx += 1
    return result


def _build_logo_text() -> Text:
    """Renkli ASCII NetRacoon banner'ı (satır + karakter gradient)."""
    logo = Text()
    top_color = (0, 255, 255)      # cyan
    bottom_color = (255, 0, 255)   # magenta
    line_count = len(ASCII_BANNER)

    for i, line in enumerate(ASCII_BANNER):
        line_t = i / max(line_count - 1, 1)
        line_color = _rgb_at(line_t, top_color, bottom_color)
        next_color = _rgb_at(min(line_t + 0.15, 1.0), top_color, bottom_color)
        chars = [c for c in line if c != " "]
        char_step = max(len(chars) - 1, 1)
        char_idx = 0

        for char in line:
            if char == " ":
                logo.append(char)
                continue
            t = char_idx / char_step
            r, g, b = _rgb_at(t, line_color, next_color)
            logo.append(char, style=f"bold rgb({r},{g},{b})")
            char_idx += 1
        logo.append("\n")

    return logo


def _build_creator_text() -> Text:
    """Creator bilgisi."""
    creator = Text()
    creator.append("✦ ", style="bold yellow")
    creator.append("creator: ", style="dim italic")
    creator.append_text(_gradient_text("WabiSabi10", (255, 200, 0), (255, 80, 180)))
    creator.append(" ✦", style="bold yellow")
    return creator


def print_banner() -> None:
    subtitle = _gradient_text(
        "Ağ Keşif & Port Tarayıcı",
        start=(100, 220, 255),
        end=(200, 150, 255),
    )
    version = Text(f"v{__version__}", style="dim bright_black")
    prompt = _gradient_text(
        "$ netracoon",
        start=(63, 185, 80),
        end=(88, 166, 255),
    )

    header = Group(
        Align.center(_build_logo_text()),
        Align.center(subtitle),
        Align.center(_build_creator_text()),
        Align.center(version),
        Text(""),
        Align.center(prompt),
    )
    console.print(
        Panel(header, border_style="bold bright_magenta", padding=(1, 3), expand=False)
    )


def print_alive_hosts(alive: list[str]) -> None:
    if not alive:
        console.print("[yellow]Canlı host bulunamadı.[/yellow]")
        return

    table = Table(title="Canlı Hostlar", border_style="green", show_lines=False)
    table.add_column("#", style="dim", width=4)
    table.add_column("IP Adresi", style="bold green")
    table.add_column("Durum", style="green")

    for i, host in enumerate(alive, 1):
        table.add_row(str(i), host, "● UP")

    console.print(table)
    console.print(f"\n[green]Toplam: {len(alive)} canlı host[/green]\n")


def print_scan_results(results: list[ScanResult]) -> None:
    for result in results:
        _print_host_result(result)


def _print_host_result(result: ScanResult) -> None:
    header = f"{result.host}"
    if result.hostname:
        header += f" ({result.hostname})"
    if result.os_guess:
        header += f" [{result.os_guess}]"

    if not result.ports and not result.subdomains:
        console.print(f"\n[dim]{header}[/dim] — [yellow]açık port yok[/yellow]")
        return

    if result.traceroute:
        console.print(f"  [dim]Route:[/dim] {' → '.join(result.traceroute)}")

    if result.subdomains:
        console.print(f"  [magenta]Subdomains:[/magenta] {', '.join(result.subdomains)}")

    if not result.ports:
        console.print(f"\n[dim]{header}[/dim] — [yellow]açık port yok[/yellow]")
        return

    table = Table(
        title=f"🔍 {header}",
        border_style="blue",
        show_lines=True,
    )
    table.add_column("Port", style="cyan", justify="right")
    table.add_column("Durum", justify="center")
    table.add_column("Servis", style="magenta")
    table.add_column("Banner", style="dim", max_width=60, overflow="fold")

    for port in result.ports:
        state_style = "bold green" if port.state == "open" else "red"
        table.add_row(
            str(port.port),
            Text(port.state.upper(), style=state_style),
            port.service,
            port.banner or "—",
        )

    console.print(table)


def make_ping_progress(total: int) -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn(
            "[bold bright_cyan]NetRacoon[/bold bright_cyan] "
            "[dim]│[/dim] [bold blue]Ping Sweep[/bold blue]"
        ),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    )


def make_port_progress(host: str, total: int) -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn(
            f"[bold bright_cyan]NetRacoon[/bold bright_cyan] "
            f"[dim]│[/dim] [bold blue]{host}[/bold blue]"
        ),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("{task.completed}/{task.total} port"),
        TimeElapsedColumn(),
        console=console,
    )


def print_ping_result(host: str, alive: bool) -> None:
    if alive:
        console.print(f"  [green]●[/green] {host} [green]UP[/green]")
    else:
        console.print(f"  [dim]○ {host} DOWN[/dim]", highlight=False)


def print_port_found(result: PortResult) -> None:
    if result.state == "open":
        console.print(
            f"  [green]●[/green] Port [cyan]{result.port}[/cyan] "
            f"[bold green]OPEN[/bold green]"
        )


def print_summary(
    alive_count: int,
    total_hosts: int,
    open_ports: int,
    elapsed: float,
) -> None:
    console.print()
    console.print(Panel(
        f"[green]Canlı host:[/green] {alive_count}/{total_hosts}\n"
        f"[cyan]Açık port:[/cyan] {open_ports}\n"
        f"[dim]Süre:[/dim] {elapsed:.1f}s",
        title="[bold bright_cyan]NetRacoon[/bold bright_cyan] Özet",
        border_style="bright_cyan",
    ))


def print_diff(diff: dict) -> None:
    """İki tarama arasındaki farkları gösterir."""
    console.print("\n[bold]Tarama Karşılaştırması[/bold]\n")

    if diff.get("new_hosts"):
        console.print("[green]+ Yeni hostlar:[/green]")
        for h in diff["new_hosts"]:
            console.print(f"  [green]+ {h}[/green]")

    if diff.get("removed_hosts"):
        console.print("[red]- Kaldırılan hostlar:[/red]")
        for h in diff["removed_hosts"]:
            console.print(f"  [red]- {h}[/red]")

    if diff.get("new_ports"):
        console.print("[green]+ Yeni açık portlar:[/green]")
        for host, ports in diff["new_ports"].items():
            console.print(f"  [green]{host}:[/green] {', '.join(map(str, ports))}")

    if diff.get("closed_ports"):
        console.print("[red]- Kapanan portlar:[/red]")
        for host, ports in diff["closed_ports"].items():
            console.print(f"  [red]{host}:[/red] {', '.join(map(str, ports))}")

    if not any(diff.values()):
        console.print("[dim]Fark bulunamadı — taramalar aynı.[/dim]")
