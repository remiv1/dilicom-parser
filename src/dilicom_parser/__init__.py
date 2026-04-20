"""dilicom_parser
===================

Package racine exposant les principaux symboles publics.

Il expose ici les classes utilitaires fréquemment importées par les
utilisateurs et les tests (ex: ``DistributorParser``).
"""

from .parser.distributor_parser import DistributorParser
from .utils.registry import ParsersRegistry, get_registry

__all__ = ["DistributorParser", "ParsersRegistry", "get_registry"]
