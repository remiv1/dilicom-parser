from dataclasses import dataclass

@dataclass
class ParserConfig:
    parser_module: str
    parser_callable: str | None = ...
    header_content: str | None = ...
