"""Tests for CLI module."""

import pytest

from netracoon.cli import _build_config, build_parser, main
from netracoon.scanner import ScanConfig


class TestBuildParser:
    def test_help_does_not_crash(self):
        parser = build_parser()
        assert parser.prog == "netracoon"

    def test_profile_choices(self):
        parser = build_parser()
        action = next(a for a in parser._actions if a.dest == "profile")
        assert "quick" in action.choices


class TestBuildConfig:
    def test_basic_target(self):
        parser = build_parser()
        args = parser.parse_args(["192.168.1.1"])
        config = _build_config(args)
        assert isinstance(config, ScanConfig)
        assert config.target == "192.168.1.1"

    def test_with_profile(self):
        parser = build_parser()
        args = parser.parse_args(["192.168.1.1", "--profile", "quick"])
        config = _build_config(args)
        assert config.grab_banners is False

    def test_no_target_raises(self, tmp_path):
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("ports: top\n")
        parser = build_parser()
        args = parser.parse_args(["--config", str(config_file)])
        with pytest.raises(ValueError, match="Hedef"):
            _build_config(args)


class TestMain:
    def test_no_args_returns_1(self):
        assert main([]) == 1
