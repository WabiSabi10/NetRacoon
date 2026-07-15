# Contributing to NetRacoon

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/WabiSabi10/NetRacoon.git
cd netracoon
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `pytest --cov=netracoon`
4. Run lint: `ruff check netracoon tests`
5. Run type check: `mypy netracoon`
6. Commit with a clear message
7. Open a Pull Request

## Code Style

- Follow existing module structure and naming conventions
- Use type hints for public functions
- Keep functions focused and testable
- Mock network calls in tests — never scan real networks in automated tests

## Ethical Use

NetRacoon is an educational network discovery tool. Only scan networks you own or have explicit permission to test.

## Reporting Issues

Please include:
- Python version
- OS
- Full command used
- Expected vs actual behavior
