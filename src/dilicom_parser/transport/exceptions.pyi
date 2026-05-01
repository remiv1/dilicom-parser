from typing import LiteralString

class DilicomConnectionError(Exception):
    def stdr_message(self) -> LiteralString: ...

class DilicomAuthenticationError(Exception):
    def stdr_message(self) -> LiteralString: ...

class DilicomSFTPError(Exception):
    def stdr_message(self) -> LiteralString: ...
