"""Lint pipeline for transactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from ..config import ConfigBundle, load_config_bundle
from ..transactions import NormalizationConfig, TransactionData, load_transaction
from ..transactions.txid import compute_tx_id
from ..validators import (
    ValidationIssue,
    validate_dsl_commands,
    validate_growth,
    validate_measurement_rows,
)


@dataclass
class LintReport:
    """Summary from linting a transaction."""

    transaction_path: Path
    tx_id: str
    issues: List[ValidationIssue] = field(default_factory=list)
    measurement_rows: List[dict] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.is_error())

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if not issue.is_error())

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

    def as_dict(self) -> dict:
        return {
            "transaction_path": str(self.transaction_path),
            "tx_id": self.tx_id,
            "issues": [
                {
                    "code": issue.code,
                    "severity": issue.severity,
                    "message": issue.message,
                    "location": issue.location,
                }
                for issue in self.issues
            ],
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "rows": len(self.measurement_rows),
            },
            "measurement_rows": self.measurement_rows,
        }


def lint_transaction(
    transaction_dir: Path,
    config_dir: Path,
    *,
    normalization: NormalizationConfig | None = None,
) -> LintReport:
    """Lint a transaction directory against project configuration."""

    config_dir = Path(config_dir)
    transaction_dir = Path(transaction_dir)
    normalization = normalization or NormalizationConfig()

    config = load_config_bundle(config_dir)
    transaction = load_transaction(transaction_dir, normalization=normalization)
    tx_id = compute_tx_id(transaction_dir)

    issues = _collect_issues(config, transaction)
    measurement_rows = [
        {
            "row_number": row.row_number,
            "site": row.site,
            "plot": row.plot,
            "tag": row.tag,
            "date": row.date.isoformat(),
            "dbh_mm": row.dbh_mm,
            "health": row.health,
            "standing": row.standing,
            "origin": row.origin,
            "flags": list(row.normalization_flags),
        }
        for row in transaction.measurements
    ]

    return LintReport(
        transaction_path=transaction_dir,
        tx_id=tx_id,
        issues=issues,
        measurement_rows=measurement_rows,
    )


def _collect_issues(config: ConfigBundle, tx: TransactionData) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    issues.extend(validate_measurement_rows(tx.measurements, config))
    issues.extend(validate_growth(tx.measurements, config))
    issues.extend(validate_dsl_commands(tx.commands))
    return sorted(issues, key=lambda issue: (issue.severity, issue.code, issue.location))
