"""Validation and diagnostics for canonical census outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .config import Config


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCode(StrEnum):
    E_UNKNOWN_SURVEY = "E_UNKNOWN_SURVEY"
    E_UNKNOWN_PLOT = "E_UNKNOWN_PLOT"
    E_HEALTH_RANGE = "E_HEALTH_RANGE"
    E_DBH_NEGATIVE = "E_DBH_NEGATIVE"
    E_FIELD_STATUS = "E_FIELD_STATUS"
    E_INTERPRETED_STATUS = "E_INTERPRETED_STATUS"
    W_ALIVE_HEALTH_CONFLICT = "W_ALIVE_HEALTH_CONFLICT"
    W_DEAD_HEALTH_CONFLICT = "W_DEAD_HEALTH_CONFLICT"
    W_DBH_JUMP = "W_DBH_JUMP"
    W_TAXON_CONFLICT = "W_TAXON_CONFLICT"
    I_INFERRED_DEAD = "I_INFERRED_DEAD"
    I_ZOMBIE_TREE = "I_ZOMBIE_TREE"
    I_CORRECTED_ROW = "I_CORRECTED_ROW"


@dataclass(frozen=True)
class Issue:
    severity: Severity
    code: IssueCode
    message: str
    survey_id: str = ""
    site: str = ""
    plot: str = ""
    public_tag: str = ""
    identity_tag: str = ""
    tree_uid: str = ""
    source_file: str = ""
    source_row: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, object]:
        return {
            "severity": str(self.severity),
            "code": str(self.code),
            "message": self.message,
            "survey_id": self.survey_id,
            "site": self.site,
            "plot": self.plot,
            "public_tag": self.public_tag,
            "identity_tag": self.identity_tag,
            "tree_uid": self.tree_uid,
            "source_file": self.source_file,
            "source_row": self.source_row,
            "details": json.dumps(_jsonable(self.details), sort_keys=True),
        }


def validate_census(census: pd.DataFrame, config: Config) -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(_row_level_issues(census, config))
    issues.extend(_dbh_jump_issues(census))
    issues.extend(_missingness_issues(census))
    issues.extend(_zombie_issues(census))
    issues.extend(_taxon_conflict_issues(census, config))
    issues.extend(_correction_issues(census))
    return issues


def write_diagnostics(
    issues: Iterable[Issue],
    output_dir: str | Path = "output/diagnostics",
) -> dict[str, object]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [issue.to_record() for issue in issues]
    issues_df = pd.DataFrame(records)
    if issues_df.empty:
        issues_df = pd.DataFrame(columns=list(Issue.__dataclass_fields__))
    issues_path = output_dir / "issues.csv"
    summary_path = output_dir / "summary.json"
    issues_df.to_csv(issues_path, index=False)

    summary = {
        "total": int(len(issues_df)),
        "by_severity": issues_df.groupby("severity").size().astype(int).to_dict()
        if not issues_df.empty
        else {},
        "by_code": issues_df.groupby("code").size().astype(int).to_dict()
        if not issues_df.empty
        else {},
        "issues_csv": str(issues_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def write_issue_context(
    census: pd.DataFrame,
    issues: Iterable[Issue],
    code: str,
    output_path: str | Path,
) -> pd.DataFrame:
    """Write surrounding tree histories for issues matching ``code``."""

    output_path = Path(output_path)
    matching_issues = [issue for issue in issues if str(issue.code) == str(code)]
    rows: list[dict[str, object]] = []
    for issue_index, issue in enumerate(matching_issues, start=1):
        tree_rows = census.loc[census["tree_uid"].eq(issue.tree_uid)].sort_values(
            ["date", "stem_rank", "source_file", "source_row"]
        )
        for row in tree_rows.itertuples(index=False):
            rows.append(
                {
                    "issue_index": issue_index,
                    "issue_code": str(issue.code),
                    "issue_message": issue.message,
                    "is_issue_row": (
                        row.source_file == issue.source_file
                        and _nullable_int(row.source_row) == issue.source_row
                    ),
                    "survey_id": row.survey_id,
                    "date": row.date,
                    "site": row.site,
                    "plot": row.plot,
                    "public_tag": row.public_tag,
                    "identity_tag": row.identity_tag,
                    "tree_uid": row.tree_uid,
                    "genus": row.genus,
                    "species": row.species,
                    "taxon_code": row.taxon_code,
                    "stem_rank": row.stem_rank,
                    "datasheet_slot": row.datasheet_slot,
                    "dbh_mm": row.dbh_mm,
                    "health_observed": row.health_observed,
                    "alive_observed": row.alive_observed,
                    "standing_observed": row.standing_observed,
                    "field_status": row.field_status,
                    "interpreted_status": row.interpreted_status,
                    "source_file": row.source_file,
                    "source_row": row.source_row,
                    "notes": row.notes,
                    "correction_notes": row.correction_notes,
                }
            )

    context = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    context.to_csv(output_path, index=False)
    return context


def _row_level_issues(census: pd.DataFrame, config: Config) -> list[Issue]:
    issues: list[Issue] = []
    known_surveys = {survey.id for survey in config.surveys}
    valid_statuses = {"observed_alive", "observed_dead", "not_found", "unknown"}
    valid_interpreted = {"alive", "observed_dead", "missing_pending", "inferred_dead"}

    for row in census.itertuples(index=False):
        if row.survey_id not in known_surveys:
            issues.append(
                _issue(
                    row,
                    Severity.ERROR,
                    IssueCode.E_UNKNOWN_SURVEY,
                    f"Unknown survey id {row.survey_id}",
                    {"survey_id": row.survey_id},
                )
            )
        if row.plot not in config.plots:
            issues.append(
                _issue(row, Severity.ERROR, IssueCode.E_UNKNOWN_PLOT, f"Unknown plot {row.plot}", {"plot": row.plot})
            )
        if pd.notna(row.health_observed) and not (0 <= row.health_observed <= 10):
            issues.append(
                _issue(
                    row,
                    Severity.ERROR,
                    IssueCode.E_HEALTH_RANGE,
                    "Health is outside 0-10",
                    {"health_observed": row.health_observed},
                )
            )
        if pd.notna(row.dbh_mm) and row.dbh_mm < 0:
            issues.append(
                _issue(
                    row,
                    Severity.ERROR,
                    IssueCode.E_DBH_NEGATIVE,
                    "DBH is negative",
                    {"dbh_mm": row.dbh_mm},
                )
            )
        if row.field_status not in valid_statuses:
            issues.append(
                _issue(
                    row,
                    Severity.ERROR,
                    IssueCode.E_FIELD_STATUS,
                    f"Unknown field_status {row.field_status}",
                    {"field_status": row.field_status, "valid_statuses": sorted(valid_statuses)},
                )
            )
        if row.interpreted_status not in valid_interpreted:
            issues.append(
                _issue(
                    row,
                    Severity.ERROR,
                    IssueCode.E_INTERPRETED_STATUS,
                    f"Unknown interpreted_status {row.interpreted_status}",
                    {"interpreted_status": row.interpreted_status, "valid_statuses": sorted(valid_interpreted)},
                )
            )
        if (
            row.field_status == "observed_alive"
            and pd.notna(row.health_observed)
            and row.health_observed == 0
        ):
            issues.append(
                _issue(
                    row,
                    Severity.WARNING,
                    IssueCode.W_ALIVE_HEALTH_CONFLICT,
                    "Observed alive but health is 0",
                    {"field_status": row.field_status, "health_observed": row.health_observed},
                )
            )
        if (
            row.field_status == "observed_dead"
            and pd.notna(row.health_observed)
            and row.health_observed > 0
        ):
            issues.append(
                _issue(
                    row,
                    Severity.WARNING,
                    IssueCode.W_DEAD_HEALTH_CONFLICT,
                    "Observed dead but health is positive",
                    {"field_status": row.field_status, "health_observed": row.health_observed},
                )
            )
    return issues


def _dbh_jump_issues(census: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []
    tree_survey = (
        census.loc[census["dbh_mm"].notna()]
        .groupby(["tree_uid", "survey_id"], as_index=False)
        .agg(
            max_dbh_mm=("dbh_mm", "max"),
            survey_date=("date", "min"),
            site=("site", "first"),
            plot=("plot", "first"),
            public_tag=("public_tag", "first"),
            identity_tag=("identity_tag", "first"),
        )
    )
    for tree_uid, group in tree_survey.groupby("tree_uid", sort=False):
        ordered = group.sort_values("survey_date")
        previous = None
        for row in ordered.itertuples(index=False):
            if previous is not None:
                delta = abs(row.max_dbh_mm - previous.max_dbh_mm)
                denominator = max(row.max_dbh_mm, previous.max_dbh_mm)
                pct = delta / denominator if denominator else 0
                if delta >= 6 and pct > 0.16:
                    issues.append(
                        Issue(
                            severity=Severity.WARNING,
                            code=IssueCode.W_DBH_JUMP,
                            message="Large DBH change between adjacent observations",
                            survey_id=row.survey_id,
                            site=row.site,
                            plot=row.plot,
                            public_tag=row.public_tag,
                            identity_tag=row.identity_tag,
                            tree_uid=tree_uid,
                            details={
                                "previous_survey": previous.survey_id,
                                "previous_dbh": previous.max_dbh_mm,
                                "current_survey": row.survey_id,
                                "current_dbh": row.max_dbh_mm,
                                "delta": delta,
                                "pct": pct,
                            },
                        )
                    )
            previous = row
    return issues


def _missingness_issues(census: pd.DataFrame) -> list[Issue]:
    issues = []
    for row in census.loc[census["interpreted_status"].eq("inferred_dead")].itertuples(index=False):
        issues.append(
            _issue(
                row,
                Severity.INFO,
                IssueCode.I_INFERRED_DEAD,
                "Missing/not-found observation interpreted as dead by threshold",
                {"interpreted_status": row.interpreted_status, "field_status": row.field_status},
            )
        )
    return issues


def _zombie_issues(census: pd.DataFrame) -> list[Issue]:
    issues = []
    zombie_rows = census.loc[census["zombie_ever"]]
    for tree_uid, group in zombie_rows.groupby("tree_uid", sort=False):
        observed = group.loc[group["field_status"].isin(["observed_dead", "observed_alive"])]
        if observed.empty:
            continue
        ordered = observed.sort_values("date")
        row = ordered.iloc[0]
        issues.append(
            Issue(
                severity=Severity.INFO,
                code=IssueCode.I_ZOMBIE_TREE,
                message="Tree has observed dead followed by observed alive evidence",
                survey_id=str(row["survey_id"]),
                site=str(row["site"]),
                plot=str(row["plot"]),
                public_tag=str(row["public_tag"]),
                identity_tag=str(row["identity_tag"]),
                tree_uid=tree_uid,
                details={"evidence": _zombie_evidence(ordered)},
            )
        )
    return issues


def _correction_issues(census: pd.DataFrame) -> list[Issue]:
    issues = []
    corrected = census.loc[census["correction_notes"].fillna("").astype(str).ne("")]
    for row in corrected.itertuples(index=False):
        issues.append(
            _issue(
                row,
                Severity.INFO,
                IssueCode.I_CORRECTED_ROW,
                "Row was changed by configured correction",
                {"correction_notes": row.correction_notes},
            )
        )
    return issues


def _taxon_conflict_issues(census: pd.DataFrame, config: Config) -> list[Issue]:
    issues = []
    unknown_taxa = {
        _taxon_code(config.unknown_genus, config.unknown_species),
        "UNISPP",
    }
    columns = ["genus", "species", "taxon_code"]
    for tree_uid, group in census.groupby("tree_uid", sort=False):
        known = group.loc[~group["taxon_code"].isin(unknown_taxa), columns + ["survey_id"]]
        taxa = known[columns].drop_duplicates()
        if len(taxa) <= 1:
            continue
        first = group.sort_values("date").iloc[0]
        details = {
            "taxa": [
                {
                    "genus": row.genus,
                    "species": row.species,
                    "taxon_code": row.taxon_code,
                    "surveys": known.loc[known["taxon_code"].eq(row.taxon_code), "survey_id"]
                    .drop_duplicates()
                    .astype(str)
                    .tolist(),
                }
                for row in taxa.itertuples(index=False)
            ]
        }
        issues.append(
            Issue(
                severity=Severity.WARNING,
                code=IssueCode.W_TAXON_CONFLICT,
                message="Tree has multiple known taxa across observations",
                survey_id=str(first["survey_id"]),
                site=str(first["site"]),
                plot=str(first["plot"]),
                public_tag=str(first["public_tag"]),
                identity_tag=str(first["identity_tag"]),
                tree_uid=tree_uid,
                details=details,
            )
        )
    return issues


def _taxon_code(genus: str, species: str) -> str:
    return f"{genus[:3]}{species[:3]}".upper().replace(".", "")


def _zombie_evidence(group: pd.DataFrame) -> list[dict[str, object]]:
    evidence = []
    for row in group.itertuples(index=False):
        if row.field_status in {"observed_alive", "observed_dead"}:
            evidence.append(
                {
                    "survey_id": row.survey_id,
                    "date": str(row.date),
                    "field_status": row.field_status,
                }
            )
    return evidence


def _issue(
    row,
    severity: Severity,
    code: IssueCode,
    message: str,
    details: dict[str, Any] | None = None,
) -> Issue:
    return Issue(
        severity=severity,
        code=code,
        message=message,
        survey_id=str(getattr(row, "survey_id", "")),
        site=str(getattr(row, "site", "")),
        plot=str(getattr(row, "plot", "")),
        public_tag=str(getattr(row, "public_tag", "")),
        identity_tag=str(getattr(row, "identity_tag", "")),
        tree_uid=str(getattr(row, "tree_uid", "")),
        source_file=str(getattr(row, "source_file", "")),
        source_row=_nullable_int(getattr(row, "source_row", None)),
        details=details or {},
    )


def _nullable_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(item) for item in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
