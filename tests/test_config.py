"""Tests for config module."""


import pytest
import yaml

from netracoon.config import load_config, merge_cli_config


class TestLoadConfig:
    def test_loads_yaml(self, tmp_path):
        config = {"target": "192.168.1.1", "ports": "top", "ping": True}
        path = tmp_path / "config.yaml"
        path.write_text(yaml.dump(config))
        result = load_config(path)
        assert result["target"] == "192.168.1.1"

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_invalid_yaml(self, tmp_path):
        path = tmp_path / "bad.yaml"
        path.write_text("just a string")
        with pytest.raises(ValueError):
            load_config(path)


class TestMergeCliConfig:
    def test_cli_overrides_file(self):
        file_cfg = {"target": "10.0.0.1", "ports": "top"}
        cli = {"target": "192.168.1.1"}
        result = merge_cli_config(cli, file_cfg)
        assert result["target"] == "192.168.1.1"
        assert result["ports"] == "top"

    def test_false_not_overridden(self):
        file_cfg = {"ping": True}
        cli = {"ping": False}
        result = merge_cli_config(cli, file_cfg)
        assert result["ping"] is True
