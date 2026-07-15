"""Tests for scan profiles."""

import pytest

from netracoon.profiles import PROFILES, apply_profile, get_profile


class TestGetProfile:
    def test_quick(self):
        p = get_profile("quick")
        assert p.name == "quick"
        assert p.grab_banners is False

    def test_deep(self):
        p = get_profile("deep")
        assert p.ping is True
        assert p.grab_banners is True

    def test_stealth(self):
        p = get_profile("stealth")
        assert p.delay > 0
        assert p.rate > 0

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Bilinmeyen profil"):
            get_profile("invalid")

    def test_case_insensitive(self):
        assert get_profile("QUICK").name == "quick"


class TestApplyProfile:
    def test_applies_defaults(self):
        result = apply_profile({}, "quick")
        assert result["ports"] == "top"
        assert result["grab_banners"] is False

    def test_cli_override(self):
        result = apply_profile({"timeout": 5.0}, "quick")
        assert result["timeout"] == 5.0

    def test_all_profiles_exist(self):
        for name in ("quick", "deep", "stealth"):
            assert name in PROFILES
