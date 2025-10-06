"""Transaction submission pipeline."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from ..config import load_config_bundle
from ..exceptions import ConfigError, ForcenError
from ..ledger.storage import Ledger
from ..transactions import NormalizationConfig, load_transaction
from ..transactions.models import MeasurementRow
from ..validators import ValidationIssue
from .lint import lint_transaction
from .utils import determine_default_effective_date, with_default_effective
from ..assembly.treebuilder import assign_tree_uids, build_alias_resolver
from ..assembly.trees import generate_implied_rows
from ..assembly.split import apply_splits
from ..assembly.survey import SurveyCatalog
from ..assembly.properties import apply_properties, build_property_timelines
from ..assembly.primary import apply_primary_tags, build_primary_timelines
from ..assembly.tree_outputs import build_retag_suggestions, build_tree_view
from ..dsl.types import AliasCommand, SplitCommand, UpdateCommand


@dataclass
class SubmitResult:
    tx_id: str
    accepted: bool
    version_seq: Optional[int] = None
    warnings: int = 0


class SubmitError(ForcenError):
    pass


def submit_transaction(
    transaction_dir: Path,
    config_dir: Path,
    workspace: Path,
    *,
    normalization: Optional[NormalizationConfig] = None,
) -> SubmitResult:
    """Submit a transaction and update the ledger."""

    transaction_dir = Path(transaction_dir)
    config_dir = Path(config_dir)
    workspace = Path(workspace)
    normalization_override = normalization
    lint_report = lint_transaction(
        transaction_dir=transaction_dir,
        config_dir=config_dir,
        normalization=normalization_override,
    )

    if lint_report.has_errors:
        raise SubmitError("transaction rejected due to validation errors")

    config = load_config_bundle(config_dir)
    normalization = normalization_override or NormalizationConfig(
        rounding=config.validation.rounding
    )
    tx_data = load_transaction(transaction_dir, normalization=normalization)
    default_effective = determine_default_effective_date(config, tx_data)
    tx_data.commands = with_default_effective(tx_data.commands, default_effective)
    resolver = build_alias_resolver(tx_data.measurements, tx_data.commands)
    assign_tree_uids(tx_data.measurements, resolver)
    catalog = SurveyCatalog.from_config(config)
    apply_splits(
        tx_data.measurements,
        [cmd for cmd in tx_data.commands if isinstance(cmd, SplitCommand)],
        resolver,
        catalog,
    )
    property_timelines = build_property_timelines(
        [cmd for cmd in tx_data.commands if isinstance(cmd, UpdateCommand)],
        resolver,
    )
    apply_properties(tx_data.measurements, property_timelines)
    primary_timelines = build_primary_timelines(
        [cmd for cmd in tx_data.commands if isinstance(cmd, AliasCommand)],
        resolver,
    )
    apply_primary_tags(tx_data.measurements, primary_timelines, catalog)
    tx_id = lint_report.tx_id

    ledger = Ledger(workspace)
    if ledger.has_transaction(tx_id):
        return SubmitResult(tx_id=tx_id, accepted=False, version_seq=None, warnings=lint_report.warning_count)

    implied_rows = generate_implied_rows(tx_data.measurements, config)
    all_rows = list(tx_data.measurements) + implied_rows

    existing_rows = _load_existing_observations(ledger.observations_csv)
    apply_primary_tags(existing_rows, primary_timelines, catalog)

    output_rows = existing_rows + all_rows
    tree_view_rows = build_tree_view(output_rows, catalog)
    retag_rows = build_retag_suggestions(output_rows, config)

    rows_added, row_counts = ledger.append_observations(config, all_rows, tx_id)
    ledger.write_tree_outputs(tree_view_rows, retag_rows)
    dsl_lines_added = ledger.append_updates(transaction_dir)

    config_hashes = _hash_config(config_dir)
    input_hashes = _hash_transaction_inputs(transaction_dir)

    issues_list = _rebuild_issues(lint_report.issues)
    summary = _summarize_issues(issues_list)

    code_version = _detect_code_version()

    validation_payload = {
        "tx_id": tx_id,
        "summary": {
            "errors": lint_report.error_count,
            "warnings": lint_report.warning_count,
        },
        "issues": [
            {
                "code": issue.code,
                "severity": issue.severity,
                "message": issue.message,
                "location": issue.location,
            }
            for issue in lint_report.issues
        ],
    }
    ledger.write_validation_report(validation_payload)

    ledger.append_transaction_entry(
        tx_id=tx_id,
        code_version=code_version,
        config_hashes=config_hashes,
        input_hashes=input_hashes,
        rows_added=rows_added,
        dsl_lines_added=dsl_lines_added,
        row_counts=row_counts,
        issues=issues_list,
    )

    version_seq = ledger.write_version(
        tx_ids=[tx_id],
        validation_summary=summary,
        config_hashes=config_hashes,
        input_hashes=input_hashes,
        code_version=code_version,
        row_counts=row_counts,
    )

    return SubmitResult(
        tx_id=tx_id,
        accepted=True,
        version_seq=version_seq,
        warnings=lint_report.warning_count,
    )


def _hash_config(config_dir: Path) -> Dict[str, str]:
    return {
        path.name: _sha256_file(path)
        for path in sorted(config_dir.glob("*.toml"))
    }


def _hash_transaction_inputs(tx_dir: Path) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for path in sorted(tx_dir.rglob("*")):
        if path.is_file():
            hashes[str(path.relative_to(tx_dir))] = _sha256_file(path)
    return hashes


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _detect_code_version() -> str:
    return "unknown"


def _rebuild_issues(issues: List[ValidationIssue]) -> List[ValidationIssue]:
    # Issues are already ValidationIssue instances, but ensure a copy for ledger writes.
    return list(issues)


def _summarize_issues(issues: List[ValidationIssue]) -> Dict[str, int]:
    return {
        "errors": sum(1 for issue in issues if issue.is_error()),
        "warnings": sum(1 for issue in issues if not issue.is_error()),
    }


def _load_existing_observations(path: Path) -> List[MeasurementRow]:
    if not path.exists():
        return []

    import pandas as pd

    df = pd.read_csv(path)
    rows: List[MeasurementRow] = []
    for record in df.to_dict(orient="records"):
        rows.append(
            MeasurementRow(
                row_number=0,
                site=str(record.get("site", "")),
                plot=str(record.get("plot", "")),
                tag=str(record.get("tag", "")),
                date=date.fromisoformat(str(record.get("date"))),
                dbh_mm=_maybe_int(record.get("dbh_mm")),
                health=_maybe_int(record.get("health")),
                standing=_maybe_bool(record.get("standing")),
                notes=str(record.get("notes", "")),
                origin=str(record.get("origin", "field")),
                genus=record.get("genus") or None,
                species=record.get("species") or None,
                code=record.get("code") or None,
                normalization_flags=[],
                raw={},
                tree_uid=record.get("tree_uid") or None,
                public_tag=record.get("public_tag") or record.get("tag"),
            )
        )
    return rows


def _maybe_int(value) -> Optional[int]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _maybe_bool(value) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).lower()
    if text in {"true", "t", "1"}:
        return True
    if text in {"false", "f", "0"}:
        return False
    return None
