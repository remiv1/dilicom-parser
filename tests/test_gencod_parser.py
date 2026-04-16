"""Tests pour le parseur GENCOD (CNUT 05003)."""

from pathlib import Path

import pytest

from src.dilicom_parser.parser.services.gencod import parse_gencod_lines
from src.dilicom_parser.models.service import GencodCommentaireAleAte, GencodCommentaireErreur


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def ate_lines() -> list[str]:
    """Charge un message ATE (Avis de traitement) valide."""
    return (FIXTURES_DIR / "gencod_ate_valid.txt").read_text().splitlines()


@pytest.fixture
def ale_lines() -> list[str]:
    """Charge un message ALE (Avis de lecture) valide."""
    return (FIXTURES_DIR / "gencod_ale_valid.txt").read_text().splitlines()


@pytest.fixture
def ane_lines() -> list[str]:
    """Charge un message ANE (Avis de non-émission) avec erreur."""
    return (FIXTURES_DIR / "gencod_ane_with_error.txt").read_text().splitlines()


@pytest.fixture
def multiple_messages_lines() -> list[str]:
    """Charge un fichier GENCOD avec plusieurs messages."""
    return (FIXTURES_DIR / "gencod_multiple_messages.txt").read_text().splitlines()


class TestGencodParserBasics:
    """Tests basiques du parseur GENCOD."""

    def test_parse_ate_message(self, ate_lines: list[str]) -> None: # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ATE (Avis de traitement)."""
        messages = parse_gencod_lines(ate_lines)

        assert len(messages) == 1
        msg = messages[0]

        assert msg.cnut == "05003"
        assert msg.gln_destinataire == "3025616805006"
        assert msg.gln_emetteur == "3025590000008"
        assert msg.date_emission == "20151230"
        assert msg.identificateur_reseau == "RESEAU001"
        assert msg.type_message == "912"
        assert msg.nombre_rubriques == "7"

        assert msg.is_ate
        assert not msg.is_ale
        assert not msg.is_erreur

        assert len(msg.commentaires) == 1
        comment = msg.commentaires[0]
        assert isinstance(comment, GencodCommentaireAleAte)
        assert comment.gln_emetteur_origine == "3025590000008"
        assert comment.cnut_message_origine == "05003"
        assert comment.reference_cnut == "REF001"
        assert comment.numero_envoi == "ENV001"
        assert comment.date_envoi == "20151201"
        assert comment.gln_destinataire == "3025616805006"
        assert comment.date_traitement == "20151230"
        assert comment.heure_traitement == "0900"
        assert comment.date_lecture is None
        assert comment.heure_lecture is None

    def test_parse_ale_message(self, ale_lines: list[str]) -> None: # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ALE (Avis de lecture)."""
        messages = parse_gencod_lines(ale_lines)

        assert len(messages) == 1
        msg = messages[0]

        assert msg.is_ale
        assert not msg.is_ate
        assert not msg.is_erreur

        comment = msg.commentaires[0]
        assert isinstance(comment, GencodCommentaireAleAte)
        assert comment.date_traitement == "20151230"
        assert comment.heure_traitement == "0900"
        assert comment.date_lecture == "20151230"
        assert comment.heure_lecture == "1130"

    def test_parse_ane_message_with_error(self, ane_lines: list[str]) -> None: # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ANE avec erreur."""
        messages = parse_gencod_lines(ane_lines)

        assert len(messages) == 1
        msg = messages[0]

        assert msg.is_erreur
        assert not msg.is_ate
        assert not msg.is_ale
        assert msg.type_message == "913"

        assert len(msg.commentaires) == 1
        comment = msg.commentaires[0]
        assert isinstance(comment, GencodCommentaireErreur)
        assert comment.gln_emetteur_origine == "3025590000008"
        assert comment.cnut_message_origine == "05003"
        assert comment.reference_cnut == "REF003"
        assert comment.numero_envoi == "ENV003"
        assert comment.code_erreur == "7"
        assert comment.libelle_erreur == "Référence inconnue"
        assert comment.numero_ligne_erreur is None
        assert comment.position_erreur is None
        assert comment.zone_erreur is None


class TestGencodParserMultipleMessages:
    """Tests pour les fichiers GENCOD avec plusieurs messages."""

    def test_parse_multiple_messages(
        self, multiple_messages_lines: list[str] # pylint: disable=redefined-outer-name
    ) -> None:
        """Valide le parsing d'un fichier GENCOD avec plusieurs messages."""
        messages = parse_gencod_lines(multiple_messages_lines)

        assert len(messages) == 2

        msg1 = messages[0]
        msg2 = messages[1]

        assert msg1.identificateur_reseau == "RESEAU004"
        assert msg1.is_ate

        assert msg2.identificateur_reseau == "RESEAU005"
        assert msg2.is_ale

        # Vérifier que les commentaires sont distincts
        comment1 = msg1.commentaires[0]
        comment2 = msg2.commentaires[0]

        assert comment1.reference_cnut == "REF004"
        assert comment2.reference_cnut == "REF005"

        assert comment1.date_lecture is None    # type: ignore
        assert comment2.date_lecture == "20151230"  # type: ignore


class TestGencodParserDataIntegrity:
    """Tests pour l'intégrité des données parsées."""

    def test_empty_fields_handled(self, ate_lines: list[str]) -> None: # pylint: disable=redefined-outer-name
        """Valide que les champs vides sont gérés correctement."""
        messages = parse_gencod_lines(ate_lines)
        msg = messages[0]

        # Tous les champs requis doivent être présents et non-vides
        assert msg.cnut
        assert msg.gln_destinataire
        assert msg.gln_emetteur
        assert msg.date_emission
        assert msg.type_message

    def test_multiple_commentaires(self) -> None:
        """Valide le parsing avec plusieurs commentaires (CNUR 177)."""
        lines = """05003
100;3025616805006
221;3025590000008
176;20151230
198;RESEAU006;912
177;904;3025590000008;05003;REF006A;ENV006;20151201;3025616805006;20151230;0900
177;904;3025590000008;05003;REF006B;ENV007;20151202;3025616805006;20151230;1030
199;8
""".strip().splitlines()

        messages = parse_gencod_lines(lines)    # type: ignore

        assert len(messages) == 1
        msg = messages[0]
        assert len(msg.commentaires) == 2

        assert msg.commentaires[0].reference_cnut == "REF006A"
        assert msg.commentaires[1].reference_cnut == "REF006B"

    def test_error_message_types(self, ane_lines: list[str]) -> None: # pylint: disable=redefined-outer-name
        """Valide que les types d'erreur (ANE/AST) sont bien différenciés."""
        messages = parse_gencod_lines(ane_lines)
        msg = messages[0]

        # Pour ANE (913) et AST (914), le commentaire doit être GencodCommentaireErreur
        assert all(isinstance(c, GencodCommentaireErreur) for c in msg.commentaires)
