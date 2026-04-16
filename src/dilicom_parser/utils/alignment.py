"""Module d'alignement des données pour les dataclasses du distributeur"""

from typing import Union, List, Any
import pandas as pd

def fix_alignment(row: Union[pd.Series, List[Any]], expected_len: int) -> List[Any]:
    """Ajuste l'alignement d'une ligne de données en fonction de la longueur attendue.
    Si la ligne a plus de valeurs que prévu, les valeurs excédentaires sont ignorées.
    Si la ligne a moins de valeurs que prévu, des valeurs None sont ajoutées pour compléter la ligne

    Args:
    - row: La ligne de données à ajuster (pandas Series ou liste).
    - expected_len: La longueur attendue de la ligne après ajustement.
    Returns:
    - La ligne de données ajustée avec la longueur attendue.
    """
    values = list(row)
    if len(values) > expected_len:
        values = values[:expected_len]
    if len(values) < expected_len:
        values += [None] * (expected_len - len(values))
    return values
