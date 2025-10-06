"""Custom exception hierarchy for forcen."""

from __future__ import annotations

from pathlib import Path


class ForcenError(Exception):
    """Base error for the forcen package."""


class ConfigError(ForcenError):
    """Raised when a configuration file fails validation."""

    def __init__(self, path: Path, message: str):
        self.path = Path(path)
        self.message = message
        super().__init__(f"{self.path.name}: {self.message}")
