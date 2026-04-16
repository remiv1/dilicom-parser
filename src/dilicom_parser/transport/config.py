"""Module de configuration pour l'intégration avec Dilicom."""

from typing import Optional
from os import getenv
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

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
        return f"""
        <DilicomConfig :
            - Host : {self.host}
            - Port : {self.port}
            - Username : {self.username}
            - Password : {'****' if self.password else None}
        >
        """

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
    return DilicomConfig(
        out_folder=Path(getenv("DILICOM_OUT_DIR", "/path/to/dilicom/files")),
        in_folder=Path(getenv("DILICOM_IN_DIR", "/path/to/dilicom/files")),
        host=getenv("DILICOM_HOST", "sftp.dilicom.com"),
        port=int(getenv("DILICOM_PORT", "22")),
        username=getenv("DILICOM_USER", "your_username"),
        password=getenv("DILICOM_SECRET", "your_password"),
    )
