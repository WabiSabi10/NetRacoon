"""YAML config dosyası desteği."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """YAML config dosyasını yükler."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config dosyası bulunamadı: {config_path}")

    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Config dosyası bir YAML sözlüğü olmalı")

    return data


def merge_cli_config(
    cli_args: dict[str, Any],
    config_file: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Config dosyası + CLI argümanlarını birleştirir (CLI öncelikli)."""
    merged: dict[str, Any] = {}
    if config_file:
        merged.update(config_file)

    for key, value in cli_args.items():
        if value is not None and value != "" and value is not False:
            merged[key] = value

    return merged
