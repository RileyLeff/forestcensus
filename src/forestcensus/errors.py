"""Explicit fatal errors raised by the forest census pipeline."""

from __future__ import annotations


class ForestCensusError(ValueError):
    """Base class for fatal domain/configuration errors."""


class ConfigError(ForestCensusError):
    """Configuration is invalid or incomplete."""


class CorrectionError(ForestCensusError):
    """A configured correction cannot be safely applied."""


class CorrectionMatchError(CorrectionError):
    """A correction selector matched the wrong number of rows."""


class CorrectionUnsafeSelectorError(CorrectionError):
    """A correction selector or assignment is unsafe."""


class IdentityOperationError(ForestCensusError):
    """An identity operation cannot be safely applied."""

