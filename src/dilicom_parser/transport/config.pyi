from _typeshed import Incomplete
from dataclasses import dataclass
from pathlib import Path

logger: Incomplete

@dataclass
class DilicomConfig:
    host: str
    port: int
    username: str
    password: str
    out_folder: Path
    in_folder: Path

def load_dilicom_config(env_path: str | None = None) -> DilicomConfig: ...
