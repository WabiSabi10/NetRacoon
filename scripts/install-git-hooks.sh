#!/bin/sh
# NetRacoon git hook kurulumu.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp "$ROOT/scripts/prepare-commit-msg" "$ROOT/.git/hooks/prepare-commit-msg"
chmod +x "$ROOT/.git/hooks/prepare-commit-msg"
echo "Git hook kuruldu."
