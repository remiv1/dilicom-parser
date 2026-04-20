"""Modèles utilitaires transverses au package."""

from dataclasses import dataclass


@dataclass
class ParserConfig:
    """Configuration d'un parser."""

    parser_module: str
    parser_callable: str | None = None
    header_content: str | None = None
