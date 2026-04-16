"""Parseur de messages de service au format GENCOD (CNUT 05003)."""

from typing import List, Dict, Any
from ...models.service import (
    GencodServiceMessage,
    GencodCommentaireAleAte,
    GencodCommentaireErreur,
)

def _parse_rubrique(    # pylint: disable=too-many-arguments
        *,
        code: str,
        parts: List[str],
        current: Dict[str, Any],
        commentaires: List[Any],
        type_message: str,
        messages: List[GencodServiceMessage],
        line: str
        ) -> None:
    """
    Parse une ligne de rubrique et met à jour le dictionnaire courant.
    Les rubriques sont identifiées par leur code (100, 221, 176, 198, 177, 199).
    La rubrique 177 est un commentaire dont le format dépend du type de message
        (912 = ATE/ALE, 913 = ANE, 914 = AST).
    La rubrique 199 indique la fin du message et déclenche la création d'un GencodServiceMessage.
    """
    match code:
        case "100":
            current["gln_destinataire"] = parts[1] if len(parts) > 1 else ""

        case "221":
            current["gln_emetteur"] = parts[1] if len(parts) > 1 else ""

        case "176":
            current["date_emission"] = parts[1] if len(parts) > 1 else ""

        case "198":
            current["identificateur_reseau"] = parts[1] if len(parts) > 1 else ""
            current["type_message"] = parts[2] if len(parts) > 2 else ""

        case "177":
            commentaires.append(_parse_commentaire_177(parts=parts, type_message=type_message))

        case "199":
            nombre_rubriques = parts[1] if len(parts) > 1 else None
            msg = GencodServiceMessage(
                cnut=current.get("cnut", "05003"),
                gln_destinataire=current.get("gln_destinataire", ""),
                gln_emetteur=current.get("gln_emetteur", ""),
                date_emission=current.get("date_emission", ""),
                identificateur_reseau=current.get("identificateur_reseau", ""),
                type_message=current.get("type_message", ""),
                commentaires=commentaires,
                nombre_rubriques=nombre_rubriques,
            )
            messages.append(msg)
        case _:
            raise ValueError(f"Code de rubrique inattendu: {code} dans la ligne: {line}")

def _parse_commentaire_177(
    *,
    parts: List[str],
    type_message: str
) -> GencodCommentaireAleAte | GencodCommentaireErreur:
    """
    Parse une ligne CNUR 177 selon le type de message.
    Les champs sont positionnels et peuvent être absents
    (dans ce cas, on les remplace par des chaînes vides ou None).
    """

    def _get(index: int) -> str:
        return parts[index] if index < len(parts) else ""

    def _get_opt(index: int) -> str | None:
        val = parts[index] if index < len(parts) else ""
        return val if val else None

    # code 912 = ATE/ALE
    if type_message == "912":
        return GencodCommentaireAleAte(
            gln_emetteur_origine=_get(2),
            cnut_message_origine=_get(3),
            reference_cnut=_get(4),
            numero_envoi=_get(5),
            date_envoi=_get(6),
            gln_destinataire=_get(7),
            date_traitement=_get(8),
            heure_traitement=_get(9),
            date_lecture=_get_opt(10),
            heure_lecture=_get_opt(11),
        )

    # code 913 = ANE, 914 = AST
    return GencodCommentaireErreur(
        gln_emetteur_origine=_get(2),
        cnut_message_origine=_get(3),
        reference_cnut=_get(4),
        numero_envoi=_get(5),
        date_envoi=_get(6),
        gln_destinataire=_get(7),
        code_erreur=_get(8),
        numero_ligne_erreur=_get_opt(9),
        position_erreur=_get_opt(10),
        zone_erreur=_get_opt(11),
        libelle_erreur=_get_opt(12),
    )


def parse_gencod_lines(lines: List[str]) -> List[GencodServiceMessage]:
    """Parse les lignes d'un fichier GENCOD et retourne les messages de service.

    Le fichier est structuré en blocs délimités par des CNUT (05003...199).
    Chaque bloc contient des CNUR identifiés par leur code rubrique.
    """
    messages: List[GencodServiceMessage] = []
    current: Dict[str, Any] = {}
    commentaires: List[Any] = []
    type_message: str = ""

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split(';')
        code = parts[0] if parts else ""

        # CNUT de début (05003)
        if code == "05003":
            current = {"cnut": "05003"}
            commentaires = []
            type_message = ""
            continue

        # Rubriques
        _parse_rubrique(
            code=code,
            parts=parts,
            current=current,
            commentaires=commentaires,
            type_message=type_message,
            messages=messages,
            line=line
        )

        # Synchroniser type_message depuis le dictionnaire courant
        # (il est mis à jour par la rubrique 198)
        type_message = current.get("type_message", "")

    return messages
