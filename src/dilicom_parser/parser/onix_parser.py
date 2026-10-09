"""Parsing des notices ONIX avec onixlib."""

from typing import Iterator

from onixlib import Notice, Product, parse as parse_onix

from ..models.classifier import FileContent


class OnixParser:
    """Parse les fichiers ONIX classifiés."""

    def __init__(self, file_contents: list[FileContent]) -> None:
        """Conserve les fichiers ONIX à parser.

        Args:
            file_contents: Fichiers ONIX classifiés.
        """
        self.file_contents = file_contents

    def iter_products(self) -> Iterator[Product]:
        """Parcourt les produits de chaque fichier ONIX sans charger la notice.

        Yields:
            Produits onixlib parsés à la demande.

        Raises:
            ValueError: Si un fichier n'a pas de chemin source.
        """
        for content in self.file_contents:
            if content.source_path is None:
                raise ValueError("Chemin source manquant pour un fichier ONIX.")
            yield from parse_onix(content.source_path)

    def parse(self) -> list[Notice]:
        """Retourne une notice onixlib par fichier.

        Returns:
            Notices ONIX parsées.

        Raises:
            ValueError: Si un fichier n'a pas de chemin source.
        """
        notices: list[Notice] = []
        for content in self.file_contents:
            if content.source_path is None:
                raise ValueError("Chemin source manquant pour un fichier ONIX.")
            notices.append(Notice.parse_full(content.source_path))
        return notices