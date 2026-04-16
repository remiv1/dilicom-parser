"""Tests pour les imports des classes principales du module dilicom_parser."""

from src.dilicom_parser import DistributorParser


def test_imports():
    """Test that the main classes can be imported without errors."""
    assert DistributorParser is not None
