"""Module de classement des fichiers reçus depuis le serveur FTP de Dilicom."""

import warnings
from typing import List, Any
import logging
from pathlib import Path
import zipfile
from ..models import FileHeader, FileContent, ParserConfig
from ..utils import ParsersRegistry

logger = logging.getLogger(__name__)


class FilesClassifier:
    """Classe de classification et d'extraction des fichiers reçus depuis le serveur FTP de Dilicom.

    Cette classe assure la gestion complète du pipeline de traitement des fichiers :
    - Extraction automatique des archives (.zip, .zip.rdy, etc.)
    - Lecture et classification par type de fichier (distributor, eancom, gencod)
    - Basculement automatique en mode streaming si les fichiers dépassent 512 MiB
    - Parsing des données selon le type de fichier détecté

    Attributes:
        file_list (list[Path]): Liste finale des fichiers à traiter après extraction des archives.
        contents (list[FileContent]): Contenus lus et parsés des fichiers.
        heavy_files (list[Path]): Fichiers archives (contenant .zip dans les extensions).
        streaming_option (bool): Mode streaming activé/désactivé (peut être forcé automatiquement).
        parsers_registry (ParsersRegistry): Registre centralisé des parsers disponibles.
        parser_config (ParserConfig): Configuration des parsers.

    Note:
        - Un fichier "livre" (archive) est identifié par la présence de ".zip" dans ses extensions.
        - Supports les formats : .zip, .zip.rdy, .zip.rdy.csv, etc.
        - Les archives sont automatiquement supprimées après extraction réussie.
        - Le streaming est forcé si un fichier non-zippé dépasse 512 MiB.
    """

    STREAMING_FILE_SIZE_THRESHOLD_BYTES = 512 * 1024 * 1024

    def __init__(self, file_list: list[Path], streaming_option: bool = True) -> None:
        """Initialise le classifieur et prépare les fichiers pour le traitement.

        Enchaîne les opérations suivantes :
        1. Extraction des archives (.zip, .zip.rdy, etc.)
        2. Lecture des contenus des fichiers extraits
        3. Résolution du mode streaming (forçage si fichiers > 512 MiB)

        Args:
            file_list (list[Path]): Liste des chemins de fichiers/archives à traiter.
                                   Peut contenir des archives .zip et des fichiers ordinaires.
            streaming_option (bool, optional): Active le mode streaming par défaut.
                                             Peut être forcé automatiquement si nécessaire.
                                             Défaut: True.

        Raises:
            Aucune exception levée directement, mais les erreurs d'extraction/lecture
            sont loggées en WARNING et les fichiers problématiques sont ignorés.

        Example:
            >>> from pathlib import Path
            >>> files = [Path("archive.zip"), Path("data.txt")]
            >>> classifier = FilesClassifier(files, streaming_option=False)
            >>> classifier.classify()
            >>> results = classifier.parse()
        """
        self.streaming_option = streaming_option
        self.heavy_files: list[Path] = []
        self.file_list = self.__prepare_files(file_list)
        self.contents: list[FileContent] = self.__get_content()
        self.parsers_registry = ParsersRegistry()
        self.parser_config: ParserConfig
        self.streaming_option = self.__resolve_streaming_option(streaming_option)

    def __prepare_files(self, file_list: list[Path]) -> list[Path]:
        """Dézippe les archives et retourne la liste finale des fichiers à traiter.

        Pour chaque fichier d'entrée :
        - Si c'est une archive (.zip dans les suffixes) :
          * Crée un dossier d'extraction nommé d'après le radical du fichier.
          * Extrait le contenu dans ce dossier.
          * Ajoute tous les fichiers extraits à la liste finale.
          * Supprime l'archive source après succès.
        - Sinon, ajoute le fichier tel quel à la liste finale.

        Args:
            file_list (list[Path]): Liste initiale de fichiers/archives.

        Returns:
            list[Path]: Liste des fichiers finaux à traiter (incluant les fichiers extraits).
                       Les archives originales sont supprimées de cette liste.

        Note:
            - Les archives invalides ou corrompues sont loggées en WARNING et ignorées.
            - Les fichiers qui ne sont pas des archives ordinaires sont silencieusement ignorés.
        """
        prepared_files: list[Path] = []

        for f in file_list:
            if not self.__is_book_archive(f):
                prepared_files.append(f)
                continue

            self.heavy_files.append(f)

            if not f.is_file():
                logger.warning("Archive ignorée (chemin invalide): %s", f)
                continue

            extracted_dir_name = self.__get_extracted_dir_name(f)
            extracted_dir = f.parent / extracted_dir_name

            try:
                extracted_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(f, "r") as archive:
                    archive.extractall(extracted_dir)

                extracted_files = [path for path in extracted_dir.rglob("*") if path.is_file()]
                prepared_files.extend(extracted_files)

                f.unlink()
                logger.info(
                    "Archive extraite: %s vers %s (%d fichier(s)). Archive supprimée.",
                    f,
                    extracted_dir,
                    len(extracted_files),
                )
            except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as err:
                logger.warning("Impossible d'extraire l'archive %s: %s", f, err)

        return prepared_files

    def __is_book_archive(self, file_path: Path) -> bool:
        """Détecte si un fichier est une archive (livre) selon ses extensions.

        Règle métier : Un fichier est considéré comme une archive si ".zip" (insensible à la casse)
        apparaît dans la liste de ses extensions.

        Exemples de fichiers considérés comme des archives :
        - archive.zip
        - data.zip.rdy
        - file.zip.rdy.csv
        - BACKUP.ZIP

        Args:
            file_path (Path): Chemin du fichier à vérifier.

        Returns:
            bool: True si ".zip" est trouvé dans les extensions, False sinon.
        """
        return ".zip" in (suffix.lower() for suffix in file_path.suffixes)

    def __get_extracted_dir_name(self, file_path: Path) -> str:
        """Construit le nom du dossier d'extraction en isolant le radical du fichier.

        Utilise la première occurrence de ".zip" (insensible à la casse) comme point de coupe.

        Exemples :
        - "DIF489084922.zip.rdy" → "DIF489084922"
        - "data.zip" → "data"
        - "archive.ZIP" → "archive"
        - "file.zip.rdy.csv" → "file"

        Args:
            file_path (Path): Chemin du fichier archive.

        Returns:
            str: Le radical du nom (partie avant la première occurrence de ".zip").
                En cas de fallback (ne devrait pas arriver), retourne file_path.stem.
        """
        archive_name = file_path.name
        zip_index = archive_name.lower().find(".zip")
        if zip_index > 0:
            return archive_name[:zip_index]
        return file_path.stem

    def __resolve_streaming_option(self, streaming_option: bool) -> bool:
        """Résout le mode streaming avec détection automatique des fichiers volumineux.

        Basculement automatique au mode streaming (True) si :
        - L'utilisateur a demandé le mode non-streaming (streaming_option=False).
        - ET au moins un fichier (non-zippé) dépasse le seuil de 512 MiB.

        En cas de basculement forcé :
        - Log en WARNING avec le(s) fichier(s) problématique(s).
        - Émet un UserWarning pour l'application.

        Args:
            streaming_option (bool): Option de streaming demandée par l'utilisateur.

        Returns:
            bool: Mode streaming résolu (peut être différent de l'entrée).
                  True si forcé ou si demandé, False sinon.

        Note:
            - Seuil : 512 * 1024 * 1024 octets (512 MiB).
            - Les erreurs de lecture de taille sont silencieuses (logged en WARNING).
        """
        oversized_files: list[Path] = []
        for f in self.file_list:
            try:
                if f.is_file() and f.stat().st_size > self.STREAMING_FILE_SIZE_THRESHOLD_BYTES:
                    oversized_files.append(f)
            except OSError as err:
                logger.warning("Impossible de lire la taille du fichier %s: %s", f, err)

        if oversized_files and not streaming_option:
            threshold_mib = self.STREAMING_FILE_SIZE_THRESHOLD_BYTES // (1024 * 1024)
            oversized_names = ", ".join(f.name for f in oversized_files)
            message = (
                f"Mode streaming activé automatiquement: {len(oversized_files)} " +
                f"fichier(s) dépasse(nt) {threshold_mib} MiB ({oversized_names})."
            )
            logger.warning(message)
            warnings.warn(message, UserWarning, stacklevel=2)
            return True

        return streaming_option

    def __get_headers(self, header: str) -> FileHeader:
        """Extrait et valide l'en-tête du fichier selon son format.

        Détecte le format du fichier et construit un objet FileHeader.

        Formats supportés :
        - Distributor (L000000) : Format CSV interne Dilicom.
        - EANCOM (UNB+UNOB) : Format EDIFACT standard.
        - GENCOD (05003) : Format GENCOD Dilicom.

        Args:
            header (str): Première ligne (en-tête) du fichier.

        Returns:
            FileHeader: Objet contenant ref_file, type_file, date_file.

        Raises:
            ValueError: Si l'en-tête ne correspond à aucun format connu.
                       Le message d'erreur liste le format en-tête non reconnu.

        Example:
            >>> header = "L000000;Distrib_DLC_11042026;11042026"
            >>> fh = classifier._FilesClassifier__get_headers(header)
            >>> fh.type_file
            'Distrib_DLC_11042026'
        """
        match header:
            case t if t.startswith("L000000"):
                h = header.strip().split(";")
                file_header = FileHeader(ref_file=h[0], type_file=h[1], date_file=h[2])
            case t if t.startswith("UNB+UNOB"):
                h = header
                file_header = FileHeader(ref_file=h, type_file="EANCOM", date_file="")
            case t if t.startswith("05003"):
                h = header
                file_header = FileHeader(ref_file=h, type_file="GENCOD", date_file="")
            case _:
                message = f"En-tête de fichier non reconnu: {header}"
                logger.error(message)
                raise ValueError(message)
        return file_header

    def __get_content(self) -> List[FileContent]:
        """Lit tous les fichiers de la liste et extrait leurs contenus structurés.

        Pour chaque fichier ordinaire (non-répertoire) :
        1. Lit les lignes en encodage cp1252.
        2. Parse l'en-tête (première ligne).
        3. Extrait le pied de page (dernière ligne).
        4. Formate les données intermédiaires selon le type :
           - Format CSV (Distributor) : chaque ligne est une liste splitée par ";".
           - Formats texte (EANCOM, GENCOD) : chaque ligne est un élément unique.
        5. Construit un objet FileContent pour chaque fichier valide.

        Returns:
            List[FileContent]: Liste des objets FileContent des fichiers valides.
                              Les fichiers en erreur sont loggés en WARNING et ignorés.

        Note:
            - Encodage : cp1252 (norme française Dilicom).
            - Les erreurs d'en-tête ou d'encodage ne bloquent pas le traitement global.
        """
        contents: list[FileContent] = []
        for f in self.file_list:
            if f.is_file():
                try:
                    with f.open("r", encoding="cp1252", newline="") as file:
                        lines = file.readlines()
                        header = self.__get_headers(lines[0])
                        footer = lines[-1].strip()

                        # Format CSV (Distributor) : splitter par ";"
                        # Autres formats (EANCOM, GENCOD) : garder les lignes entières
                        if "Distrib_DLC" in header.type_file:
                            # Format CSV : chaque ligne devient une liste
                            data = [line.strip().split(";") for line in lines[1:-1]]
                        else:
                            # Format texte/EDIFACT : chaque ligne est un élément unique
                            data = [[line.strip()] for line in lines[1:-1]]

                        content = FileContent(header=header, data=data, footer=footer)
                        contents.append(content)
                        logger.debug(
                            "Fichier lu: %s, en-tête: %s, nombre de lignes de données: %d",
                            f.name,
                            header,
                            len(data),
                        )
                except ValueError as e:
                    logger.warning(
                        "Fichier ignoré (en-tête ou encodage non reconnu): %s — %s",
                        f.name,
                        e,
                    )
            else:
                logger.warning("Le chemin %s n'est pas un fichier valide.", f)
        return contents

    def classify(self) -> "FilesClassifier":
        """Classifie tous les fichiers selon leur type (distributor, eancom, gencod, unknown).

        Pour chaque contenu chargé, consulte son en-tête (header.type_file) et
        le mappe à un type connu via la registry des parsers.

        Classification :
        - "Distrib_DLC" → type "distributor"
        - "EANCOM" → type "eancom"
        - "GENCOD" → type "gencod"
        - Tout autre → type "unknown"

        Retourne self pour permettre le chaînage des appels.

        Returns:
            FilesClassifier: L'instance elle-même (self).

        Note:
            - Les fichiers de type "unknown" ne seront pas parsés en cas d'appel à parse().
            - Chaque fichier est loggé avec son type détecté en DEBUG.
        """
        headers_and_types = self.parsers_registry.get_headers_and_types()

        for content in self.contents:
            match content.header.type_file:
                case t if any(k in t for k in headers_and_types):
                    file_type = next(v for k, v in headers_and_types.items() if k in t)
                    logger.debug(
                        "En-tête reconnu: %s, type de fichier: %s",
                        content.header.type_file,
                        file_type,
                    )
                    content.file_type = file_type
                case _:
                    logger.warning(
                        "En-tête non reconnu: %s. Type de fichier inconnu.",
                        content.header.type_file
                    )
        return self

    def count_by_type(self) -> dict[str, int]:
        """Compte et retourne le nombre de fichiers classifiés par type.

        Parcourt tous les contenus et agrège le compte par type de fichier.
        Le résultat est loggé au niveau INFO.

        Returns:
            dict[str, int]: Dictionnaire {type_fichier: count}.
                           Exemples : {"distributor": 5, "eancom": 2, "unknown": 1}

        Example:
            >>> counts = classifier.count_by_type()
            >>> print(counts)
            {'distributor': 9, 'eancom': 5, 'gencod': 4}
        """
        counts: dict[str, int] = {}
        for content in self.contents:
            counts[content.file_type] = counts.get(content.file_type, 0) + 1
        logger.info("Nombre de fichiers par type: %s", counts)
        return counts

    def get_files_by_type(self, file_type: str) -> list[FileContent]:
        """Récupère et filtre tous les fichiers d'un type spécifique.

        Le résultat est loggé au niveau INFO.

        Args:
            file_type (str): Nom du type à filtrer (ex: "distributor", "eancom", "unknown").

        Returns:
            list[FileContent]: Liste des objets FileContent du type demandé.
                              Liste vide si aucun fichier ne correspond.

        Example:
            >>> distributors = classifier.get_files_by_type("distributor")
            >>> len(distributors)
            5
        """
        filtered_files = [content for content in self.contents if content.file_type == file_type]
        logger.info("Nombre de fichiers de type '%s': %d", file_type, len(filtered_files))
        return filtered_files

    def parse(self) -> dict[str, list[Any]]:
        """Parse tous les fichiers selon leur type reconnu en utilisant la registry des parsers.

        Prérequis : classify() doit être appelé avant parse().

        Workflow :
        1. Vérifie qu'au moins un fichier a été classifié.
        2. Pour chaque type connu :
           - Récupère les fichiers du type.
           - Instancie le parser approprié.
           - Appelle sa méthode parse().
           - Stocke les résultats.
        3. En cas d'erreur, log l'erreur et retourne une liste vide pour ce type.

        Returns:
            dict[str, list[Any]]: Résultats organisés par type de fichier.
                                 Exemple : {"distributor": [...], "eancom": [...], "gencod": [...]}
                                 Les types sans fichier ou en erreur ont une liste vide.

        Raises:
            ValueError: Si aucun fichier n'a été classifié (tous de type "unknown").
                       Message : "Aucun fichier classifié avant le parsing. Appelez classify() d'abord."

        Example:
            >>> classifier = FilesClassifier([Path("file.txt")]).classify()
            >>> results = classifier.parse()
            >>> results.get("distributor")
            [DistributorData(...), DistributorData(...)]
        """
        if not any(c.file_type != "unknown" for c in self.contents):
            message = "Aucun fichier classifié avant le parsing. Appelez classify() d'abord."
            logger.error(message)
            raise ValueError(message)

        parsed_results: dict[str, list[Any]] = {}

        for file_type in self.parsers_registry.list_types():
            files_of_type = self.get_files_by_type(file_type)

            if not files_of_type:
                logger.debug("Aucun fichier classifié du type '%s'", file_type)
                continue

            try:
                parser_class = self.parsers_registry.get_parser(file_type)
                logger.info("Parsing de %d fichier(s) de type '%s'", len(files_of_type), file_type)

                # Tous les parsers prennent une liste de FileContent en __init__
                # et disposent d'une méthode parse()
                parsed_data = parser_class(files_of_type).parse()
                parsed_results[file_type] = parsed_data

                logger.debug("Parsing réussi pour le type '%s'", file_type)
            except (KeyError, ImportError, ValueError, AttributeError, TypeError) as e:
                logger.error(
                    "Erreur lors du parsing des fichiers de type '%s': %s",
                    file_type,
                    str(e),
                )
                parsed_results[file_type] = []

        return parsed_results
