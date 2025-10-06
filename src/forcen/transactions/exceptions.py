"""Transaction loading and validation errors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..exceptions import ForcenError


class TransactionError(ForcenError):
    """Base class for transaction-related issues."""


@dataclass
class TransactionFormatError(TransactionError):
    path: Path
    message: str

    def __post_init__(self) -> None:
        super().__init__(f"{self.message} ({self.path})")


@dataclass
class TransactionDataError(TransactionError):
    """Raised when measurement data fails normalization."""

    path: Path
    row: int
    column: str
    message: str

    def __post_init__(self) -> None:
        location = f"{self.path.name}:row {self.row},col {self.column}"
        super().__init__(f"{location}: {self.message}")
