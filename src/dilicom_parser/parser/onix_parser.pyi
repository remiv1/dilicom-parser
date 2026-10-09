from typing import Iterator

from onixlib import Notice, Product

from ..models.classifier import FileContent


class OnixParser:
    file_contents: list[FileContent]
    def __init__(self, file_contents: list[FileContent]) -> None: ...
    def iter_products(self) -> Iterator[Product]: ...
    def parse(self) -> list[Notice]: ...
