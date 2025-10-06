"""Data models for transaction processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from ..dsl import Command


@dataclass
class MeasurementRow:
    row_number: int
    site: str
    plot: str
    tag: str
    date: date
    dbh_mm: Optional[int]
    health: Optional[int]
    standing: Optional[bool]
    notes: str
    genus: Optional[str] = None
    species: Optional[str] = None
    origin: str = "field"
    normalization_flags: List[str] = field(default_factory=list)
    raw: Dict[str, str] = field(default_factory=dict)


@dataclass
class SurveyMeta:
    data: Dict[str, object]


@dataclass
class TransactionData:
    path: Path
    measurements: List[MeasurementRow]
    commands: List[Command]
    survey_meta: Optional[SurveyMeta]
