"""Module de parsing des fichiers de messages de service Dilicom."""

from typing import Optional, List, Union
from os import getenv
from pathlib import Path

from dilicom_parser.models.service import (
    GencodServiceMessage,
    EancomInterchange,
)
from dilicom_parser.parser.services.gencod import parse_gencod_lines
from dilicom_parser.parser.services.eancom import parse_eancom


class ServiceParser:
    """Parseur pour les fichiers de messages de service (ATE/ALE/ANE/AST).

    Supporte les formats :
    - GENCOD (CNUT 05003) : fichiers à plat séparés par ';'
    - EANCOM D96A (APERAK) : fichiers EDIFACT
    """

    def __init__(self, directory: Optional[str] = None):
        self.directory: Path = Path(directory or getenv('DILICOM_IN_DIR', './DILICOM_IN'))
        self.gencod_messages: List[GencodServiceMessage] = []
        self.eancom_interchange: Optional[EancomInterchange] = None
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)

    def _detect_format(self, content: str) -> str:
        """Détecte le format du fichier (gencod ou eancom)."""
        stripped = content.strip()
        if stripped.startswith("UNA") or stripped.startswith("UNB"):
            return "eancom"
        return "gencod"

    def parse_file(self, filename: str) -> Union[List[GencodServiceMessage], EancomInterchange]:
        """Lit et parse un fichier de message de service.

        Args:
            filename: Nom du fichier à parser dans le répertoire configuré.

        Returns:
            - Liste de GencodServiceMessage pour un fichier GENCOD
            - EancomInterchange pour un fichier EANCOM
        """
        file_path = self.directory / filename
        content = file_path.read_text(encoding='cp1252')
        file_format = self._detect_format(content)

        if file_format == "eancom":
            self.eancom_interchange = parse_eancom(content)
            return self.eancom_interchange

        lines = content.splitlines()
        self.gencod_messages = parse_gencod_lines(lines)
        return self.gencod_messages

    def parse_content(self, content: str) -> Union[List[GencodServiceMessage], EancomInterchange]:
        """Parse du contenu brut de message de service.

        Args:
            content: Contenu brut du fichier.

        Returns:
            - Liste de GencodServiceMessage pour du GENCOD
            - EancomInterchange pour de l'EANCOM
        """
        file_format = self._detect_format(content)

        if file_format == "eancom":
            self.eancom_interchange = parse_eancom(content)
            return self.eancom_interchange

        lines = content.splitlines()
        self.gencod_messages = parse_gencod_lines(lines)
        return self.gencod_messages
