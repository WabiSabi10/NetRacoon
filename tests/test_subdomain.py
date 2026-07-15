"""Tests for subdomain discovery."""

from unittest.mock import patch

from netracoon.subdomain import discover_subdomains, load_wordlist


class TestLoadWordlist:
    def test_builtin_fallback(self, tmp_path):
        words = load_wordlist(tmp_path / "missing.txt")
        assert "www" in words
        assert len(words) > 10

    def test_load_from_file(self, tmp_path):
        path = tmp_path / "words.txt"
        path.write_text("api\ntest\n# comment\n\ndev\n")
        words = load_wordlist(path)
        assert words == ["api", "test", "dev"]


class TestDiscoverSubdomains:
    @patch("netracoon.subdomain.socket.gethostbyname")
    def test_finds_subdomains(self, mock_dns):
        def side_effect(host):
            if host == "www.example.com":
                return "1.2.3.4"
            raise OSError("not found")

        mock_dns.side_effect = side_effect
        result = discover_subdomains("example.com", wordlist=["www", "missing"], workers=2)
        assert "www.example.com" in result

    @patch("netracoon.subdomain.socket.gethostbyname", side_effect=OSError("fail"))
    def test_no_results(self, mock_dns):
        result = discover_subdomains("example.com", wordlist=["nope"], workers=1)
        assert result == []
