"""
Module de connection au serveur SFTP de Dilicom, avec gestion des erreurs et
des reconnexions automatiques.

Ce module inclut:
- La classe `Connector` pour gérer la connexion SFTP, les opérations de téléchargement
    et de listing de fichiers.
- Des exceptions personnalisées pour les erreurs de connexion, d'authentification
    et d'opérations SFTP.
- Un décorateur `retry_sftp` pour réessayer les opérations SFTP en cas d'erreur de connexion,
    avec une reconnexion automatique.
"""

from .connector import Connector  # pylint: disable=unused-import # type: ignore
from .exceptions import (  # pylint: disable=unused-import # type: ignore
    DilicomConnectionError,  # pylint: disable=unused-import # type: ignore
    DilicomAuthenticationError,  # pylint: disable=unused-import # type: ignore
    DilicomSFTPError,  # pylint: disable=unused-import # type: ignore
)
