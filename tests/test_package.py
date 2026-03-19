"""Tests for uq_feature."""

from __future__ import annotations

import uq_feature


def test_version() -> None:
    """Test that version is defined."""
    assert hasattr(uq_feature, "__version__")
    assert isinstance(uq_feature.__version__, str)


def test_all_exports() -> None:
    """Test that __all__ is defined."""
    assert hasattr(uq_feature, "__all__")
    assert isinstance(uq_feature.__all__, list)
