"""Module de configuration pour l'intégration avec Dilicom."""

import logging
from typing import Optional
from os import getenv
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class DilicomConfig:
    """Classe de configuration pour l'intégration avec Dilicom."""
    host: str
    port: int
    username: str
    password: str
    out_folder: Path
    in_folder: Path

    def __repr__(self) -> str:
        return f"<DilicomConfig, host:port={self.host}:{self.port}, " \
               f"user={self.username}, password={'****' if self.password else 'None'}, " \
               f"out_folder={self.out_folder}, in_folder={self.in_folder}>"

    def __str__(self) -> str:
        return f"<DilicomConfig :" \
               f"\n  - host: {self.host}" \
               f"\n  - port: {self.port}" \
               f"\n  - username: {self.username}" \
               f"\n  - password: {'****' if self.password else 'None'}" \
               f"\n  - out_folder: {self.out_folder}" \
               f"\n  - in_folder: {self.in_folder}" \
               f">"


def load_dilicom_config(env_path: Optional[str] = None) -> DilicomConfig:
    """
    Charge la configuration de Dilicom à partir des variables d'environnement.
    
    Args:
        env_path (Optional[str]): Chemin vers le fichier .env.
                                  Si None, utilise le fichier .env par défaut.
    Returns:
        DilicomConfig: La configuration chargée.
    """
    load_dotenv(dotenv_path=env_path)
    logger.debug("Chargement de la configuration Dilicom à partir des variables d'environnement.")
    config = DilicomConfig(
        out_folder=Path(getenv("DILICOM_OUT_DIR", "/path/to/dilicom/files")),
        in_folder=Path(getenv("DILICOM_IN_DIR", "/path/to/dilicom/files")),
        host=getenv("DILICOM_HOST", "sftp.dilicom.com"),
        port=int(getenv("DILICOM_PORT", "22")),
        username=getenv("DILICOM_USER", "your_username"),
        password=getenv("DILICOM_SECRET", "your_password"),
    )
    logger.info("Configuration Dilicom chargée avec succès.")
    logger.debug(f"Configuration Dilicom : {config!r}")
    return config
