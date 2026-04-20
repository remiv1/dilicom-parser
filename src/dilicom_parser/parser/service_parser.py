"""Module de parsing des fichiers de messages de service Dilicom."""

import logging
from typing import List, Union

from ..models.classifier import FileContent
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
    - Traite une liste de FileContent et détecte automatiquement le format (GENCOD/EANCOM).
    - Les messages GENCOD sont retournés dans une liste de GencodServiceMessage.
    - Les messages EANCOM sont retournés dans une instance d'EancomInterchange.

    - ATE : Accusé de réception technique
    - ALE : Accusé de réception logistique
    - ANE : Accusé de réception d'erreur
    - AST : Accusé de réception de statut

    Supporte les formats :
    - GENCOD (CNUT 05003) : fichiers à plat séparés par ';'
    - EANCOM D96A (APERAK) : fichiers EDIFACT
    """

    def __init__(self, file_contents: List[FileContent]) -> None:
        """Initialise le parseur avec une liste de FileContent.

        Args:
            file_contents: Liste de FileContent à parser
        """
        self.file_contents = file_contents
        self.parsed_results: List[Union[List[GencodServiceMessage], EancomInterchange]] = []

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

    def _reconstruct_content(self, file_content: FileContent) -> str:
        """Reconstruit le contenu texte à partir d'un FileContent.

        Args:
            file_content: FileContent à reconstruire

        Returns:
            Contenu texte original (header + data + footer)
        """
        lines: list[str] = []

        # Ajouter le header
        # Pour EANCOM/GENCOD, ref_file contient la première ligne originale
        # Pour Distributor, on la reconstruit à partir des champs
        if file_content.header.ref_file.startswith(("UNB", "05003", "L000000")):
            # C'est la première ligne originale (stockée dans ref_file)
            lines.append(file_content.header.ref_file)
        else:
            # Format distributor : reconstituer la ligne
            lines.append(
                f"{file_content.header.ref_file};" + \
                f"{file_content.header.type_file};" + \
                f"{file_content.header.date_file}"
            )

        # Ajouter les données
        for row in file_content.data:
            lines.append(";".join(row))

        # Ajouter le footer
        if file_content.footer:
            lines.append(file_content.footer)

        return "\n".join(lines)

    def parse(self) -> List[Union[List[GencodServiceMessage], EancomInterchange]]:
        """Parse la liste de FileContent.

        Traite chaque FileContent en détectant son format et en utilisant
        le parseur approprié (GENCOD ou EANCOM).

        Returns:
            Liste contenant les résultats du parsing.
            - List[GencodServiceMessage] pour les fichiers GENCOD
            - EancomInterchange pour les fichiers EANCOM

        Raises:
            ValueError: Si la liste de FileContent est vide
        """
        if not self.file_contents:
            message = "Aucun FileContent à parser"
            logger.error(message)
            raise ValueError(message)

        self.parsed_results = []

        for file_content in self.file_contents:
            try:
                # Reconstruire le contenu texte
                content = self._reconstruct_content(file_content)

                # Détecter le format
                file_format = self._detect_format(content)

                if file_format == "eancom":
                    result = parse_eancom(content)
                    logger.debug(
                        "Fichier EANCOM parsé avec succès. "
                        "Interchange EANCOM extrait."
                    )
                else:  # gencod
                    lines = content.splitlines()
                    result = parse_gencod_lines(lines)
                    logger.debug(
                        "Fichier GENCOD parsé avec succès. "
                        "Nombre de messages GENCOD extraits: %d",
                        len(result),
                    )

                self.parsed_results.append(result)

            except Exception as e:
                logger.error(
                    "Erreur lors du parsing du fichier %s: %s",
                    file_content.header.ref_file or file_content.header.type_file,
                    str(e),
                )
                raise

        return self.parsed_results
