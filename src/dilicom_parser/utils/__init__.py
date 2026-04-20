"""Utilitaires du package dilicom_parser."""

from .registry import ParsersRegistry, get_registry  # pylint: disable=unused-import # type: ignore

__all__ = ["ParsersRegistry", "get_registry"]
