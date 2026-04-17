"""Module de tests unitaires pour le module de transport du projet dilicom-parser."""

from typing import Any
import unittest
from unittest.mock import patch, MagicMock
from src.dilicom_parser.transport.config import load_dilicom_config, DilicomConfig
from src.dilicom_parser.transport.connector import Connector
from src.dilicom_parser.transport.decorators import retry_sftp
from src.dilicom_parser.transport.exceptions import (
    DilicomConnectionError,
    DilicomAuthenticationError,
    DilicomSFTPError,
)

SECRET_VALUE = "pass"


class TestDilicomConfig(unittest.TestCase):
    """Tests unitaires pour la classe DilicomConfig et la fonction load_dilicom_config."""

    @patch("src.dilicom_parser.transport.config.load_dotenv")
    @patch("src.dilicom_parser.transport.config.getenv")
    def test_load_dilicom_config(
        self, mock_getenv: MagicMock, mock_load_dotenv: MagicMock
    ):  # pylint: disable=unused-argument
        """
        Test de la fonction load_dilicom_config pour s'assurer qu'elle charge correctement
        la configuration à partir des variables d'environnement.
        Args:
            mock_getenv (MagicMock):
                Mock de la fonction getenv pour simuler les variables d'environnement.
            mock_load_dotenv (MagicMock):
                Mock de la fonction load_dotenv pour éviter de charger un fichier .env réel.
        """
        mock_getenv.side_effect = lambda key, default=None: {  # type: ignore
            "DILICOM_HOST": "localhost",
            "DILICOM_PORT": "22",
            "DILICOM_USER": "user",
            "DILICOM_SECRET": SECRET_VALUE,
            "DILICOM_OUT_DIR": "/tmp/out",
            "DILICOM_IN_DIR": "/tmp/in",
        }.get(
            key, default  # type: ignore
        )

        config = load_dilicom_config()
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 22)
        self.assertEqual(config.username, "user")
        self.assertEqual(config.password, SECRET_VALUE)
        self.assertEqual(str(config.out_folder), "/tmp/out")
        self.assertEqual(str(config.in_folder), "/tmp/in")


class TestConnector(unittest.TestCase):
    """
    Tests unitaires pour la classe Connector, en particulier l'initialisation de la configuration
    """

    @patch("src.dilicom_parser.transport.connector.load_dilicom_config")
    @patch("paramiko.SSHClient")
    def test_connector_initialization(
        self,
        mock_ssh_client: MagicMock,  # pylint: disable=unused-argument
        mock_load_config: MagicMock,
    ):
        """
        Test de l'initialisation de la classe Connector pour s'assurer que la configuration
        est correctement chargée
        """
        mock_load_config.return_value = DilicomConfig(
            host="localhost",
            port=22,
            username="user",
            password=SECRET_VALUE,
            out_folder="/tmp/out",  # type: ignore
            in_folder="/tmp/in",  # type: ignore
        )

        connector = Connector()
        self.assertEqual(connector.config.host, "localhost")
        self.assertEqual(connector.config.port, 22)
        self.assertEqual(connector.config.username, "user")
        self.assertEqual(connector.config.password, SECRET_VALUE)


class TestRetrySFTPDecorator(unittest.TestCase):
    """
    Tests unitaires pour le décorateur retry_sftp, en particulier la gestion des
    erreurs de connexion SFTP
    """

    @patch("src.dilicom_parser.transport.decorators.logger.warning")
    def test_retry_sftp(self, mock_logger: MagicMock):
        """
        Test du décorateur retry_sftp pour s'assurer qu'il gère correctement les erreurs de
        connexion SFTP en tentant de se reconnecter et en enregistrant un message d'avertissement
        """

        class MockConnector:
            """Classe de test pour simuler un connecteur avec une méthode de connexion."""

            def connect(self):
                """Simule une méthode de connexion qui échoue avec une erreur EOFError."""
                pass  # pylint: disable=unnecessary-pass

        @retry_sftp
        def mock_sftp_operation(self: Any):
            raise EOFError("Connection lost")

        mock_instance = MockConnector()
        with self.assertRaises(EOFError):
            mock_sftp_operation(mock_instance)
        mock_logger.assert_called_with(
            "Erreur de connexion SFTP détectée, tentative de reconnexion..."
        )


class TestExceptions(unittest.TestCase):
    """Tests unitaires pour les exceptions personnalisées du module de transport."""

    def test_dilicom_connection_error(self):
        """
        Test de l'exception DilicomConnectionError pour s'assurer qu'elle est levée correctement.
        """
        with self.assertRaises(DilicomConnectionError):
            raise DilicomConnectionError("Erreur de connexion")

    def test_dilicom_authentication_error(self):
        """
        Test de l'exception DilicomAuthenticationError pour s'assurer qu'elle est levée.
        """
        with self.assertRaises(DilicomAuthenticationError):
            raise DilicomAuthenticationError("Erreur d'authentification")

    def test_dilicom_sftp_error(self):
        """
        Test de l'exception DilicomSFTPError pour s'assurer qu'elle est levée correctement.
        """
        with self.assertRaises(DilicomSFTPError):
            raise DilicomSFTPError("Erreur SFTP")


if __name__ == "__main__":
    unittest.main()
