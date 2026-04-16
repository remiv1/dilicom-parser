"""
Module de définition des structures de données pour les messages de service Dilicom.
Couvre les formats GENCOD (CNUT 05003) et EANCOM (APERAK D96A).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union, TypeAlias
from enum import Enum


class ServiceMessageType(Enum):
    """Type de message de service Dilicom."""
    ATE = "912"  # Avis de traitement
    ALE = "912"  # Avis de lecture (même code, différencié par la présence de date de lecture)
    ANE = "913"  # Avis de non-émission
    AST = "914"  # Avis d'anomalie de structure


class OrigineMessageType(Enum):
    """Type du message d'origine."""
    COMMANDE = "023"
    AVIS_EXPEDITION = "024"
    JOURNAL_MOUVEMENTS = "152"


# ==================== GENCOD ====================

@dataclass
class GencodCommentaireAleAte:  # pylint: disable=too-many-instance-attributes
    """Commentaires (CNUR 177) pour ATE/ALE - identifiant 904."""
    gln_emetteur_origine: str
    cnut_message_origine: str
    reference_cnut: str
    numero_envoi: str
    date_envoi: str
    gln_destinataire: str
    date_traitement: str
    heure_traitement: str
    date_lecture: Optional[str] = None
    heure_lecture: Optional[str] = None


@dataclass
class GencodCommentaireErreur:  # pylint: disable=too-many-instance-attributes
    """Commentaires (CNUR 177) pour ANE (905) / AST (906)."""
    gln_emetteur_origine: str
    cnut_message_origine: str
    reference_cnut: str
    numero_envoi: str
    date_envoi: str
    gln_destinataire: str
    code_erreur: str
    numero_ligne_erreur: Optional[str] = None
    position_erreur: Optional[str] = None
    zone_erreur: Optional[str] = None
    libelle_erreur: Optional[str] = None


# TypeAlias pour clarifier le type des commentaires
GencodCommentaire: TypeAlias = Union[GencodCommentaireAleAte, GencodCommentaireErreur]


@dataclass
class GencodServiceMessage:
    """Message de service au format GENCOD (CNUT 05003)."""
    cnut: str
    gln_destinataire: str
    gln_emetteur: str
    date_emission: str
    identificateur_reseau: str
    type_message: str
    commentaires: list[GencodCommentaire] = field(default_factory=lambda: [])
    nombre_rubriques: Optional[str] = None

    @property
    def is_ale(self) -> bool:
        """ALE si type 912 et date de lecture présente dans au moins un commentaire."""
        if self.type_message != "912":
            return False
        return any(
            isinstance(c, GencodCommentaireAleAte) and c.date_lecture
            for c in self.commentaires
        )

    @property
    def is_ate(self) -> bool:
        """ATE si type 912 sans date de lecture."""
        return self.type_message == "912" and not self.is_ale

    @property
    def is_erreur(self) -> bool:
        """ANE (913) ou AST (914)."""
        return self.type_message in ("913", "914")


# ==================== EANCOM ====================

@dataclass
class EancomNAD:
    """Partie identifiée (NAD segment)."""
    fonction: str       # SU, BY, DP
    gln: str
    code_identifiant: str = "9"


@dataclass
class EancomErreur:
    """Segments ERC + FTX pour les erreurs."""
    code_erreur: str
    code_identification: str = "ZZZ"
    libelle_erreur: Optional[str] = None


@dataclass
class EancomServiceMessage:
    """Message de service au format EANCOM D96A (APERAK)."""
    # UNB
    syntaxe_id: str
    syntaxe_version: str
    gln_emetteur: str
    gln_destinataire: str
    date_preparation: str
    heure_preparation: str
    reference_interchange: str
    # UNH
    reference_message: str
    type_message: str       # APERAK
    version: str            # D
    revision: str           # 96A
    agence: str             # UN
    version_gs1: str
    # BGM
    identification_document: str
    type_acquittement: str  # AB (traitement/lecture), RE (erreur)
    # DTM
    date_creation: str
    format_date_creation: str
    # RFF
    reference_acquittee: str
    # DTM traitement
    date_traitement: Optional[str] = None
    format_date_traitement: Optional[str] = None
    # DTM lecture
    date_lecture: Optional[str] = None
    format_date_lecture: Optional[str] = None
    # NAD
    parties: list[EancomNAD] = field(default_factory=lambda: [])
    # ERC + FTX
    erreur: Optional[EancomErreur] = None
    # UNT
    nombre_segments: Optional[str] = None

    @property
    def is_ale(self) -> bool:
        """ALE si type AB et date de lecture présente."""
        return self.type_acquittement == "AB" and self.date_lecture is not None

    @property
    def is_ate(self) -> bool:
        """ATE si type AB sans date de lecture."""
        return self.type_acquittement == "AB" and self.date_lecture is None

    @property
    def is_erreur(self) -> bool:
        """Erreur si type RE."""
        return self.type_acquittement == "RE"


@dataclass
class EancomInterchange:
    """Un interchange EANCOM complet (UNB...UNZ) contenant N messages."""
    # UNB header
    syntaxe_id: str
    syntaxe_version: str
    gln_emetteur: str
    gln_destinataire: str
    date_preparation: str
    heure_preparation: str
    reference_interchange: str
    # Messages
    messages: list[EancomServiceMessage] = field(default_factory=lambda: [])
    # UNZ
    nombre_messages: Optional[str] = None
