"""
Module des modèles de données pour la classification des
fichiers distants sur le serveur SFTP de Dilicom.
"""

from typing import Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class FileHeader:
    """
    Classe représentant l'en-tête d'un fichier de données de Dilicom.

    Attributes:
        ref_file (str): La référence du fichier.
        type_file (str): Le type de fichier.
        date_file (str): La date de création du fichier.
    """
    ref_file: str
    type_file: str
    date_file: str

@dataclass
class FileContent:
    """
    Classe représentant le contenu d'un fichier de données de Dilicom.

    Attributes:
        header (FileHeader): L'en-tête du fichier.
        data (list[list[str]]): Les données du fichier, représentées comme une liste
                                de listes de chaînes de caractères.
        footer (str): Le pied de page du fichier.
    """
    header: FileHeader
    data: list[list[str]]
    footer: str
    file_type: str = "unknown"
    df: Optional[pd.DataFrame] = None
