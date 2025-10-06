"""Shared validation issue types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ValidationSeverity = Literal["error", "warning"]


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: ValidationSeverity
    message: str
    location: str

    def is_error(self) -> bool:
        return self.severity == "error"
