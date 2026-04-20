"""Module de classement des fichiers reçus depuis le serveur FTP de Dilicom."""

from typing import List
import logging
from pathlib import Path
from ..models import FileHeader, FileContent

logger = logging.getLogger(__name__)

class FilesClassifier:
    """Classe de classification des fichiers reçus depuis le serveur FTP de Dilicom."""

    HEADERS_AND_TYPES = {
        "Distrib_DLC": "supplier",
    }
    TYPES = set(HEADERS_AND_TYPES.values())

    def __init__(self, file_list: list[Path]) -> None:
        self.file_list = file_list
        self.contents: list[FileContent] = self.__get_content()

    def __get_headers(self, header: str) -> FileHeader:
        """
        Lit le fichier et retourne l'en-tête et les données.

        Returns:
            FileHeader: L'en-tête du fichier.

        """
        h = header.strip().split(";")
        file_header = FileHeader(ref_file=h[0], type_file=h[1], date_file=h[2])
        return file_header

    def __get_content(self) -> List[FileContent]:
        """
        Lit le fichier et retourne le contenu.

        Returns:
            List[FileContent]: La liste des contenus des fichiers.
        """
        contents: list[FileContent] = []
        for f in self.file_list:
            if f.is_file():
                with f.open("r", encoding="cp1252", newline="") as f:
                    lines = f.readlines()
                    header = self.__get_headers(lines[0])
                    footer = lines[-1].strip()
                    data = [line.strip().split(";") for line in lines[1:-1]]
                    content = FileContent(header=header, data=data, footer=footer)
                    contents.append(content)
                    logger.debug(
                        "Fichier lu: %s, en-tête: %s, nombre de lignes de données: %d",
                        f.name,
                        header,
                        len(data),
                    )
            else:
                logger.warning("Le chemin %s n'est pas un fichier valide.", f)
        return contents

    def classify(self) -> "FilesClassifier":
        """
        Détermine le type de fichier en fonction de son en-tête.
         - Si l'en-tête correspond à "Distrib_DLC", le type de fichier est "supplier".
         - Autre en-têtes à implémenter selon les besoins futurs.
         - Si l'en-tête ne correspond à aucun type connu, le type de fichier est "unknown".
        Args:
            header (List[str]): L'en-tête du fichier à analyser.
        Returns:
            str: Le type de fichier déterminé ("supplier", "unknown", etc.).
        Raises:
            ValueError: Si la taille ou le format de l'en-tête est inattendu ou incorrect.
        """
        for content in self.contents:
            if content.header.ref_file != "L000000":
                message = f"Format d'en-tête inattendu: {content.header.ref_file}"
                logger.error(message)
                raise ValueError(message)
            match content.header.type_file:
                case t if any(k in t for k in self.HEADERS_AND_TYPES):
                    file_type = next(v for k, v in self.HEADERS_AND_TYPES.items() if k in t)
                    logger.debug(
                        "En-tête reconnu: %s, type de fichier: %s",
                        content.header.type_file,
                        file_type,
                    )
                    content.file_type = file_type
                case _:
                    logger.warning(
                        "En-tête non reconnu: %s. Type de fichier inconnu.",
                        content.header.type_file
                    )
        return self

    def count_by_type(self) -> dict[str, int]:
        """
        Compte le nombre de fichiers par type.

        Returns:
            dict[str, int]:
                Un dictionnaire avec les types de fichiers comme clés et les comptes comme valeurs.
        """
        counts: dict[str, int] = {}
        for content in self.contents:
            counts[content.file_type] = counts.get(content.file_type, 0) + 1
        logger.info("Nombre de fichiers par type: %s", counts)
        return counts

    def get_files_by_type(self, file_type: str) -> list[FileContent]:
        """
        Récupère les fichiers d'un type spécifique.

        Args:
            file_type (str): Le type de fichier à filtrer.

        Returns:
            list[FileContent]: La liste des contenus de fichiers correspondant au type spécifié.
        """
        filtered_files = [content for content in self.contents if content.file_type == file_type]
        logger.info("Nombre de fichiers de type '%s': %d", file_type, len(filtered_files))
        return filtered_files
