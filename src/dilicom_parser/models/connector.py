"""
Module des modèles de données pour la gestion des fichiers distants sur le serveur SFTP de Dilicom.
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class RemoteFile:
    """
    Classe représentant un fichier distant sur le serveur SFTP de Dilicom.

    Attributes:
         filename (str): Le nom du fichier.
         filepath (str): Le chemin complet du fichier sur le serveur SFTP.
         size (int | None): La taille du fichier en octets, ou None si non disponible.
         modified_time (datetime | None): La date et l'heure de la dernière modification du fichier,
                                          ou None si non disponible.
    """

    filename: str
    filepath: str
    size: int | None
    modified_time: datetime | None

    def __str__(self):
        return (
            f"RemoteFile(filename='{self.filename}', filepath='{self.filepath}', "
            f"size={self.size}, modified_time={self.modified_time})"
        )
