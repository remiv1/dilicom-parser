"""Exceptions et avertissements du parseur Dilicom."""


class SegmentInconnuWarning(UserWarning):
    """Avertissement levé lorsqu'un segment ou un qualificatif inattendu est
    rencontré pendant le parsing.

    Ce warning ne bloque pas le parsing : les données connues sont extraites
    normalement, le segment ou la valeur inconnue est ignoré(e). Il permet
    néanmoins à l'appelant d'être alerté d'une dérive éventuelle du format.

    Utilisation typique :

        import warnings
        from dilicom_parser.utils.exceptions import SegmentInconnuWarning

        # Transformer le warning en erreur (mode strict) :
        warnings.filterwarnings("error", category=SegmentInconnuWarning)

        # Rediriger vers le système de logging :
        logging.captureWarnings(True)
    """
