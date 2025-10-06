"""Row-level validation for measurement data."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from .issues import ValidationIssue


def validate_measurement_rows(
    measurements: Iterable[MeasurementRow], config: ConfigBundle
) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    taxonomy_pairs: Dict[Tuple[str, str], str] = {
        (entry.genus.lower(), entry.species.lower()): entry.code
        for entry in config.taxonomy.species
    }
    site_plots = {
        site: set(site_cfg.plots)
        for site, site_cfg in config.sites.sites.items()
    }

    for row in measurements:
        issues.extend(_validate_row(row, taxonomy_pairs, site_plots, config))
    return issues


def _validate_row(
    row: MeasurementRow,
    taxonomy_pairs: Dict[Tuple[str, str], str],
    site_plots: Dict[str, set[str]],
    config: ConfigBundle,
) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    def location(column: str) -> str:
        return f"measurements.csv:row {row.row_number},col {column}"

    if row.dbh_mm is not None and row.dbh_mm < 0:
        issues.append(
            ValidationIssue(
                code="E_ROW_DBH_NEG",
                severity="error",
                message="dbh_mm must be >= 0",
                location=location("dbh_mm"),
            )
        )

    if row.dbh_mm is None and row.origin != "implied":
        issues.append(
            ValidationIssue(
                code="E_ROW_DBH_NA_NOT_IMPLIED",
                severity="error",
                message="dbh_mm may be NA only for origin='implied'",
                location=location("dbh_mm"),
            )
        )

    if row.health is not None and not (0 <= row.health <= 10):
        issues.append(
            ValidationIssue(
                code="E_ROW_HEALTH_RANGE",
                severity="error",
                message="health must be within 0..10",
                location=location("health"),
            )
        )

    if not _site_known(row.site, row.plot, site_plots):
        issues.append(
            ValidationIssue(
                code="E_ROW_SITE_OR_PLOT_UNKNOWN",
                severity="error",
                message=f"unknown site/plot {row.site}/{row.plot}",
                location=location("plot"),
            )
        )

    if not _date_within_surveys(row.date.isoformat(), config):
        issues.append(
            ValidationIssue(
                code="E_ROW_DATE_OUTSIDE_SURVEY",
                severity="error",
                message=f"date {row.date.isoformat()} not within configured surveys",
                location=location("date"),
            )
        )

    taxonomy_issue = _validate_taxonomy(row, taxonomy_pairs)
    if taxonomy_issue is not None:
        issues.append(taxonomy_issue)

    return issues


def _site_known(site: str, plot: str, site_plots: Dict[str, set[str]]) -> bool:
    plots = site_plots.get(site)
    if plots is None:
        return False
    return plot in plots


def _date_within_surveys(date_iso: str, config: ConfigBundle) -> bool:
    target = date_iso
    for survey in config.surveys.surveys:
        if survey.start.isoformat() <= target <= survey.end.isoformat():
            return True
    return False


def _validate_taxonomy(
    row: MeasurementRow, taxonomy_pairs: Dict[Tuple[str, str], str]
) -> Optional[ValidationIssue]:
    if not row.genus and not row.species and not row.code:
        return None

    if not row.genus or not row.species:
        return ValidationIssue(
            code="E_ROW_TAXONOMY_MISMATCH",
            severity="error",
            message="genus and species must both be provided when one is present",
            location=f"measurements.csv:row {row.row_number},col genus",
        )

    key = (row.genus.lower(), row.species.lower())
    expected_code = taxonomy_pairs.get(key)
    if expected_code is None:
        return ValidationIssue(
            code="E_ROW_TAXONOMY_MISMATCH",
            severity="error",
            message=f"species {row.genus} {row.species} not in taxonomy",
            location=f"measurements.csv:row {row.row_number},col species",
        )

    if row.code and row.code != expected_code:
        return ValidationIssue(
            code="E_ROW_TAXONOMY_MISMATCH",
            severity="error",
            message=(
                "code must match taxonomy ({} expected {})".format(
                    row.code, expected_code
                )
            ),
            location=f"measurements.csv:row {row.row_number},col code",
        )

    return None
