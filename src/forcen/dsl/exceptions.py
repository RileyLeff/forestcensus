"""Exceptions raised by the DSL parser and applier."""

from __future__ import annotations

from dataclasses import dataclass

from ..exceptions import ForcenError


@dataclass
class DSLParseError(ForcenError):
    """Raised when a DSL line fails to parse."""

    line_no: int
    line: str
    detail: str

    def __post_init__(self) -> None:
        message = f"line {self.line_no}: {self.detail.strip()}"
        super().__init__(message)


class DSLSemanticError(ForcenError):
    """Raised when DSL commands violate semantic constraints."""

    def __init__(self, line_no: int, message: str):
        self.line_no = line_no
        super().__init__(f"line {line_no}: {message}")


class AliasOverlapError(DSLSemanticError):
    """Raised when an alias binding conflicts with an existing binding."""


class PrimaryConflictError(DSLSemanticError):
    """Raised when PRIMARY assignments overlap for the same tree."""
