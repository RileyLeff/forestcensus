"""Per-tree validation across surveys."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from ..assembly import SurveyCatalog
from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from .issues import ValidationIssue


@dataclass
class TreeSurveyRecord:
    survey_id: str
    max_dbh_mm: Optional[int]


TreeKey = Tuple[str, str, str]


def validate_growth(
    measurements: Iterable[MeasurementRow],
    config: ConfigBundle,
) -> List[ValidationIssue]:
    """Validate DBH growth across surveys for each tree."""

    catalog = SurveyCatalog.from_config(config)
    tree_history = _build_tree_history(measurements, catalog)

    warn_pct = config.validation.dbh_pct_warn
    warn_abs = config.validation.dbh_abs_floor_warn_mm
    err_pct = config.validation.dbh_pct_error
    err_abs = config.validation.dbh_abs_floor_error_mm

    issues: List[ValidationIssue] = []

    for key, history in tree_history.items():
        sorted_history = _sort_history(history, catalog)
        previous: Optional[TreeSurveyRecord] = None
        for record in sorted_history:
            if previous is None:
                previous = record
                continue
            prev_dbh = previous.max_dbh_mm
            curr_dbh = record.max_dbh_mm
            if prev_dbh is None or curr_dbh is None:
                previous = record
                continue
            delta = abs(curr_dbh - prev_dbh)
            if delta == 0:
                previous = record
                continue
            pct_change = delta / max(prev_dbh, curr_dbh)
            location = _growth_location(key, record.survey_id)
            if pct_change >= err_pct and delta >= err_abs:
                issues.append(
                    ValidationIssue(
                        code="E_DBH_GROWTH_ERROR",
                        severity="error",
                        message=(
                            f"dbh change {delta}mm ({pct_change:.2%}) between {previous.survey_id}"
                            f" and {record.survey_id} exceeds error threshold"
                        ),
                        location=location,
                    )
                )
            elif pct_change >= warn_pct and delta >= warn_abs:
                issues.append(
                    ValidationIssue(
                        code="W_DBH_GROWTH_WARN",
                        severity="warning",
                        message=(
                            f"dbh change {delta}mm ({pct_change:.2%}) between {previous.survey_id}"
                            f" and {record.survey_id} exceeds warning threshold"
                        ),
                        location=location,
                    )
                )
            previous = record

    return issues


def _build_tree_history(
    measurements: Iterable[MeasurementRow],
    catalog: SurveyCatalog,
) -> Dict[TreeKey, Dict[str, TreeSurveyRecord]]:
    history: Dict[TreeKey, Dict[str, TreeSurveyRecord]] = defaultdict(dict)
    for row in measurements:
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        key = (row.site, row.plot, row.tag)
        record = history[key].get(survey_id)
        max_dbh = row.dbh_mm
        if record is None:
            history[key][survey_id] = TreeSurveyRecord(survey_id, max_dbh)
        else:
            if max_dbh is not None:
                if record.max_dbh_mm is None or max_dbh > record.max_dbh_mm:
                    history[key][survey_id] = TreeSurveyRecord(survey_id, max_dbh)
    return history


def _sort_history(
    history: Dict[str, TreeSurveyRecord], catalog: SurveyCatalog
) -> List[TreeSurveyRecord]:
    ordered_ids = catalog.ordered_surveys()
    return [history[survey_id] for survey_id in ordered_ids if survey_id in history]


def _growth_location(key: TreeKey, survey_id: str) -> str:
    site, plot, tag = key
    return f"growth:{site}/{plot}/{tag}:{survey_id}"
