"""Tests for display module."""

from netracoon.display import ASCII_BANNER, _build_creator_text, print_diff


class TestAsciiBanner:
    def test_banner_has_five_lines(self):
        assert len(ASCII_BANNER) == 5

    def test_banner_contains_letters(self):
        art = "\n".join(ASCII_BANNER)
        assert "_" in art
        assert "|" in art

    def test_creator_shows_wabisabi10(self):
        text = _build_creator_text()
        assert "WabiSabi10" in str(text)


class TestPrintDiff:
    def test_no_diff(self, capsys):
        print_diff({"new_hosts": [], "removed_hosts": [], "new_ports": {}, "closed_ports": {}})
        captured = capsys.readouterr()
        assert "Fark bulunamadı" in captured.out or "Fark" in captured.out

    def test_new_hosts(self, capsys):
        print_diff({
            "new_hosts": ["192.168.1.5"],
            "removed_hosts": [],
            "new_ports": {},
            "closed_ports": {},
        })
        captured = capsys.readouterr()
        assert "192.168.1.5" in captured.out
