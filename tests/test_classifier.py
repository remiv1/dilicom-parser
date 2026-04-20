"""Tests unitaires pour le FilesClassifier."""

from pathlib import Path

from src.dilicom_parser.classifier import FilesClassifier
from src.dilicom_parser.models import FileHeader


FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Helpers : création de fichiers temporaires
# ---------------------------------------------------------------------------

def _write_file(tmp_path: Path, name: str, lines: list[str], encoding: str = "cp1252") -> Path:
    """Écrit un fichier temporaire avec les lignes données."""
    p = tmp_path / name
    p.write_text("\n".join(lines), encoding=encoding)
    return p


def _make_distributor_lines() -> list[str]:
    """Retourne les lignes d'un fichier distributeur valide (header + 1 data + footer)."""
    header = "L000000;Distrib_DLC_11042026;11042026"
    data = (
        "L000001;03;3019000602807;EDWARDA EDITIONS;;44;RUE DES ACACIAS;;;75017;PARIS;FRANCE;"
        ";06 98 93 33 66;;s.guelimi@gmail.com;www.edwarda.fr;51244645100035;"
        ";;;01;0;00;00;;;02;01;02;1;0;1;0;0;0;0;0;0;0;0;0;0;0;FIN"
    )
    footer = "F999999"
    return [header, data, footer]


# ---------------------------------------------------------------------------
# Tests : initialisation et lecture
# ---------------------------------------------------------------------------

class TestFilesClassifierInit:
    """Tests de l'initialisation et de la lecture des fichiers."""

    def test_init_with_valid_file(self, tmp_path: Path) -> None:
        """Un fichier valide est lu et produit un FileContent."""
        f = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        classifier = FilesClassifier([f])

        assert len(classifier.contents) == 1
        content = classifier.contents[0]
        assert isinstance(content.header, FileHeader)
        assert content.header.ref_file == "L000000"
        assert content.header.type_file == "Distrib_DLC_11042026"
        assert content.header.date_file == "11042026"
        assert content.footer == "F999999"
        assert len(content.data) == 1  # 1 ligne de données

    def test_init_with_multiple_files(self, tmp_path: Path) -> None:
        """Plusieurs fichiers sont lus indépendamment."""
        f1 = _write_file(tmp_path, "a.txt", _make_distributor_lines())
        f2 = _write_file(tmp_path, "b.txt", _make_distributor_lines())
        classifier = FilesClassifier([f1, f2])

        assert len(classifier.contents) == 2

    def test_init_skips_non_file_path(self, tmp_path: Path) -> None:
        """Un répertoire dans la liste est silencieusement ignoré."""
        d = tmp_path / "subdir"
        d.mkdir()
        classifier = FilesClassifier([d])

        assert len(classifier.contents) == 0

    def test_init_with_empty_list(self) -> None:
        """Une liste vide ne produit aucun contenu."""
        classifier = FilesClassifier([])
        assert len(classifier.contents) == 0


# ---------------------------------------------------------------------------
# Tests : classify()
# ---------------------------------------------------------------------------

class TestFilesClassifierClassify:
    """Tests de la méthode classify()."""

    def test_classify_distributor(self, tmp_path: Path) -> None:
        """Un fichier Distrib_DLC est classé comme 'distributor'."""
        f = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        classifier = FilesClassifier([f]).classify()

        assert classifier.contents[0].file_type == "distributor"

    def test_classify_unknown_type(self, tmp_path: Path) -> None:
        """Un fichier avec un type d'en-tête inconnu reste 'unknown'."""
        lines = [
            "L000000;TypeInconnu;20250415",
            "data;line",
            "FIN",
        ]
        f = _write_file(tmp_path, "unknown.txt", lines)
        classifier = FilesClassifier([f]).classify()

        assert classifier.contents[0].file_type == "unknown"

    def test_classify_returns_self(self, tmp_path: Path) -> None:
        """classify() retourne l'instance pour permettre le chaînage."""
        f = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        classifier = FilesClassifier([f])
        result = classifier.classify()

        assert result is classifier


# ---------------------------------------------------------------------------
# Tests : count_by_type()
# ---------------------------------------------------------------------------

class TestFilesClassifierCountByType:
    """Tests de la méthode count_by_type()."""

    def test_count_single_type(self, tmp_path: Path) -> None:
        """Comptage avec un seul type de fichier."""
        f1 = _write_file(tmp_path, "a.txt", _make_distributor_lines())
        f2 = _write_file(tmp_path, "b.txt", _make_distributor_lines())
        classifier = FilesClassifier([f1, f2]).classify()

        counts = classifier.count_by_type()
        assert counts == {"distributor": 2}

    def test_count_mixed_types(self, tmp_path: Path) -> None:
        """Comptage avec des types mélangés (distributor + unknown)."""
        f1 = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        lines_unknown = ["L000000;Autre;20250415", "x;y", "FIN"]
        f2 = _write_file(tmp_path, "other.txt", lines_unknown)
        classifier = FilesClassifier([f1, f2]).classify()

        counts = classifier.count_by_type()
        assert counts["distributor"] == 1
        assert counts["unknown"] == 1

    def test_count_empty(self) -> None:
        """Comptage sans aucun fichier."""
        classifier = FilesClassifier([])
        assert not classifier.count_by_type()


# ---------------------------------------------------------------------------
# Tests : get_files_by_type()
# ---------------------------------------------------------------------------

class TestFilesClassifierGetFilesByType:
    """Tests de la méthode get_files_by_type()."""

    def test_get_distributor_files(self, tmp_path: Path) -> None:
        """Filtrage par type 'distributor'."""
        f1 = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        lines_unknown = ["L000000;Autre;20250415", "x;y", "FIN"]
        f2 = _write_file(tmp_path, "other.txt", lines_unknown)
        classifier = FilesClassifier([f1, f2]).classify()

        distributors = classifier.get_files_by_type("distributor")
        assert len(distributors) == 1
        assert distributors[0].file_type == "distributor"

    def test_get_nonexistent_type(self, tmp_path: Path) -> None:
        """Filtrage par un type absent retourne une liste vide."""
        f = _write_file(tmp_path, "distrib.txt", _make_distributor_lines())
        classifier = FilesClassifier([f]).classify()

        assert classifier.get_files_by_type("inexistant") == []
