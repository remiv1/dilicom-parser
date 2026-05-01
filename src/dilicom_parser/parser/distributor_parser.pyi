from ..models.classifier import FileContent as FileContent
from ..models.distributor import DistributorData as DistributorData, DistributorDataBloc1 as DistributorDataBloc1, DistributorDataBloc2 as DistributorDataBloc2, DistributorDataBloc3 as DistributorDataBloc3, DistributorLineData as DistributorLineData # pylint: disable=unused-import
from _typeshed import Incomplete

logger: Incomplete

class DistributorParser:
    files_data: list[FileContent]
    distributor_data: list[DistributorData]
    def __init__(self, distributor_list: list[FileContent]) -> None: ... # pylint: disable=unused-argument
    def parse(self) -> list[DistributorData]: ...
