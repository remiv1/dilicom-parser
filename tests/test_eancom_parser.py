"""Tests pour le parseur EANCOM D96A (APERAK)."""

import warnings
from pathlib import Path

import pytest

from src.dilicom_parser.parser import parse_eancom
from src.dilicom_parser.utils.exceptions import SegmentInconnuWarning


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def ate_content() -> str:
    """Charge un message ATE (Avis de traitement) valide."""
    return (FIXTURES_DIR / "eancom_ate_valid.txt").read_text()


@pytest.fixture
def ale_content() -> str:
    """Charge un message ALE (Avis de lecture) valide."""
    return (FIXTURES_DIR / "eancom_ale_valid.txt").read_text()


@pytest.fixture
def ane_content() -> str:
    """Charge un message ANE (Avis de non-émission) avec erreur."""
    return (FIXTURES_DIR / "eancom_ane_with_error.txt").read_text()


@pytest.fixture
def invalid_qualifier_content() -> str:
    """Charge un message avec qualificatif DTM invalide."""
    return (FIXTURES_DIR / "eancom_invalid_qualifier.txt").read_text()


@pytest.fixture
def multiple_messages_content() -> str:
    """Charge un interchange avec plusieurs messages."""
    return (FIXTURES_DIR / "eancom_multiple_messages.txt").read_text()


class TestEancomParserBasics:
    """Tests basiques du parseur EANCOM."""

    def test_parse_ate_message(
        self, ate_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ATE (Avis de traitement)."""
        interchange = parse_eancom(ate_content)

        assert interchange.syntaxe_id == "UNOB"
        assert interchange.syntaxe_version == "2"
        assert interchange.gln_emetteur == "3025590000008"
        assert interchange.gln_destinataire == "3025616805006"
        assert len(interchange.messages) == 1

        msg = interchange.messages[0]
        assert msg.is_ate
        assert not msg.is_ale
        assert not msg.is_erreur
        assert msg.type_acquittement == "AB"
        assert msg.reference_message == "MSG001"
        assert msg.date_creation == "20151230"
        assert msg.format_date_creation == "102"
        assert msg.reference_acquittee == "2015456450123"
        assert len(msg.parties) == 3

    def test_parse_ale_message(
        self, ale_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ALE (Avis de lecture)."""
        interchange = parse_eancom(ale_content)

        assert len(interchange.messages) == 1
        msg = interchange.messages[0]

        assert msg.is_ale
        assert not msg.is_ate
        assert msg.type_acquittement == "AB"
        assert msg.date_lecture == "20151230"
        assert msg.format_date_lecture == "102"
        assert msg.date_traitement == "20151230"
        assert msg.format_date_traitement == "102"

    def test_parse_ane_message_with_error(
        self, ane_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide le parsing d'un message ANE avec erreur."""
        interchange = parse_eancom(ane_content)

        assert len(interchange.messages) == 1
        msg = interchange.messages[0]

        assert msg.is_erreur
        assert not msg.is_ate
        assert not msg.is_ale
        assert msg.type_acquittement == "RE"
        assert msg.erreur is not None
        assert msg.erreur.code_erreur == "7"
        assert msg.erreur.code_identification == "ZZZ"
        assert msg.erreur.libelle_erreur == "Référence inconnue"


class TestEancomParserWarnings:
    """Tests pour la gestion des warnings du parseur."""

    def test_invalid_qualifier_raises_warning(
        self, invalid_qualifier_content: str  # pylint: disable=redefined-outer-name
    ) -> None:
        """Valide qu'un qualificatif DTM invalide lève un SegmentInconnuWarning."""
        with pytest.warns(SegmentInconnuWarning, match="Qualificatif DTM inattendu"):
            interchange = parse_eancom(invalid_qualifier_content)

        # Le parsing continue malgré le warning
        assert len(interchange.messages) == 1
        msg = interchange.messages[0]
        # La date création est présente (DTM 137 a été parsée)
        assert msg.date_creation == "20151230"
        # Mais la date avec le qualificatif 999 n'a pas été assignée nulle part
        assert msg.date_traitement is None
        assert msg.date_lecture is None

    def test_warning_can_be_filtered_as_error(
        self, invalid_qualifier_content: str  # pylint: disable=redefined-outer-name
    ) -> None:
        """Valide qu'on peut configurer le warning comme erreur."""
        with pytest.raises(SegmentInconnuWarning):
            warnings.filterwarnings("error", category=SegmentInconnuWarning)
            try:
                parse_eancom(invalid_qualifier_content)
            finally:
                warnings.filterwarnings("default", category=SegmentInconnuWarning)


class TestEancomParserMultipleMessages:
    """Tests pour les interchanges avec plusieurs messages."""

    def test_parse_multiple_messages(
        self, multiple_messages_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide le parsing d'un interchange avec plusieurs messages."""
        interchange = parse_eancom(multiple_messages_content)

        assert interchange.nombre_messages == "2"
        assert len(interchange.messages) == 2

        msg1 = interchange.messages[0]
        msg2 = interchange.messages[1]

        assert msg1.reference_message == "MSG005"
        assert msg1.date_traitement == "20151230"
        assert msg1.date_lecture is None

        assert msg2.reference_message == "MSG006"
        assert msg2.date_traitement is None
        assert msg2.date_lecture == "20151230"


class TestEancomParserParties:
    """Tests pour la gestion des parties identifiées (NAD)."""

    def test_parse_parties_with_roles(
        self, ate_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide que les parties sont correctement parsées avec leurs rôles."""
        interchange = parse_eancom(ate_content)
        msg = interchange.messages[0]

        assert len(msg.parties) == 3

        # Vérifier les trois rôles
        roles = {p.fonction: p for p in msg.parties}
        assert "SU" in roles  # Fournisseur
        assert "BY" in roles  # Acheteur
        assert "DP" in roles  # Livré à

        # Vérifier les GLN
        assert roles["SU"].gln == "3025590000008"
        assert roles["BY"].gln == "3025616805006"
        assert roles["DP"].gln == "3025616805006"

        # Vérifier le code d'identification (tous en GS1)
        for party in msg.parties:
            assert party.code_identifiant == "9"


class TestEancomParserEdgeCases:
    """Tests pour les cas limites et comportements particuliers."""

    def test_partial_message_fields(
        self, ate_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide que les champs optionnels non présents sont None ou vides."""
        interchange = parse_eancom(ate_content)
        msg = interchange.messages[0]

        # Ces champs ne sont pas dans le message ATE
        assert msg.date_traitement is None
        assert msg.date_lecture is None
        assert msg.erreur is None

    def test_empty_parts_handled_gracefully(
        self, ate_content: str
    ) -> None:  # pylint: disable=redefined-outer-name
        """Valide que les segments partiels ne causent pas d'erreur."""
        # Les segments avec moins que le nombre de parties attendues
        # doivent être gérés sans crash
        interchange = parse_eancom(ate_content)
        assert interchange is not None
