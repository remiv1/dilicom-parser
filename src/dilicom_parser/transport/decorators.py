"""
Module contenant les décorateurs et classes utilitaires pour les opérations SFTP
avec le serveur de Dilicom.
Ce module inclut:
- Le décorateur `retry_sftp` pour réessayer les opérations SFTP en cas d'erreur de connexion.
"""

from typing import Callable, Any
import logging
import paramiko

logger = logging.getLogger(__name__)


def retry_sftp(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Décorateur pour réessayer une opération SFTP en cas d'erreur de connexion.

    args:
        func (callable): La fonction SFTP à décorer.
    returns:
        callable: La fonction décorée avec la logique de réessai.
    """

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except (paramiko.SSHException, EOFError):
            logger.warning(
                "Erreur de connexion SFTP détectée, tentative de reconnexion..."
            )
            self.connect()
            return func(self, *args, **kwargs)

    return wrapper
