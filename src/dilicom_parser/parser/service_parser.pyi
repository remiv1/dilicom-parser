from ..models.classifier import FileContent as FileContent
from ..models.service import EancomInterchange as EancomInterchange, GencodServiceMessage as GencodServiceMessage
from .services.eancom import parse_eancom as parse_eancom # pylint: disable=unused-import
from .services.gencod import parse_gencod_lines as parse_gencod_lines # pylint: disable=unused-import
from _typeshed import Incomplete

logger: Incomplete

class ServiceParser:
    file_contents: Incomplete
    parsed_results: list[list[GencodServiceMessage] | EancomInterchange]
    def __init__(self, file_contents: list[FileContent]) -> None: ... # pylint: disable=unused-argument
    def parse(self) -> list[list[GencodServiceMessage] | EancomInterchange]: ...
