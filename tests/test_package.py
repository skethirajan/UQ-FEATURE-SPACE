"""Tests for package_name."""

from __future__ import annotations

import package_name


def test_version() -> None:
    """Test that version is defined."""
    assert hasattr(package_name, "__version__")
    assert isinstance(package_name.__version__, str)


def test_all_exports() -> None:
    """Test that __all__ is defined."""
    assert hasattr(package_name, "__all__")
    assert isinstance(package_name.__all__, list)
