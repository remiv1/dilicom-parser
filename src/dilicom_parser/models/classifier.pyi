import pandas as pd
from dataclasses import dataclass

@dataclass
class FileHeader:
    ref_file: str
    type_file: str
    date_file: str

@dataclass
class FileContent:
    header: FileHeader
    data: list[list[str]]
    footer: str
    file_type: str = ...
    df: pd.DataFrame | None = ...
