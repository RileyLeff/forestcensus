"""Auditable corrections applied after input adaptation and before assembly."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .config import Config, RowCorrection, RowExclusion
from .errors import CorrectionMatchError, CorrectionUnsafeSelectorError

NUMERIC_COLUMNS = {"dbh_mm", "health_observed", "source_row"}
DATE_COLUMNS = {"date"}
TEXT_COLUMNS = {
    "source_file",
    "survey_id",
    "site",
    "zone",
    "plot",
    "public_tag",
    "identity_tag",
    "identity_label",
    "tree_number",
    "datasheet_slot",
    "genus",
    "species",
    "taxon_code",
    "field_status",
    "notes",
    "origin",
}
PROVENANCE_COLUMNS = {"source_file", "source_row"}
ROW_NUMBER_GUARD_COLUMNS = {
    "survey_id",
    "date",
    "site",
    "zone",
    "plot",
    "public_tag",
    "identity_tag",
    "identity_label",
    "tree_number",
    "datasheet_slot",
    "genus",
    "species",
    "taxon_code",
    "dbh_mm",
    "health_observed",
    "alive_observed",
    "standing_observed",
    "field_status",
    "notes",
}


def apply_corrections(events: pd.DataFrame, config: Config) -> pd.DataFrame:
    corrected = events.copy()
    if "identity_tag" not in corrected.columns:
        corrected["identity_tag"] = corrected["public_tag"]
    if "correction_notes" not in corrected.columns:
        corrected["correction_notes"] = ""

    for correction in config.row_corrections:
        _apply_row_correction(corrected, correction)
    for exclusion in getattr(config, "row_exclusions", ()):
        corrected = _apply_row_exclusion(corrected, exclusion)

    return corrected


def _apply_row_correction(df: pd.DataFrame, correction: RowCorrection) -> None:
    _validate_row_correction(correction)
    mask = _match_mask(df, correction.match)
    _require_exactly_one_match(mask, "Row correction", correction.note)

    for column, value in correction.set.items():
        if column in TEXT_COLUMNS:
            df.loc[mask, column] = str(value)
        elif column in NUMERIC_COLUMNS:
            df.loc[mask, column] = float(value)
        elif column in DATE_COLUMNS:
            df.loc[mask, column] = date.fromisoformat(str(value))
        else:
            df.loc[mask, column] = value

    if "public_tag" in correction.set and "identity_tag" not in correction.set:
        df.loc[mask, "identity_tag"] = str(correction.set["public_tag"])
    _append_note(df, mask, correction.note)


def _apply_row_exclusion(df: pd.DataFrame, exclusion: RowExclusion) -> pd.DataFrame:
    _validate_row_selector(exclusion.match, exclusion.note, operation="Row exclusion")
    mask = _match_mask(df, exclusion.match)
    _require_exactly_one_match(mask, "Row exclusion", exclusion.note)
    return df.loc[~mask].copy()


def _validate_row_correction(correction: RowCorrection) -> None:
    changed_provenance = PROVENANCE_COLUMNS.intersection(correction.set)
    if changed_provenance:
        columns = ", ".join(sorted(changed_provenance))
        raise CorrectionUnsafeSelectorError(f"Row correction cannot change provenance column(s): {columns}")
    _validate_row_selector(correction.match, correction.note, operation="Row correction")


def _validate_row_selector(match: dict[str, object], note: str, operation: str) -> None:
    if "source_row" not in match:
        return

    if "source_file" not in match:
        raise CorrectionUnsafeSelectorError(
            f"{operation} matching source_row must also match source_file: "
            f"{note}"
        )
    guard_columns = ROW_NUMBER_GUARD_COLUMNS.intersection(match)
    if not guard_columns:
        raise CorrectionUnsafeSelectorError(
            f"{operation} matching source_row must include at least one non-provenance "
            f"sanity field: {note}"
        )


def _require_exactly_one_match(mask: pd.Series, operation: str, note: str) -> None:
    match_count = int(mask.sum())
    if match_count == 0:
        raise CorrectionMatchError(f"{operation} matched no rows: {note}")
    if match_count > 1:
        raise CorrectionMatchError(
            f"{operation} matched {match_count} rows; selectors must match exactly one row: {note}"
        )


def _match_mask(df: pd.DataFrame, match: dict[str, object]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, expected in match.items():
        if column not in df.columns:
            raise CorrectionUnsafeSelectorError(f"Correction match refers to unknown column {column!r}")
        if column in NUMERIC_COLUMNS:
            actual = pd.to_numeric(df[column], errors="coerce")
            mask &= actual.eq(float(expected))
        elif column in DATE_COLUMNS:
            actual = pd.to_datetime(df[column]).dt.date
            mask &= actual.eq(date.fromisoformat(str(expected)))
        else:
            actual = df[column].astype("string").fillna("")
            mask &= actual.eq(str(expected))
    return mask


def _append_note(df: pd.DataFrame, mask: pd.Series, note: str) -> None:
    note = note.strip()
    if not note:
        return
    current = df.loc[mask, "correction_notes"].fillna("").astype(str)
    df.loc[mask, "correction_notes"] = current.map(
        lambda existing: note if not existing else f"{existing}; {note}"
    )
