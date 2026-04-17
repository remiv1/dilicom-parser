"""Repository pour les opérations liées à Dilicom."""

from datetime import datetime
from typing import List, Optional
from types import TracebackType
from pathlib import Path
import logging
import paramiko
from .config import DilicomConfig, load_dilicom_config
from .decorators import retry_sftp
from .exceptions import (
    DilicomConnectionError,
    DilicomAuthenticationError,
    DilicomSFTPError,
)
from ..models.connector import RemoteFile

logger = logging.getLogger(__name__)


class Connector:
    """
    Repository pour les opérations liées à Dilicom.
    Attributes:
        direction (str): La direction de l'opération, par défaut "put".
    """

    def __init__(self, timeout: int = 30):
        self.config: DilicomConfig = (
            load_dilicom_config()
        )  # Charger la configuration de Dilicom
        self.timeout = timeout  # Timeout pour la connexion SFTP
        self.client = None  # Client SSH pour la connexion SFTP
        self.transport = None  # Transport SSH pour la connexion SFTP
        self.sftp = None  # Client SFTP

    def __str__(self):
        return (
            f"<Dilicom Connector\n"
            f"    username={self.config.username}\n"
            f"    host={self.config.host}\n"
            f"    port={self.config.port}\n"
            f"    password={'****' if self.config.password else None}>"
        )

    def __repr__(self):
        return (
            f"<Connector("
            f"user={self.config.username!r}, "
            f"host={self.config.host!r}, "
            f"port={self.config.port!r})>"
        )

    def print_config(self) -> None:
        """Affiche la configuration de Dilicom utilisée par le repository."""
        print(self.config)

    def connect(self) -> None:
        """Établit une connexion au serveur SFTP de Dilicom."""
        try:
            # 1. client SSH
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.debug(
                "Initialisation SSH, host:port = %s:%s, user = %s, timeout = %s secondes",
                self.config.host,
                self.config.port,
                self.config.username,
                self.timeout,
            )
            # 2. connection SSH
            self.client.connect(
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                allow_agent=False,
                look_for_keys=False,
                timeout=self.timeout,
                banner_timeout=self.timeout,
                auth_timeout=self.timeout,
            )
            logger.debug(
                "Connexion SSH réussie, host:port = %s:%s, user = %s",
                self.config.host,
                self.config.port,
                self.config.username,
            )
            # 3. récupération du transport SSH
            self.transport = self.client.get_transport()
            if self.transport is None:
                raise DilicomConnectionError(
                    "Transport SSH indisponible pour la connexion SFTP."
                )
            opts = self.transport.get_security_options()
            # 4. forcer les algorithmes legacy encore utilisés par Dilicom
            opts.kex = ["diffie-hellman-group1-sha1"]
            opts.ciphers = ["aes128-cbc", "3des-cbc"]
            opts.digests = ["hmac-sha1"]
            opts.key_types = ["ssh-rsa"]
            logger.debug(
                "Transport SSH établi, host:port = %s:%s, useur = %s, "
                + "algo_KEX_dispo = %s, algo_chiffr_dispo = %s",
                self.config.host,
                self.config.port,
                self.config.username,
                opts.kex,
                opts.ciphers,
            )
            # 5. ouverture du client SFTP
            self.sftp = self.client.open_sftp()
            logger.info(
                "Connexion réussie, host:port = %s:%s",
                self.config.host,
                self.config.port,
            )
        except paramiko.AuthenticationException as e:
            message = f"Erreur d'authentification SSH : {e}"
            logger.exception(message)
            raise DilicomAuthenticationError(message) from e
        except paramiko.SSHException as e:
            message = f"Erreur SSH : {e}"
            logger.exception(message)
            raise DilicomConnectionError(message) from e
        except Exception as e:
            message = f"Erreur inattendue lors de la connexion : {e}"
            logger.error(message)
            raise DilicomConnectionError(message) from e

    def close(self) -> None:
        """Ferme la connexion au serveur SFTP de Dilicom."""
        if self.sftp:
            try:
                self.sftp.close()
                logger.info(
                    "Client SFTP fermé avec succès, host:port = %s:%s",
                    self.config.host,
                    self.config.port,
                )
            except Exception as e:
                message = f"Erreur lors de la fermeture du client SFTP de Dilicom: {e}"
                logger.error(message)
                raise DilicomSFTPError(message) from e

        if self.client:
            try:
                self.client.close()
                logger.info(
                    "Client SSH fermé avec succès, host:port = %s:%s",
                    self.config.host,
                    self.config.port,
                )
            except Exception as e:
                message = f"Erreur lors de la fermeture du client SSH de Dilicom: {e}"
                logger.exception(message)
                raise DilicomSFTPError(message) from e

        self.sftp = None
        self.client = None
        self.transport = None

    @retry_sftp
    def upload(self, local_path: str, remote_path: str) -> None:
        """
        Télécharge un fichier vers le serveur SFTP de Dilicom.

        Args:
            local_path (str): Le chemin local du fichier à télécharger.
            remote_path (str): Le chemin distant où le fichier doit être téléchargé.
        """
        if not self.sftp:
            message = DilicomConnectionError().stdr_message()
            logger.error(message)
            raise DilicomConnectionError(message)
        try:
            self.sftp.put(local_path, remote_path)
            logger.info(
                "Fichier '%s' téléchargé vers '%s' sur le serveur SFTP",
                local_path,
                remote_path,
            )
        except FileNotFoundError as e:
            message = f"Le fichier local '{local_path}' n'existe pas."
            logger.error(message)
            raise DilicomSFTPError(message) from e
        except Exception as e:
            message = (
                f"Erreur de téléchargement de '{local_path}' vers "
                f"'{remote_path}' sur le serveur SFTP de Dilicom: {e}"
            )
            logger.error(message)
            raise DilicomSFTPError(message) from e

    @retry_sftp
    def upload_from_memory(self, content: str | bytes, remote_path: str) -> None:
        """
        Télécharge un contenu depuis la mémoire vers le serveur SFTP de Dilicom.

        Args:
            content (str | bytes): Le contenu à télécharger.
            remote_path (str): Le chemin distant où le contenu doit être téléchargé.
        """
        if not self.sftp:
            message = DilicomConnectionError().stdr_message()
            logger.error(message)
            raise DilicomConnectionError(message)
        try:
            with self.sftp.file(remote_path, "w") as remote_file:
                if isinstance(content, str):
                    content = content.encode("utf-8")
                remote_file.write(content)
            logger.info(
                "Contenu téléchargé vers '%s' sur le serveur SFTP de Dilicom",
                remote_path,
            )
        except Exception as e:
            message = (
                f"Erreur lors du téléchargement de contenu vers '{remote_path}' "
                f"sur le serveur SFTP de Dilicom: {e}"
            )
            logger.error(message)
            raise DilicomSFTPError(message) from e

    @retry_sftp
    def download(
        self,
        remote_path: str | Path,
        local_path: Optional[str | Path] = None,
        archive: bool = False,
    ) -> None:
        """
        Télécharge un fichier depuis le serveur SFTP de Dilicom.

        Args:
            remote_path (str | Path): Le chemin distant du fichier à télécharger.
            local_path (str | Path, optional): Le chemin local où le fichier doit être téléchargé.
                                               Par défaut, './'.
            archive (bool): Indique si le fichier à télécharger se trouve dans le dossier d'archive
                            (./ARC) ou dans le dossier d'entrée (./O). Par défaut, False.
        Returns:
            None
        Raises:
            DilicomConnectionError: Si la connexion SFTP n'est pas établie.
            DilicomSFTPError: Si une erreur survient lors du téléchargement du fichier.
        """
        local_path = Path(local_path) if local_path else Path("./")
        local_file: Path | None = None
        if not self.sftp:
            message = DilicomConnectionError().stdr_message()
            logger.error(message)
            raise DilicomConnectionError(message)
        try:
            remote_path = Path(remote_path)
            filename = remote_path.name
            if archive:
                remote_path = (
                    Path("./ARC") / remote_path
                    if not str(remote_path).startswith("./")
                    else remote_path
                )
                remote_path = (
                    remote_path.with_suffix(".rdy")
                    if remote_path.suffix != ".rdy"
                    else remote_path
                )
            else:
                remote_path = (
                    Path("./O") / remote_path
                    if not str(remote_path).startswith("./")
                    else remote_path
                )

            # Si l'utilisateur a fourni un répertoire local (ou '.'), écrire le fichier
            # sous ce répertoire en gardant le nom distant.
            local_file_name = (
                f"{filename}.csv" if not filename.endswith(".csv") else filename
            )
            local_file = local_path / local_file_name

            # créer le répertoire parent si nécessaire
            try:
                local_file.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass

            # télécharger
            self.sftp.get(str(remote_path), str(local_file))

            # lire le contenu téléchargé (retourné au caller)
            with open(local_file, "rb") as f:
                content = f.read()
            txt_debug = (
                "Fichier '%s' téléchargé vers '%s' depuis '%s:%s' "
                + "(size = %d octets, content preview = %s)"
            )
            txt_info = (
                "Fichier '%s' téléchargé vers '%s' depuis '%s:%s' (size = %d octets)"
            )
            logger.debug(
                txt_debug,
                remote_path,
                local_file,
                self.config.host,
                self.config.port,
                len(content),
                content[:100],
            )
            logger.info(
                txt_info,
                remote_path,
                local_file,
                self.config.host,
                self.config.port,
                len(content),
            )
        except FileNotFoundError as e:
            message = f"Le fichier distant '{remote_path}' n'existe pas pour le téléchargement."
            logger.error(message)
            raise DilicomSFTPError(message) from e
        except Exception as e:
            message = (
                f"Erreur lors du téléchargement du fichier '{remote_path}' vers "
                f"'{local_path}' depuis le serveur SFTP de Dilicom: {e}"
            )
            logger.error(message)
            raise DilicomSFTPError(message) from e

    def list_files(
        self, remote_path: str = ".", complete: bool = False
    ) -> List[str] | List[RemoteFile]:
        """Liste les fichiers présents dans un répertoire du serveur SFTP de Dilicom.
        Args:
            remote_path (str): Le chemin distant du répertoire à lister.
            complete (bool): Si True, retourne les attributs complets des fichiers
                                (nom, chemin, taille, date de modification).
                             Si False, retourne uniquement les noms de fichiers.
        Returns:
            List[str] | List[RemoteFile]:
                - Une liste des noms de fichiers présents dans le répertoire ou
                - Une liste d'objets RemoteFile si complete est True.
        """
        if not self.sftp:
            message = DilicomConnectionError().stdr_message()
            logger.error(message)
            raise DilicomConnectionError(message)
        try:
            if complete:
                remotefiles: list[RemoteFile] = []
                for attr in self.sftp.listdir_attr(remote_path):
                    filename = attr.filename
                    filepath = f"{remote_path}/{filename}"
                    size = attr.st_size
                    int_modified_time = attr.st_mtime
                    if int_modified_time:
                        modified_time = datetime.fromtimestamp(int_modified_time)
                    else:
                        modified_time = None
                    remotefiles.append(
                        RemoteFile(
                            filename=filename,
                            filepath=filepath,
                            size=size,
                            modified_time=modified_time,
                        )
                    )
                logger.info(
                    "Fichier listés, répertoire '%s', serveur '%s:%s', nb_fichiers = %d",
                    remote_path,
                    self.config.host,
                    self.config.port,
                    len(remotefiles),
                )
                logger.debug(
                    "Fichiers listés, répertoire '%s', serveur '%s:%s', "
                    + "nb_fichiers = %d, fichiers = %s",
                    remote_path,
                    self.config.host,
                    self.config.port,
                    len(remotefiles),
                    [str(f) for f in remotefiles],
                )
                return remotefiles
            return self.sftp.listdir(remote_path)
        except FileNotFoundError as e:
            message = f"Le répertoire distant '{remote_path}' n'existe pas sur le serveur SFTP."
            logger.error(message)
            raise DilicomSFTPError(message) from e
        except Exception as e:
            message = (
                f"Erreur lors du listage dans le répertoire '{remote_path}' "
                + f"sur le serveur SFTP: {e}"
            )
            logger.error(message)
            raise DilicomSFTPError(message) from e

    def __enter__(self):
        """Permet d'utiliser le repository dans un contexte de gestion de ressources."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],  # pylint: disable=unused-argument
        exc_value: Optional[BaseException],  # pylint: disable=unused-argument
        traceback: Optional[TracebackType],  # pylint: disable=unused-argument
    ) -> None:
        """Ferme automatiquement la connexion lorsque le contexte est quitté."""
        self.close()
