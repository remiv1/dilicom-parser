"""Module de parsing des fichiers de messages de service Dilicom."""

import logging
from typing import Optional, List, Union
from os import getenv
from pathlib import Path

from ..models.service import (
    GencodServiceMessage,
    EancomInterchange,
)
from .services.gencod import parse_gencod_lines
from .services.eancom import parse_eancom


logger = logging.getLogger(__name__)


class ServiceParser:
    """
    Parseur pour les fichiers de messages de service (ATE/ALE/ANE/AST).
    - Détecte automatiquement le format du fichier (GENCOD/EANCOM) et utilise le parseur approprié.
    - Les messages GENCOD sont stockés dans une liste de GencodServiceMessage.
    - Les messages EANCOM sont stockés dans une instance d'EancomInterchange.

    - ATE : Accusé de réception technique
    - ALE : Accusé de réception logistique
    - ANE : Accusé de réception d'erreur
    - AST : Accusé de réception de statut

    Supporte les formats :
    - GENCOD (CNUT 05003) : fichiers à plat séparés par ';'
    - EANCOM D96A (APERAK) : fichiers EDIFACT
    """

    def __init__(self, directory: Optional[str] = None) -> None:
        self.directory: Path = Path(
            directory or getenv("DILICOM_IN_DIR", "./DILICOM_IN")
        )
        self.gencod_messages: List[GencodServiceMessage] = []
        self.eancom_interchange: Optional[EancomInterchange] = None
        if not self.directory.exists():
            logger.debug("Création du répertoire '%s'", self.directory)
            self.directory.mkdir(parents=True, exist_ok=True)

    def _detect_format(self, content: str) -> str:
        """
        Détecte le format du fichier (gencod ou eancom).

        Args:
            content: Contenu brut du fichier.

        Returns:
            - "gencod" pour un fichier GENCOD
            - "eancom" pour un fichier EANCOM
        """
        stripped = content.strip()
        if stripped.startswith("UNA") or stripped.startswith("UNB"):
            logger.debug("Format détecté: EANCOM")
            return "eancom"
        logger.debug("Format détecté: GENCOD")
        return "gencod"

    def parse_file(
        self, filename: str
    ) -> Union[List[GencodServiceMessage], EancomInterchange]:
        """
        Lit et parse un fichier de message de service.

        Args:
            filename: Nom du fichier à parser dans le répertoire configuré.

        Returns:
            - Liste de GencodServiceMessage pour un fichier GENCOD
            - EancomInterchange pour un fichier EANCOM
        """
        file_path = self.directory / filename
        content = file_path.read_text(encoding="cp1252")
        file_format = self._detect_format(content)

        if file_format == "eancom":
            self.eancom_interchange = parse_eancom(content)
            logger.debug(
                "Fichier '%s' parsé avec succès. Interchange EANCOM extrait.", filename
            )
            return self.eancom_interchange

        lines = content.splitlines()
        self.gencod_messages = parse_gencod_lines(lines)
        logger.debug(
            "Fichier '%s' parsé avec succès. Nombre de messages GENCOD extraits: %d",
            filename,
            len(self.gencod_messages),
        )
        return self.gencod_messages

    def parse_content(
        self, content: str
    ) -> Union[List[GencodServiceMessage], EancomInterchange]:
        """
        Parse du contenu brut de message de service.

        Args:
            content: Contenu brut du fichier.

        Returns:
            - Liste de GencodServiceMessage pour du GENCOD
            - EancomInterchange pour de l'EANCOM
        """
        file_format = self._detect_format(content)

        if file_format == "eancom":
            self.eancom_interchange = parse_eancom(content)
            logger.debug("Contenu parsé avec succès. Interchange EANCOM extrait.")
            return self.eancom_interchange

        lines = content.splitlines()
        self.gencod_messages = parse_gencod_lines(lines)
        logger.debug(
            "Contenu parsé avec succès. Nombre de messages GENCOD extraits: %d",
            len(self.gencod_messages),
        )
        return self.gencod_messages
