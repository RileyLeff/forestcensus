"""Normalization for transaction measurement rows."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .exceptions import TransactionDataError, TransactionFormatError
from .models import MeasurementRow


REQUIRED_COLUMNS = [
    "site",
    "plot",
    "tag",
    "date",
    "dbh_mm",
    "health",
    "standing",
    "notes",
]


@dataclass
class NormalizationConfig:
    rounding: str = "half_up"
    default_origin: str = "field"


def load_measurements(
    path: Path, config: NormalizationConfig = NormalizationConfig()
) -> List[MeasurementRow]:
    """Load and normalize measurement rows from *path*."""

    path = Path(path)
    if not path.exists():
        raise TransactionFormatError(path=path, message="measurements.csv not found")

    rows: List[MeasurementRow] = []
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise TransactionFormatError(path=path, message="missing header row")
        _validate_required_columns(path, reader.fieldnames)
        for index, raw in enumerate(reader, start=2):  # row numbers include header
            row = _normalize_row(
                path=path,
                row_number=index,
                raw=raw,
                config=config,
            )
            rows.append(row)
    return rows


def _validate_required_columns(path: Path, columns: Iterable[str]) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing:
        raise TransactionFormatError(
            path=path,
            message=f"missing required columns: {', '.join(missing)}",
        )


def _normalize_row(
    path: Path,
    row_number: int,
    raw: Dict[str, str],
    config: NormalizationConfig,
) -> MeasurementRow:
    def require(field: str) -> str:
        value = (raw.get(field) or "").strip()
        if value == "":
            raise TransactionDataError(path=path, row=row_number, column=field, message="value required")
        return value

    def optional(field: str) -> str:
        return (raw.get(field) or "").strip()

    site = require("site")
    plot = require("plot")
    tag = require("tag")
    date_value = require("date")
    try:
        observed_date = date.fromisoformat(date_value)
    except ValueError as exc:
        raise TransactionDataError(
            path=path,
            row=row_number,
            column="date",
            message=f"invalid date '{date_value}'",
        ) from exc

    dbh_value = optional("dbh_mm")
    dbh_mm = _parse_dbh(path, row_number, dbh_value)

    health_value = optional("health")
    health, health_flags = _parse_health(path, row_number, health_value, config)

    standing_value = optional("standing")
    standing = _parse_optional_bool(path, row_number, "standing", standing_value)

    notes = optional("notes")
    genus = optional("genus") or None
    species = optional("species") or None
    code = optional("code") or None
    origin = optional("origin") or config.default_origin
    origin = origin.lower()
    if origin not in {"field", "ai", "implied"}:
        raise TransactionDataError(
            path=path,
            row=row_number,
            column="origin",
            message=f"invalid origin '{origin}'",
        )

    normalization_flags = list(health_flags)

    alive_flag = None
    if "alive" in raw:
        alive_raw = optional("alive")
        if alive_raw:
            alive_flag = _parse_optional_bool(path, row_number, "alive", alive_raw)

    if alive_flag is True and health == 0:
        health = 1
        normalization_flags.append("alive_override")

    return MeasurementRow(
        row_number=row_number,
        site=site,
        plot=plot,
        tag=tag,
        date=observed_date,
        dbh_mm=dbh_mm,
        health=health,
        standing=standing,
        notes=notes,
        genus=genus,
        species=species,
        code=code,
        origin=origin,
        normalization_flags=normalization_flags,
        raw={key: (value or "") for key, value in raw.items()},
    )


def _parse_dbh(path: Path, row: int, value: str) -> Optional[int]:
    if value == "" or value.upper() == "NA":
        return None
    try:
        number = int(value)
    except ValueError as exc:
        raise TransactionDataError(
            path=path,
            row=row,
            column="dbh_mm",
            message=f"invalid integer '{value}'",
        ) from exc
    return number


def _parse_health(
    path: Path, row: int, value: str, config: NormalizationConfig
) -> tuple[Optional[int], List[str]]:
    if value == "":
        return None, []
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise TransactionDataError(
            path=path,
            row=row,
            column="health",
            message=f"invalid numeric value '{value}'",
        ) from exc

    if config.rounding != "half_up":
        raise ValueError(f"unsupported rounding mode: {config.rounding}")

    rounded = int(number.to_integral_value(rounding=ROUND_HALF_UP))
    flags: List[str] = []
    if rounded != number:
        flags.append("health_rounded")

    clamped = max(0, min(10, rounded))
    if clamped != rounded:
        flags.append("health_clamped")

    return clamped, flags


def _parse_optional_bool(path: Path, row: int, column: str, value: str) -> Optional[bool]:
    if value == "":
        return None
    lowered = value.lower()
    if lowered in {"true", "t", "1", "yes"}:
        return True
    if lowered in {"false", "f", "0", "no"}:
        return False
    if lowered in {"na", "null", "none"}:
        return None
    raise TransactionDataError(
        path=path,
        row=row,
        column=column,
        message=f"invalid boolean '{value}'",
    )
