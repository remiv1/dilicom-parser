"""Module de parsing des fichiers distributeurs Dilicom."""

from typing import Optional, List
from os import getenv
from pathlib import Path
import logging
import pandas as pd
from ..models.distributor import (
    df_to_distributor_data, DistributorData, FileDistri
)

logger = logging.getLogger(__name__)

class DistributorParser:
    """
    Classe de service pour le parsing des fichiers reçus de Dilicom.
    Cette classe est responsable de :
     - Lire les fichiers depuis un répertoire spécifié.
     - Déterminer le type de fichier en fonction de son en-tête.
     - Extraire les données pertinentes en fonction du type de fichier.
     - Stocker les données extraites dans des structures de données appropriées.

    Attributs :
     - directory : Path - Le répertoire où les fichiers sont stockés.
     - data : Optional[pd.DataFrame] - Les données extraites du fichier.
     - file_path : Optional[Path] - Le chemin complet du fichier en cours de traitement.
     - filename : str - Le nom du fichier en cours de traitement.
     - distributor_data : Optional[DistributorData] - Les données du distributeur extraites.

    Méthodes :
     - __init__() : Initialise les attributs de la classe et crée le répertoire s'il n'existe pas.
     - __define_file_type(header: List[str]) -> str : Détermine le type en fonction de son en-tête.
     - __parse_distrib(file_distri: FileDistri) -> None : Parse les fichiers de type 'supplier'
                                                          et extrait les données.
     - __get_header_footer_and_data() -> FileDistri : Lit le fichier et retourne l'en-tête,
                                                      le pied de page et les données.
     - parse_file(filename: str) -> None : Parse le fichier en fonction de son type et extrait
                                           les données.
    """

    def __init__(self) -> None:
        self.directory: Path = Path(getenv('DILICOM_IN_DIR', './DILICOM_IN'))
        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[Path] = None
        self.filename: str = ""
        self.distributor_data: Optional[DistributorData] = None
        if not self.directory.exists():
            logger.debug(
                "Création du répertoire '%s'",
                self.directory
            )
            self.directory.mkdir(parents=True, exist_ok=True)


    def __define_file_type(self, header: List[str]) -> str:
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
        headers_and_types = {
            "Distrib_DLC": "supplier",
        }
        if len(header) != 3:
            message = f"Taille du header inattendue: {len(header)}, attendu : 3"
            logger.error(message)
            raise ValueError(message)
        if header[0] != "L000000":
            message = f"Format d'en-tête inattendu: {header[0]}"
            logger.error(message)
            raise ValueError(message)
        match header[1]:
            case t if any(t.startswith(k) for k in headers_and_types):
                logger.debug("En-tête reconnu: %s, type de fichier: %s",
                             header[1], headers_and_types[t])
                return next(v for k, v in headers_and_types.items() if t.startswith(k))
            case _:
                logger.warning("En-tête non reconnu: %s. Type de fichier inconnu.",
                               header[1])
                return 'unknown'


    def __parse_distrib(self, file_distri: FileDistri) -> None:
        """
        Parse les fichiers de type 'supplier' et extrait les données.

        Args:
            file_distri (FileDistri): L'objet contenant l'en-tête, le pied de page
                                      et les données du fichier.
        Returns:
            None
        """
        if self.data is not None:
            self.distributor_data = df_to_distributor_data(file_distri)
        else:
            logger.warning("Aucune donnée à parser. Veuillez d'abord parser le fichier.")


    def __get_header_footer_and_data(self) -> FileDistri:
        """
        Lit le fichier et retourne l'en-tête et les données.

        Args:
            None
        Returns:
            FileDistri: Un objet contenant l'en-tête, le pied de page et les données du fichier.
        """
        _file_to_read = Path(self.directory / self.filename)
        with _file_to_read.open('r', encoding='cp1252', newline='') as f:
            lines = f.readlines()
            header = lines[0].strip().split(';')
            footer = lines[-1].strip()
            data = [line.strip().split(';') for line in lines[1:-1]]
            df = pd.DataFrame(data)
        logger.debug("Fichier lu: %s, en-tête: %s, nombre de lignes de données: %d",
                     self.filename, header, len(data))
        return FileDistri(header, footer, df)


    def parse_file(self, filename: str) -> None:
        """
        Parse le fichier en fonction de son type et extrait les données.

        Args:
            filename (str): Le nom du fichier à parser.
        Returns:
            None
        """
        parsers = {
            'supplier': self.__parse_distrib,
        }
        self.filename = filename
        self.file_path = self.directory / filename
        distri_file = self.__get_header_footer_and_data()
        file_type = self.__define_file_type(distri_file.header)
        logger.debug("Type de fichier déterminé: %s", file_type)
        if file_type in parsers:
            self.data = distri_file.data
            parsers[file_type](distri_file)
        else:
            logger.warning("Type de fichier inconnu pour l'en-tête: %s. Aucun parsing effectué.",
                           distri_file.header[1])
