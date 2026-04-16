"""
Modules de modèles de données pour le parser Dilicom.

Ce module regroupe les classes de modèles de données utilisées pour représenter les différentes
entités et structures de données rencontrées lors du parsing des fichiers Dilicom,
tels que les messages de service, les données de distributeurs, etc.
"""

from .connector import RemoteFile    # pylint: disable=unused-import # type: ignore
from .service import (
    GencodServiceMessage,    # pylint: disable=unused-import # type: ignore
    EancomInterchange,    # pylint: disable=unused-import # type: ignore
    EancomServiceMessage,    # pylint: disable=unused-import # type: ignore
    EancomNAD,    # pylint: disable=unused-import # type: ignore
    EancomErreur,    # pylint: disable=unused-import # type: ignore
)
from .distributor import (
    DistributorData,    # pylint: disable=unused-import # type: ignore
    DistributorLineData,    # pylint: disable=unused-import # type: ignore
    DistributorDataBloc1,    # pylint: disable=unused-import # type: ignore
    DistributorDataBloc2,    # pylint: disable=unused-import # type: ignore
    DistributorDataBloc3,    # pylint: disable=unused-import # type: ignore
)
