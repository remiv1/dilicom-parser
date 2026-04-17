"""Parseur de messages de service au format EANCOM D96A (APERAK)."""

import warnings
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from ...models.service import (
    EancomInterchange,
    EancomServiceMessage,
    EancomNAD,
    EancomErreur,
)
from ...utils.exceptions import SegmentInconnuWarning


def parse_eancom(content: str) -> EancomInterchange:
    """Parse le contenu brut d'un fichier EANCOM APERAK.

    Le séparateur de segment est le retour à la ligne (après UNA).
    Les éléments sont séparés par '+', les sous-éléments par ':'.
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    # Ignorer UNA si présent
    start = 0
    if lines and lines[0].startswith("UNA"):
        start = 1

    interchange = _parse_unb(lines[start])
    idx = start + 1

    while idx < len(lines):
        segment = lines[idx]
        tag = segment.split("+")[0]

        if tag == "UNH":
            msg, idx = _parse_message(lines, idx, interchange)
            interchange.messages.append(msg)
        elif tag == "UNZ":
            parts = segment.split("+")
            interchange.nombre_messages = parts[1] if len(parts) > 1 else None
            idx += 1
        else:
            idx += 1

    return interchange


def _parse_unb(line: str) -> EancomInterchange:
    """Parse le segment UNB (en-tête d'interchange).

    Le segment UNB identifie l'interchange et ses deux partenaires (émetteur
    et destinataire) ainsi que la date/heure de préparation et la référence
    unique d'interchange.

    Exemple : UNB+UNOB:2+3025590000008:14+3025616805006:14+151230:0638+2015456451964
    """
    # UNB+UNOB:2+3025590000008:14+3025616805006:14+151230:0638+2015456451964
    parts = line.split("+")
    syntaxe = parts[1].split(":") if len(parts) > 1 else ["", ""]
    emetteur = parts[2].split(":") if len(parts) > 2 else ["", ""]
    destinataire = parts[3].split(":") if len(parts) > 3 else ["", ""]
    date_heure = parts[4].split(":") if len(parts) > 4 else ["", ""]
    ref = parts[5] if len(parts) > 5 else ""

    return EancomInterchange(
        syntaxe_id=syntaxe[0],
        syntaxe_version=syntaxe[1] if len(syntaxe) > 1 else "",
        gln_emetteur=emetteur[0],
        gln_destinataire=destinataire[0],
        date_preparation=date_heure[0],
        heure_preparation=date_heure[1] if len(date_heure) > 1 else "",
        reference_interchange=ref,
    )


# ==================== Contexte de parsing ====================


@dataclass
class _MessageContext:
    """État mutable accumulé lors du parsing d'un message EANCOM (UNH…UNT).

    Chaque handler de segment met à jour les champs correspondants. À la fin
    du message (UNT), ce contexte est transmis à _build_message pour construire
    l'objet EancomServiceMessage immuable.

    Attributs:
        identification_document : Numéro du document acquitté (issu du BGM).
        type_acquittement       : Nature de l'acquittement — AB (traitement ou
                                  lecture) ou RE (rejet/erreur) (issu du BGM).
        date_creation           : Date de création du message APERAK (DTM 137).
        format_date_creation    : Format de date_creation, ex. « 102 » = AAAAMMJJ
                                  (DTM 137).
        reference_acquittee     : Référence du message d'origine acquitté (RFF).
        date_traitement         : Date à laquelle le message origine a été traité
                                  (DTM 4). None si non renseignée.
        format_date_traitement  : Format de date_traitement (DTM 4).
        date_lecture            : Date à laquelle le message origine a été lu
                                  (DTM 8). Présente uniquement pour les ALE.
        format_date_lecture     : Format de date_lecture (DTM 8).
        parties                 : Liste des parties identifiées (NAD) — typiquement
                                  l'émetteur (SU), le destinataire (BY) et le
                                  point de livraison (DP).
        erreur                  : Erreur signalée (ERC + FTX). None si aucune.
        nombre_segments         : Nombre de segments du message, tel que déclaré
                                  dans UNT.
    """

    identification_document: str = ""
    type_acquittement: str = ""
    date_creation: str = ""
    format_date_creation: str = ""
    reference_acquittee: str = ""
    date_traitement: Optional[str] = None
    format_date_traitement: Optional[str] = None
    date_lecture: Optional[str] = None
    format_date_lecture: Optional[str] = None
    parties: list[EancomNAD] = field(default_factory=lambda: [])
    erreur: Optional[EancomErreur] = None
    nombre_segments: Optional[str] = None


# ==================== Handlers de segments ====================


def _handle_bgm(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment BGM (Beginning of Message — début de message).

    Extrait l'identifiant du document acquitté et le type d'acquittement.
    Exemple : BGM+351::9+<identification_document>+5+AB
    """
    parts = segment.split("+")
    ctx.identification_document = parts[2] if len(parts) > 2 else ""
    ctx.type_acquittement = parts[4] if len(parts) > 4 else ""


