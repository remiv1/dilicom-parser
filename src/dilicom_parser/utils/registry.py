"""Module pour charger et accéder aux parsers à partir du fichier de configuration TOML."""

import importlib
from pathlib import Path
from typing import Any, Callable
import logging

import tomllib  # Python 3.11+

from ..models.utils import ParserConfig

logger = logging.getLogger(__name__)

class ParsersRegistry:
    """Registre centralisé pour accéder aux parsers du package."""

    def __init__(self, config_path: str | None = None) -> None:
        """Initialise le registre avec le fichier TOML de configuration.

        Args:
            config_path: Chemin vers le fichier type_parsers.toml.
                         Par défaut, utilise le fichier embarqué dans le package.
        """
        if config_path is None:
            config_path = str(Path(__file__).parent / "type_parsers.toml")

        self.config_path = config_path
        self._config_data: dict[str, ParserConfig] = {}
        self._cache: dict[str, Callable[..., Any]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Charge la configuration TOML."""
        with open(self.config_path, "rb") as f:
            data: dict[str, Any] = tomllib.load(f)

        for type_name, type_config in data.get("types", {}).items():
            self._config_data[type_name] = ParserConfig(**type_config)

    def get_parser(self, type_name: str) -> Callable[..., Any]:
        """Récupère le callable de parsing pour un type donné.

        Args:
            type_name: Nom du type (ex : "distributor", "eancom")

        Returns:
            Fonction ou classe de parsing

        Raises:
            KeyError: Si le type n'existe pas dans la configuration
            ImportError: Si le module ou le callable ne peut pas être importé
        """
        if type_name in self._cache:
            return self._cache[type_name]

        config = self.get_config(type_name)
        callable_name = config.parser_callable or f"parse_{type_name}"

        module = importlib.import_module(config.parser_module)
        parser = getattr(module, callable_name)

        self._cache[type_name] = parser
        return parser

    def get_module(self, type_name: str) -> Any:
        """Récupère le module de parser complet.

        Args:
            type_name: Nom du type

        Returns:
            Module importé

        Raises:
            ImportError: Si le module ne peut pas être importé
        """
        try:
            config = self.get_config(type_name)
            return importlib.import_module(config.parser_module)
        except KeyError as e:
            raise ImportError(
                f"Impossible d'importer le module pour le type '{type_name}'"
            ) from e
        except ImportError as e:
            raise ImportError(
                f"Erreur lors de l'importation du module pour le type '{type_name}'"
            ) from e

    def get_config(self, type_name: str) -> ParserConfig:
        """Récupère la configuration pour un type.

        Args:
            type_name: Nom du type

        Returns:
            Configuration du type

        Raises:
            KeyError: Si le type n'existe pas
        """
        if type_name not in self._config_data:
            raise KeyError(
                f"Type '{type_name}' non trouvé. Types disponibles : {self.list_types()}"
            )
        return self._config_data[type_name]

    def list_types(self) -> list[str]:
        """Liste tous les types disponibles."""
        return list(self._config_data.keys())

    def get_header_start(self) -> list[str]:
        """Liste le contenu de l'en-tête pour tous les types disponibles.

        Returns:
            Contenu de l'en-tête pour tous les types
        """
        return [
            config.header_content for config in self._config_data.values() \
                if config.header_content is not None
            ]

    def get_headers_and_types(self) -> dict[str, str]:
        """Retourne un dictionnaire {header_content: type_name} pour tous les types configurés.

        Returns:
            Dictionnaire mappant le contenu d'en-tête au nom du type
        """
        values =  {
            config.header_content: type_name
            for type_name, config in self._config_data.items()
            if config.header_content is not None
        }
        if not values:
            message = "Aucun type de fichier avec en-tête défini dans la configuration."
            logger.warning(message)
            raise ValueError(message)
        return values


# Singleton
_registry: ParsersRegistry | None = None


def get_registry() -> ParsersRegistry:
    """Retourne l'instance globale du registre (singleton).

    Returns:
        Instance ParsersRegistry
    """
    global _registry  # pylint: disable=global-statement
    if _registry is None:
        _registry = ParsersRegistry()
    return _registry
