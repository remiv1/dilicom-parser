"""Tests unitaires pour le DistributorParser."""

from pathlib import Path

import pytest

from src.dilicom_parser.parser.distributor_parser import DistributorParser
from src.dilicom_parser.models import FileHeader, FileContent
from src.dilicom_parser.models.distributor import (
    DistributorData,
    DistributorDataBloc1,
    DistributorDataBloc2,
    DistributorDataBloc3,
    DistributorLineData
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_data_row(
    ref: str = "L000001",
    mvt: str = "03",
    gln: str = "3019000602807",
) -> list[str]:
    """Retourne une ligne de données distributeur réaliste (45 champs)."""
    bloc1 = [
        ref, mvt, gln, "EDWARDA EDITIONS", "",
        "44", "RUE DES ACACIAS", "", "", "75017",
        "PARIS", "FRANCE", "", "06 98 93 33 66", "",
        "s.guelimi@gmail.com", "www.edwarda.fr", "51244645100035",
        "", "", "", "01", "0",
    ]
    bloc2 = ["00", "00", "", "", "", "02", "01"]
    bloc3 = ["02", "1", "0", "1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    fin = ["FIN"]
    return bloc1 + bloc2 + bloc3 + fin


def _make_file_content(
    file_type: str = "distributor",
    data: list[list[str]] | None = None,
    ref_file: str = "L000000",
    type_file: str = "Distrib_DLC_11042026",
    date_file: str = "11042026",
) -> FileContent:
    """Crée un FileContent avec des valeurs réalistes."""
    header = FileHeader(ref_file=ref_file, type_file=type_file, date_file=date_file)
    if data is None:
        data = [_make_data_row()]
    return FileContent(header=header, data=data, footer="F999999", file_type=file_type)


# ---------------------------------------------------------------------------
# Tests : initialisation
# ---------------------------------------------------------------------------

class TestDistributorParserInit:
    """Tests du constructeur du DistributorParser."""

    def test_init_with_distributor_files(self) -> None:
        """L'initialisation accepte des fichiers de type 'distributor'."""
        fc = _make_file_content()
        parser = DistributorParser([fc])

        assert len(parser.files_data) == 1
        assert not parser.distributor_data

    def test_init_rejects_non_distributor(self) -> None:
        """L'initialisation lève ValueError si un fichier n'est pas 'distributor'."""
        fc = _make_file_content(file_type="unknown")

        with pytest.raises(ValueError, match="type 'distributor'"):
            DistributorParser([fc])

    def test_init_rejects_mixed_types(self) -> None:
        """L'initialisation lève ValueError si les types sont mélangés."""
        fc_ok = _make_file_content(file_type="distributor")
        fc_bad = _make_file_content(file_type="unknown")

        with pytest.raises(ValueError):
            DistributorParser([fc_ok, fc_bad])


# ---------------------------------------------------------------------------
# Tests : parse()
# ---------------------------------------------------------------------------

class TestDistributorParserParse:
    """Tests de la méthode parse()."""

    def test_parse_single_line(self) -> None:
        """Parse un fichier avec une seule ligne de données."""
        fc = _make_file_content()
        parser = DistributorParser([fc])
        parser.parse()

        assert len(parser.distributor_data) == 1
        dist = parser.distributor_data[0]
        assert isinstance(dist, DistributorData)
        assert len(dist.lines) == 1

    def test_parse_multiple_lines(self) -> None:
        """Parse un fichier avec plusieurs lignes de données."""
        row1 = _make_data_row()
        row2 = _make_data_row(ref="L000002", gln="3019000603507")
        fc = _make_file_content(data=[row1, row2])
        parser = DistributorParser([fc])
        parser.parse()

        assert len(parser.distributor_data) == 1
        assert len(parser.distributor_data[0].lines) == 2

    def test_parse_multiple_files(self) -> None:
        """Parse plusieurs fichiers indépendamment."""
        fc1 = _make_file_content()
        fc2 = _make_file_content()
        parser = DistributorParser([fc1, fc2])
        parser.parse()

        assert len(parser.distributor_data) == 2

    def test_parse_resets_previous_data(self) -> None:
        """Un second appel à parse() réinitialise les données."""
        fc = _make_file_content()
        parser = DistributorParser([fc])
        parser.parse()
        parser.parse()

        assert len(parser.distributor_data) == 1

    def test_parse_header_fields(self) -> None:
        """Les métadonnées du header sont correctement extraites."""
        fc = _make_file_content(ref_file="L000000", date_file="11042026")
        parser = DistributorParser([fc])
        parser.parse()

        dist = parser.distributor_data[0]
        assert dist.debut_fichier == "L000000"
        assert dist.ref_edi == "L000000"
        assert dist.date_edi == 11042026

    def test_parse_footer(self) -> None:
        """Le footer est correctement conservé."""
        fc = _make_file_content()
        parser = DistributorParser([fc])
        parser.parse()

        assert parser.distributor_data[0].fin_fichier == "F999999"

    def test_parse_non_numeric_date(self) -> None:
        """Une date non numérique donne date_edi = 0."""
        fc = _make_file_content(date_file="ABCDEF")
        parser = DistributorParser([fc])
        parser.parse()

        assert parser.distributor_data[0].date_edi == 0


# ---------------------------------------------------------------------------
# Tests : extraction des blocs
# ---------------------------------------------------------------------------

class TestDistributorParserBlocs:
    """Tests de l'extraction des blocs de données."""

    @pytest.fixture()
    def parsed_line(self):
        """Retourne la première ligne parsée d'un fichier à une ligne."""
        fc = _make_file_content()
        parser = DistributorParser([fc])
        parser.parse()
        return parser.distributor_data[0].lines[0]

    def test_bloc1_fields(self, parsed_line: DistributorLineData) -> None:
        """Les champs du bloc 1 sont correctement extraits."""
        b1 = parsed_line.bloc1
        assert isinstance(b1, DistributorDataBloc1)
        assert b1.ref == "L000001"
        assert b1.mvt == "03"
        assert b1.gln == "3019000602807"
        assert b1.rs1 == "EDWARDA EDITIONS"
        assert b1.rs2 == ""
        assert b1.numero_voie == "44"
        assert b1.adresse_l1 == "RUE DES ACACIAS"
        assert b1.adresse_l2 == ""
        assert b1.adresse_l3 == ""
        assert b1.code_postal == "75017"
        assert b1.ville == "PARIS"
        assert b1.pays == "FRANCE"
        assert b1.fonction == "01"
        assert b1.adherent_prisme == "0"

    def test_bloc2_fields(self, parsed_line: DistributorLineData) -> None:
        """Les champs du bloc 2 sont correctement extraits."""
        b2 = parsed_line.bloc2
        assert isinstance(b2, DistributorDataBloc2)
        assert b2.integration_commande == "00"
        assert b2.place_commande == "00"
        assert b2.heure_limite == ""
        assert b2.jours_collecte == ""
        assert b2.format_commandes == ""
        assert b2.type_connection == "02"
        assert b2.avis_expedition == "01"

    def test_bloc3_fields(self, parsed_line: DistributorLineData) -> None:
        """Les champs du bloc 3 sont correctement extraits."""
        b3 = parsed_line.bloc3
        assert isinstance(b3, DistributorDataBloc3)
        assert b3.fiche_produit == "02"
        assert b3.propo_commandes == "1"
        assert b3.commande == "0"
        assert b3.reponse_commandes == "1"
        assert b3.avis_exp_v1 == "0"
        assert b3.avis_exp_v2 == "0"
        assert b3.journal_mvt == "0"

    def test_fin_ligne(self, parsed_line: DistributorLineData) -> None:
        """Le champ fin_ligne est correctement extrait."""
        assert parsed_line.fin_ligne == "FIN"


# ---------------------------------------------------------------------------
# Tests : cas limites
# ---------------------------------------------------------------------------

class TestDistributorParserEdgeCases:
    """Tests des cas limites."""

    def test_parse_with_empty_data(self) -> None:
        """Un FileContent sans données produit un DistributorData avec 0 lignes."""
        fc = _make_file_content(data=[])
        parser = DistributorParser([fc])
        parser.parse()

        assert len(parser.distributor_data) == 1
        assert len(parser.distributor_data[0].lines) == 0

    def test_parse_with_fixture_file(self) -> None:
        """Intégration : lecture et parsing du fichier fixture distributor_valid.txt."""
        fixture = FIXTURES_DIR / "distributor_valid.txt"
        with fixture.open("r", encoding="cp1252") as fh:
            lines = fh.readlines()
        header_parts = lines[0].strip().split(";")
        header = FileHeader(
            ref_file=header_parts[0],
            type_file=header_parts[1],
            date_file=header_parts[2],
        )
        footer = lines[-1].strip()
        data = [line.strip().split(";") for line in lines[1:-1]]
        fc = FileContent(header=header, data=data, footer=footer, file_type="distributor")

        parser = DistributorParser([fc])
        parser.parse()

        assert len(parser.distributor_data) == 1
        dist = parser.distributor_data[0]
        assert len(dist.lines) == 3
        assert dist.lines[0].bloc1.gln == "3019000602807"
        assert dist.lines[1].bloc1.gln == "3019000603507"
        assert dist.lines[2].bloc1.gln == "3019007662903"
        assert dist.lines[0].bloc1.rs1 == "EDWARDA EDITIONS"
        assert dist.lines[1].bloc1.rs1 == "LES OMBRES DU SOIR"
        assert dist.lines[2].bloc1.rs1 == "EDITIONS DU FIGUIER"
        assert dist.fin_fichier == "F999999"
        assert dist.date_edi == 11042026

    def test_parse_with_empty_fixture_file(self) -> None:
        """Intégration : parsing du fichier fixture vide (header + footer seulement)."""
        fixture = FIXTURES_DIR / "distributor_empty.txt"
        with fixture.open("r", encoding="cp1252") as fh:
            lines = fh.readlines()
        header_parts = lines[0].strip().split(";")
        header = FileHeader(
            ref_file=header_parts[0],
            type_file=header_parts[1],
            date_file=header_parts[2],
        )
        footer = lines[-1].strip()
        data = [line.strip().split(";") for line in lines[1:-1]]
        fc = FileContent(header=header, data=data, footer=footer, file_type="distributor")

        parser = DistributorParser([fc])
        parser.parse()

        assert len(parser.distributor_data) == 1
        dist = parser.distributor_data[0]
        assert len(dist.lines) == 0
        assert dist.fin_fichier == "F999999"
        assert dist.date_edi == 12042026
