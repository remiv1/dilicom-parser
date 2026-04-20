"""Module de parsing des fichiers distributeurs Dilicom."""

from typing import Optional, Any
from dataclasses import fields
import logging
import pandas as pd
from ..models.distributor import (
    DistributorData,
    DistributorLineData,
    DistributorDataBloc1,
    DistributorDataBloc2,
    DistributorDataBloc3,
)
from ..models.classifier import FileContent

logger = logging.getLogger(__name__)


class DistributorParser:    # pylint: disable=too-few-public-methods
    """
    Classe de service pour le parsing des fichiers reçus de Dilicom.
    Cette classe est responsable de :
     - Lire les fichiers depuis un répertoire spécifié.
     - Déterminer le type de fichier en fonction de son en-tête.
     - Extraire les données pertinentes en fonction du type de fichier.
     - Stocker les données extraites dans des structures de données appropriées.

    Attributs :
     - directory : Path - Le répertoire où les fichiers sont stockés.
     - data : Optional[pd.DataFrame] - Les données extraites du fichier.
     - file_path : Optional[Path] - Le chemin complet du fichier en cours de traitement.
     - filename : str - Le nom du fichier en cours de traitement.
     - distributor_data : Optional[DistributorData] - Les données du distributeur extraites.

    Méthodes :
        - __init__() : Initialise les attributs de la classe et crée le répertoire s'il n'existe pas
        - parse() : Parse les fichiers de type 'supplier' et extrait les données
                    (combine _transform_data_to_dataframe() et _df_to_distributor_data()).
        - _transform_data_to_dataframe() : transforme la donnée texte en un DataFrame pandas.
        - _df_to_distributor_data() : Convertit un DataFrame en une instance de DistributorData.
    """

    def __init__(self, distributor_list: list[FileContent]) -> None:
        self.files_data: list[FileContent] = distributor_list
        self.distributor_data: list[DistributorData] = []
        if any(f.file_type != "supplier" for f in distributor_list):
            logger.warning(
                "Certains fichiers ne sont pas de type 'supplier'." \
                " Veuillez vérifier les en-têtes des fichiers."
            )
            raise ValueError("Tous les fichiers doivent être de type 'supplier' pour le parsing.")

    def parse(self) -> None:
        """
        Parse les fichiers de type 'supplier' et extrait les données.

        Args:
            None
        Returns:
            None
        """
        self.distributor_data = []  # Réinitialiser les données du distributeur avant de parser
        for f in self.files_data:
            self._transform_data_to_dataframe()
            parsed_data = self._df_to_distributor_data(f)
            if parsed_data is not None:
                self.distributor_data.append(parsed_data)
            else:
                logger.warning(
                    "Aucune donnée à parser. Veuillez d'abord parser le fichier."
                )

    def _transform_data_to_dataframe(self) -> "DistributorParser":
        """
        Lit le fichier et retourne l'en-tête et les données.

        Args:
            None
        Returns:
            FileDistri: Un objet contenant l'en-tête, le pied de page et les données du fichier.
        """
        for f in self.files_data:
            f.df = pd.DataFrame(f.data)
            logger.debug(
                "Fichier lu: %s, en-tête: %s, nombre de lignes de données: %d",
                f.header.ref_file if f.header else "N/A",
                f.header,
                len(f.data),
            )
        return self


    def __row_to_dataclass_by_position(self, row: pd.Series[Any] | list[Any], cls: Any) -> Any:
        """
        Convertit une ligne de données en une instance d'une dataclass en utilisant
        la position des champs.

        Args:
            row: La ligne de données à convertir (pandas Series ou liste).
            cls: La classe de dataclass dans laquelle convertir la ligne.
        Returns:
            Une instance de la dataclass cls avec les valeurs de la ligne.
        """
        values = list(row)  # valeurs dans l'ordre du DataFrame
        attrs = [f.name for f in fields(cls)]  # attributs dans l'ordre de la dataclass
        kwargs = dict(zip(attrs, values))
        return cls(**kwargs)


    def __split_row_for_dataclasses(
        self, row: pd.Series[Any] | list[Any],
    ) -> tuple[DistributorDataBloc1, DistributorDataBloc2, DistributorDataBloc3]:
        """
        Divise une ligne de données en segments correspondant à plusieurs dataclasses
        en utilisant la position des champs.
        Args:
            row: La ligne de données à diviser (pandas Series ou liste).
        Returns:
            Un tuple d'instances de dataclass correspondant aux segments de la ligne.
        """
        classes = DistributorDataBloc1, DistributorDataBloc2, DistributorDataBloc3
        pos = 0
        result: list[Any] = []
        for cls in classes:
            n = len(fields(cls))
            if isinstance(row, pd.Series):
                segment: pd.Series[Any] | list[Any] = row.iloc[pos : pos + n]
            else:
                segment = row[pos : pos + n]
            result.append(self.__row_to_dataclass_by_position(segment, cls))
            pos += n
        return result[0], result[1], result[2]


    def _df_to_distributor_data(self, data: FileContent) -> Optional[DistributorData]:
        """
        Convertit les data en une instance de DistributorData en utilisant la position des champs.

        Args:
            data: Le FileContent à convertir.
        Returns:
            Une instance de DistributorData avec les données du FileContent,
            ou None si le DataFrame est vide.
        """
        lines: list[DistributorLineData] = []
        if data.df is None:
            message = "Le DataFrame est vide. Impossible de convertir en DistributorData."
            logger.warning(message)
            return None
        header, footer, df = data.header, data.footer, data.df

        for _, row in df.iterrows():
            blocs = self.__split_row_for_dataclasses(row)

            if len(blocs) != 3:
                message = f"""
                3 blocs attendus pour chaque ligne, mais {len(blocs)} ont été trouvés.
                Vérifiez la structure du DataFrame et les dataclasses.
                """
                raise ValueError(message)
            line = DistributorLineData(
                bloc1=blocs[0],
                bloc2=blocs[1],
                bloc3=blocs[2],
                fin_ligne=row.iloc[-1],  # dernière colonne
            )

            lines.append(line)

        head_filed = header.ref_file if header else ""
        ref_filed = header.ref_file if header else ""
        date_filed = int(header.date_file) if header and header.date_file.isdigit() else 0

        return DistributorData(
            debut_fichier=head_filed,
            ref_edi=ref_filed,
            date_edi=date_filed,
            lines=lines,
            fin_fichier=footer,
        )
