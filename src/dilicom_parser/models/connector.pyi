from dataclasses import dataclass
from datetime import datetime

@dataclass
class RemoteFile:
    filename: str
    filepath: str
    size: int | None
    modified_time: datetime | None
