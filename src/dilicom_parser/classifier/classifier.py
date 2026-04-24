"""Module de classement des fichiers reçus depuis le serveur FTP de Dilicom."""

from typing import List, Any
import logging
from pathlib import Path
from ..models import FileHeader, FileContent, ParserConfig
from ..utils import ParsersRegistry

logger = logging.getLogger(__name__)

class FilesClassifier:
    """Classe de classification des fichiers reçus depuis le serveur FTP de Dilicom."""

    def __init__(self, file_list: list[Path]) -> None:
        self.file_list = file_list
        self.contents: list[FileContent] = self.__get_content()
        self.parsers_registry = ParsersRegistry()
        self.parser_config: ParserConfig

    def __get_headers(self, header: str) -> FileHeader:
        """
        Lit le fichier et retourne l'en-tête et les données.

        Returns:
            FileHeader: L'en-tête du fichier.

        """
        match header:
            case t if t.startswith("L000000"):
                h = header.strip().split(";")
                file_header = FileHeader(ref_file=h[0], type_file=h[1], date_file=h[2])
            case t if t.startswith("UNB+UNOB"):
                h = header
                file_header = FileHeader(ref_file=h, type_file="EANCOM", date_file="")
            case t if t.startswith("05003"):
                h = header
                file_header = FileHeader(ref_file=h, type_file="GENCOD", date_file="")
            case _:
                message = f"En-tête de fichier non reconnu: {header}"
                logger.error(message)
                raise ValueError(message)
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
                try:
                    with f.open("r", encoding="cp1252", newline="") as file:
                        lines = file.readlines()
                        header = self.__get_headers(lines[0])
                        footer = lines[-1].strip()

                        # Format CSV (Distributor) : splitter par ";"
                        # Autres formats (EANCOM, GENCOD) : garder les lignes entières
                        if "Distrib_DLC" in header.type_file:
                            # Format CSV : chaque ligne devient une liste
                            data = [line.strip().split(";") for line in lines[1:-1]]
                        else:
                            # Format texte/EDIFACT : chaque ligne est un élément unique
                            data = [[line.strip()] for line in lines[1:-1]]

                        content = FileContent(header=header, data=data, footer=footer)
                        contents.append(content)
                        logger.debug(
                            "Fichier lu: %s, en-tête: %s, nombre de lignes de données: %d",
                            f.name,
                            header,
                            len(data),
                        )
                except ValueError as e:
                    logger.warning(
                        "Fichier ignoré (en-tête ou encodage non reconnu): %s — %s",
                        f.name,
                        e,
                    )
            else:
                logger.warning("Le chemin %s n'est pas un fichier valide.", f)
        return contents

    def classify(self) -> "FilesClassifier":
        """
        Détermine le type de fichier en fonction de son en-tête.
         - Si l'en-tête correspond à "Distrib_DLC", le type de fichier est "distributor".
         - Autre en-têtes à implémenter selon les besoins futurs.
         - Si l'en-tête ne correspond à aucun type connu, le type de fichier est "unknown".
        Args:
            header (List[str]): L'en-tête du fichier à analyser.
        Returns:
            str: Le type de fichier déterminé ("distributor", "unknown", etc.).
        Raises:
            ValueError: Si la taille ou le format de l'en-tête est inattendu ou incorrect.
        """
        headers_and_types = self.parsers_registry.get_headers_and_types()

        for content in self.contents:
            match content.header.type_file:
                case t if any(k in t for k in headers_and_types):
                    file_type = next(v for k, v in headers_and_types.items() if k in t)
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

    def parse(self) -> dict[str, list[Any]]:
        """
        Parse les fichiers en fonction de leur type reconnu.
        
        Utilise les parsers définis dans la registry pour traiter
        les données de chaque type de fichier.

        Returns:
            dict[str, list]: Résultats du parsing organisés par type.
                            Ex: {"distributor": [...], "eancom": [...], ...}

        Raises:
            ValueError: Si aucun fichier n'a été classifié.
        """
        if not any(c.file_type != "unknown" for c in self.contents):
            message = "Aucun fichier classifié avant le parsing. Appelez classify() d'abord."
            logger.error(message)
            raise ValueError(message)

        parsed_results: dict[str, list[Any]] = {}

        for file_type in self.parsers_registry.list_types():
            files_of_type = self.get_files_by_type(file_type)

            if not files_of_type:
                logger.debug("Aucun fichier classifié du type '%s'", file_type)
                continue

            try:
                parser_class = self.parsers_registry.get_parser(file_type)
                logger.info("Parsing de %d fichier(s) de type '%s'", len(files_of_type), file_type)

                # Tous les parsers prennent une liste de FileContent en __init__
                # et disposent d'une méthode parse()
                parsed_data = parser_class(files_of_type).parse()
                parsed_results[file_type] = parsed_data

                logger.debug("Parsing réussi pour le type '%s'", file_type)
            except (KeyError, ImportError, ValueError, AttributeError, TypeError) as e:
                logger.error(
                    "Erreur lors du parsing des fichiers de type '%s': %s",
                    file_type,
                    str(e),
                )
                parsed_results[file_type] = []

        return parsed_results
