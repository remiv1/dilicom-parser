from ..models import FileContent as FileContent, FileHeader as FileHeader, ParserConfig as ParserConfig # pylint: disable=unused-import
from ..utils import ParsersRegistry as ParsersRegistry # pylint: disable=unused-import
from _typeshed import Incomplete
from pathlib import Path
from typing import Any

logger: Incomplete

class FilesClassifier:
    STREAMING_FILE_SIZE_THRESHOLD_BYTES: Incomplete
    streaming_option: Incomplete
    heavy_files: list[Path]
    file_list: Incomplete
    contents: list[FileContent]
    parsers_registry: Incomplete
    parser_config: ParserConfig
    def __init__(self, file_list: list[Path], streaming_option: bool = True) -> None: ... # pylint: disable=unused-argument
    def classify(self) -> FilesClassifier: ...
    def count_by_type(self) -> dict[str, int]: ...
    def get_files_by_type(self, file_type: str) -> list[FileContent]: ... # pylint: disable=unused-argument
    def parse(self) -> dict[str, list[Any]]: ...
