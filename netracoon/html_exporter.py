"""HTML rapor oluşturma."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

from netracoon.port_scanner import ScanResult

HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NetRacoon Scan Report</title>
  <style>
    :root {
      --bg: #0d1117; --surface: #161b22; --border: #30363d;
      --text: #c9d1d9; --accent: #58a6ff; --green: #3fb950;
      --red: #f85149; --yellow: #d29922; --purple: #bc8cff;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: var(--bg); color: var(--text); padding: 2rem; line-height: 1.6; }
    h1 { color: var(--accent); margin-bottom: 0.25rem; }
    .subtitle { color: #8b949e; margin-bottom: 2rem; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
             gap: 1rem; margin-bottom: 2rem; }
    .stat { background: var(--surface); border: 1px solid var(--border);
            border-radius: 8px; padding: 1.25rem; text-align: center; }
    .stat-value { font-size: 2rem; font-weight: 700; color: var(--accent); }
    .stat-label { font-size: 0.85rem; color: #8b949e; margin-top: 0.25rem; }
    .host-card { background: var(--surface); border: 1px solid var(--border);
                 border-radius: 8px; margin-bottom: 1.5rem; overflow: hidden; }
    .host-header { padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
                   display: flex; justify-content: space-between; align-items: center; }
    .host-ip { font-size: 1.1rem; font-weight: 600; color: var(--green); }
    .host-meta { font-size: 0.85rem; color: #8b949e; }
    .badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
             font-size: 0.75rem; font-weight: 600; }
    .badge-open { background: rgba(63,185,80,0.15); color: var(--green); }
    .badge-os { background: rgba(188,140,255,0.15); color: var(--purple); }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 0.75rem 1.25rem; background: rgba(255,255,255,0.03);
         font-size: 0.8rem; text-transform: uppercase; color: #8b949e; }
    td { padding: 0.75rem 1.25rem; border-top: 1px solid var(--border); font-size: 0.9rem; }
    .port-num { color: var(--accent); font-weight: 600; font-family: monospace; }
    .service { color: var(--purple); }
    .banner { color: #8b949e; font-size: 0.8rem; max-width: 500px; word-break: break-all; }
    .section { margin-bottom: 1rem; padding: 0 1.25rem 1rem; }
    .section h3 { font-size: 0.9rem; color: #8b949e; margin-bottom: 0.5rem; }
    .hop-list, .sub-list { list-style: none; display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .hop-list li, .sub-list li { background: rgba(255,255,255,0.05); padding: 0.25rem 0.75rem;
                                  border-radius: 4px; font-size: 0.85rem; font-family: monospace; }
    .filter-bar { margin-bottom: 1.5rem; }
    .filter-bar input { background: var(--surface); border: 1px solid var(--border);
                        color: var(--text); padding: 0.5rem 1rem; border-radius: 6px;
                        width: 300px; font-size: 0.9rem; }
    footer { margin-top: 3rem; text-align: center; color: #484f58; font-size: 0.8rem; }
  </style>
</head>
<body>
  <h1>🦝 NetRacoon Scan Report</h1>
  <p class="subtitle">Generated {{ scan_time }} · Duration: {{ elapsed }}s</p>

  <div class="stats">
    <div class="stat"><div class="stat-value">{{ host_count }}</div><div class="stat-label">Hosts Scanned</div></div>
    <div class="stat"><div class="stat-value">{{ open_port_count }}</div><div class="stat-label">Open Ports</div></div>
    <div class="stat"><div class="stat-value">{{ alive_count }}</div><div class="stat-label">Alive Hosts</div></div>
    <div class="stat"><div class="stat-value">{{ subdomain_count }}</div><div class="stat-label">Subdomains</div></div>
  </div>

  <div class="filter-bar">
    <input type="text" id="search" placeholder="Filter by IP, hostname, port, service..." oninput="filterHosts()">
  </div>

  {% for host in hosts %}
  <div class="host-card" data-search="{{ host.host }} {{ host.hostname }} {{ host.os_guess }} {% for p in host.open_ports %}{{ p.port }} {{ p.service }} {% endfor %}">
    <div class="host-header">
      <div>
        <span class="host-ip">{{ host.host }}</span>
        {% if host.hostname %}<span class="host-meta"> ({{ host.hostname }})</span>{% endif %}
      </div>
      <div>
        {% if host.os_guess %}<span class="badge badge-os">{{ host.os_guess }}</span>{% endif %}
        <span class="badge badge-open">{{ host.open_ports|length }} open</span>
      </div>
    </div>

    {% if host.traceroute %}
    <div class="section">
      <h3>Traceroute</h3>
      <ul class="hop-list">{% for hop in host.traceroute %}<li>{{ hop }}</li>{% endfor %}</ul>
    </div>
    {% endif %}

    {% if host.subdomains %}
    <div class="section">
      <h3>Subdomains</h3>
      <ul class="sub-list">{% for sub in host.subdomains %}<li>{{ sub }}</li>{% endfor %}</ul>
    </div>
    {% endif %}

    {% if host.open_ports %}
    <table>
      <thead><tr><th>Port</th><th>State</th><th>Service</th><th>Banner</th></tr></thead>
      <tbody>
        {% for p in host.open_ports %}
        <tr>
          <td class="port-num">{{ p.port }}</td>
          <td><span class="badge badge-open">{{ p.state }}</span></td>
          <td class="service">{{ p.service }}</td>
          <td class="banner">{{ p.banner or '—' }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="section"><em>No open ports found</em></div>
    {% endif %}
  </div>
  {% endfor %}

  <footer>NetRacoon — Network Discovery Tool · Use only on authorized networks</footer>

  <script>
    function filterHosts() {
      const q = document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('.host-card').forEach(card => {
        card.style.display = card.dataset.search.toLowerCase().includes(q) ? '' : 'none';
      });
    }
  </script>
</body>
</html>""")


def save_html(
    results: list[ScanResult],
    path: str | Path,
    elapsed: float = 0.0,
) -> Path:
    """Tarama sonuçlarını HTML rapor olarak kaydeder."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    hosts_data = []
    subdomain_count = 0
    open_port_count = 0

    for r in results:
        open_port_count += len(r.ports)
        subdomain_count += len(r.subdomains)
        hosts_data.append({
            "host": r.host,
            "hostname": r.hostname,
            "alive": r.alive,
            "os_guess": r.os_guess,
            "traceroute": r.traceroute,
            "subdomains": r.subdomains,
            "open_ports": [
                {
                    "port": p.port,
                    "state": p.state,
                    "service": p.service,
                    "banner": p.banner,
                }
                for p in r.ports
            ],
        })

    html = HTML_TEMPLATE.render(
        scan_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        elapsed=f"{elapsed:.1f}",
        host_count=len(results),
        open_port_count=open_port_count,
        alive_count=sum(1 for r in results if r.alive),
        subdomain_count=subdomain_count,
        hosts=hosts_data,
    )

    output.write_text(html, encoding="utf-8")
    return output
