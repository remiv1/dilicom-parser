from _typeshed import Incomplete
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

class ServiceMessageType(Enum):
    ATE = '912'
    ALE = '912'
    ANE = '913'
    AST = '914'

class OrigineMessageType(Enum):
    COMMANDE = '023'
    AVIS_EXPEDITION = '024'
    JOURNAL_MOUVEMENTS = '152'

@dataclass
class GencodCommentaireAleAte:
    gln_emetteur_origine: str
    cnut_message_origine: str
    reference_cnut: str
    numero_envoi: str
    date_envoi: str
    gln_destinataire: str
    date_traitement: str
    heure_traitement: str
    date_lecture: str | None = ...
    heure_lecture: str | None = ...

@dataclass
class GencodCommentaireErreur:
    gln_emetteur_origine: str
    cnut_message_origine: str
    reference_cnut: str
    numero_envoi: str
    date_envoi: str
    gln_destinataire: str
    code_erreur: str
    numero_ligne_erreur: str | None = ...
    position_erreur: str | None = ...
    zone_erreur: str | None = ...
    libelle_erreur: str | None = ...
GencodCommentaire: TypeAlias = GencodCommentaireAleAte | GencodCommentaireErreur

@dataclass
class GencodServiceMessage:
    cnut: str
    gln_destinataire: str
    gln_emetteur: str
    date_emission: str
    identificateur_reseau: str
    type_message: str
    commentaires: list[GencodCommentaire] = field(default_factory=Incomplete)
    nombre_rubriques: str | None = ...
    @property
    def is_ale(self) -> bool: ...
    @property
    def is_ate(self) -> bool: ...
    @property
    def is_erreur(self) -> bool: ...

@dataclass
class EancomNAD:
    fonction: str
    gln: str
    code_identifiant: str = ...

@dataclass
class EancomErreur:
    code_erreur: str
    code_identification: str = ...
    libelle_erreur: str | None = ...

@dataclass
class EancomServiceMessage:
    syntaxe_id: str
    syntaxe_version: str
    gln_emetteur: str
    gln_destinataire: str
    date_preparation: str
    heure_preparation: str
    reference_interchange: str
    reference_message: str
    type_message: str
    version: str
    revision: str
    agence: str
    version_gs1: str
    identification_document: str
    type_acquittement: str
    date_creation: str
    format_date_creation: str
    reference_acquittee: str
    date_traitement: str | None = ...
    format_date_traitement: str | None = ...
    date_lecture: str | None = ...
    format_date_lecture: str | None = ...
    parties: list[EancomNAD] = field(default_factory=Incomplete)
    erreur: EancomErreur | None = ...
    nombre_segments: str | None = ...
    @property
    def is_ale(self) -> bool: ...
    @property
    def is_ate(self) -> bool: ...
    @property
    def is_erreur(self) -> bool: ...

@dataclass
class EancomInterchange:
    syntaxe_id: str
    syntaxe_version: str
    gln_emetteur: str
    gln_destinataire: str
    date_preparation: str
    heure_preparation: str
    reference_interchange: str
    messages: list[EancomServiceMessage] = field(default_factory=Incomplete)
    nombre_messages: str | None = ...
