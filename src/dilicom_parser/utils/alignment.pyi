import pandas as pd
from typing import Any

def fix_alignment(row: pd.Series | list[Any], expected_len: int) -> list[Any]: ...
