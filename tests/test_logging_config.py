"""Tests for logging configuration."""

import logging

from netracoon.logging_config import setup_logging


class TestSetupLogging:
    def test_returns_logger(self):
        logger = setup_logging(verbose=False)
        assert logger.name == "netracoon"

    def test_verbose_sets_debug(self):
        logger = setup_logging(verbose=True)
        assert logger.level == logging.DEBUG

    def test_log_file(self, tmp_path):
        log_path = tmp_path / "scan.log"
        setup_logging(log_file=str(log_path), verbose=True)
        logging.getLogger("netracoon").info("test message")
        assert log_path.exists()
        assert "test message" in log_path.read_text()