def _handle_dtm(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment DTM (Date/Time/Period — date ou heure).

    Le qualificatif détermine la nature de la date :
      - 137 : date de création du message APERAK
      - 4   : date de traitement du message d'origine
      - 8   : date de lecture du message d'origine (ALE uniquement)

    Exemple : DTM+137:20151230:102
    """
    parts = segment[4:].split(":")
    qualifier = parts[0] if parts else ""
    date_val = parts[1] if len(parts) > 1 else ""
    format_val = parts[2] if len(parts) > 2 else ""
    match qualifier:
        case "137":
            ctx.date_creation, ctx.format_date_creation = date_val, format_val
        case "4":
            ctx.date_traitement, ctx.format_date_traitement = date_val, format_val
        case "8":
            ctx.date_lecture, ctx.format_date_lecture = date_val, format_val
        case _:
            warnings.warn(
                f"Qualificatif DTM inattendu : {qualifier!r} — segment ignoré.",
                SegmentInconnuWarning,
                stacklevel=2,
            )


def _handle_rff(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment RFF (Reference — référence).

    Extrait la référence du message d'origine faisant l'objet de cet acquittement.
    Exemple : RFF+ACE:2015456451964
    """
    parts = segment[4:].split(":")
    ctx.reference_acquittee = parts[1] if len(parts) > 1 else ""


def _handle_nad(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment NAD (Name and Address — identification d'une partie).

    Ajoute la partie identifiée à la liste du contexte. La fonction indique
    le rôle de la partie : SU (fournisseur/émetteur), BY (acheteur/destinataire)
    ou DP (point de livraison).

    Exemple : NAD+SU+3025590000008::9
    """
    parts = segment.split("+")
    fonction = parts[1] if len(parts) > 1 else ""
    gln_sub = parts[2].split(":") if len(parts) > 2 else ["", "", ""]
    ctx.parties.append(
        EancomNAD(
            fonction=fonction,
            gln=gln_sub[0],
            code_identifiant=gln_sub[2] if len(gln_sub) > 2 else "9",
        )
    )


def _handle_erc(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment ERC (Application Error Information — code d'erreur applicatif).

    Initialise l'erreur du contexte avec le code d'erreur Dilicom et son
    qualificatif d'identification. Le libellé est complété ultérieurement
    par le handler FTX.

    Exemple : ERC+7:ZZZ
    """
    parts = segment[4:].split(":")
    ctx.erreur = EancomErreur(
        code_erreur=parts[0],
        code_identification=parts[1] if len(parts) > 1 else "ZZZ",
    )


def _handle_ftx(segment: str, ctx: _MessageContext) -> None:
    """Traite le segment FTX (Free Text — texte libre).

    Complète le libellé de l'erreur déjà initialisée par ERC.
    Sans segment ERC préalable, ce segment est ignoré.

    Exemple : FTX+AAI+++Référence inconnue
    """
    parts = segment.split("+")
    if ctx.erreur:
        ctx.erreur.libelle_erreur = parts[4] if len(parts) > 4 else ""


_SEGMENT_HANDLERS: dict[str, Callable[[str, _MessageContext], None]] = {
    "BGM": _handle_bgm,
    "DTM": _handle_dtm,
    "RFF": _handle_rff,
    "NAD": _handle_nad,
    "ERC": _handle_erc,
    "FTX": _handle_ftx,
}


# ==================== Parsing principal ====================


def _parse_message(
    lines: List[str], idx: int, interchange: EancomInterchange
) -> tuple[EancomServiceMessage, int]:
    """Parse un message EANCOM délimité par UNH et UNT.

    Parcourt les segments ligne par ligne à partir de l'index donné et délègue
    chaque segment au handler correspondant via _SEGMENT_HANDLERS. S'arrête
    dès la rencontre du segment UNT (fin de message).

    Args:
        lines       : Liste de toutes les lignes de l'interchange.
        idx         : Index de la ligne UNH (début du message).
        interchange : Interchange parent, dont les informations d'en-tête
                      (GLN, référence…) sont reprises dans chaque message.

    Returns:
        Le message construit et l'index de la première ligne après UNT.
    """
    unh_parts = lines[idx].split("+")
    ref_message = unh_parts[1] if len(unh_parts) > 1 else ""
    msg_info = unh_parts[2].split(":") if len(unh_parts) > 2 else []
    idx += 1

    ctx = _MessageContext()

    while idx < len(lines):
        segment = lines[idx]
        tag = segment.split("+")[0]

        if tag == "UNT":
            parts = segment.split("+")
            ctx.nombre_segments = parts[1] if len(parts) > 1 else None
            idx += 1
            break

        handler = _SEGMENT_HANDLERS.get(tag)
        if handler:
            handler(segment, ctx)
        idx += 1

    return _build_message(ref_message, msg_info, interchange, ctx), idx


def _build_message(
    ref_message: str,
    msg_info: List[str],
    interchange: EancomInterchange,
    ctx: _MessageContext,
) -> EancomServiceMessage:
    """Construit un EancomServiceMessage immuable à partir du contexte de parsing.

    Args:
        ref_message : Référence unique du message, issue du segment UNH.
        msg_info    : Éléments d'identification du type de message issus de UNH
                      (type, version, révision, agence, version GS1).
        interchange : Interchange parent dont les métadonnées sont dupliquées
                      dans chaque message pour faciliter l'exploitation.
        ctx         : Contexte accumulé à la lecture des segments BGM, DTM,
                      RFF, NAD, ERC et FTX.
    """
    return EancomServiceMessage(
        syntaxe_id=interchange.syntaxe_id,
        syntaxe_version=interchange.syntaxe_version,
        gln_emetteur=interchange.gln_emetteur,
        gln_destinataire=interchange.gln_destinataire,
        date_preparation=interchange.date_preparation,
        heure_preparation=interchange.heure_preparation,
        reference_interchange=interchange.reference_interchange,
        reference_message=ref_message,
        type_message=msg_info[0] if msg_info else "APERAK",
        version=msg_info[1] if len(msg_info) > 1 else "",
        revision=msg_info[2] if len(msg_info) > 2 else "",
        agence=msg_info[3] if len(msg_info) > 3 else "",
        version_gs1=msg_info[4] if len(msg_info) > 4 else "",
        identification_document=ctx.identification_document,
        type_acquittement=ctx.type_acquittement,
        date_creation=ctx.date_creation,
        format_date_creation=ctx.format_date_creation,
        reference_acquittee=ctx.reference_acquittee,
        date_traitement=ctx.date_traitement,
        format_date_traitement=ctx.format_date_traitement,
        date_lecture=ctx.date_lecture,
        format_date_lecture=ctx.format_date_lecture,
        parties=ctx.parties,
        erreur=ctx.erreur,
        nombre_segments=ctx.nombre_segments,
    )
