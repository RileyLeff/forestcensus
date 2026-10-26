"""Unified manual-decision phase for accepted canonical calls."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import Config
from .corrections import _apply_row_correction, _apply_row_exclusion
from .identity import apply_identity_operations
from .taxonomy import apply_taxon_overrides


@dataclass(frozen=True)
class ConfiguredDecision:
    decision_id: str
    operation: str
    source_config: str
    note: str
    selector: dict[str, object]
    parameters: dict[str, object]

    def to_record(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id,
            "operation": self.operation,
            "source_config": self.source_config,
            "note": self.note,
            "selector": json.dumps(_jsonable(self.selector), sort_keys=True),
            "parameters": json.dumps(_jsonable(self.parameters), sort_keys=True),
        }


def build_configured_decision_ledger(config: Config) -> pd.DataFrame:
    """Return the accepted manual decisions loaded from project config."""

    decisions: list[ConfiguredDecision] = []
    for index, correction in enumerate(config.row_corrections, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"row_correction:{index:04d}",
                operation=_row_correction_operation(correction.set),
                source_config="corrections.toml:row_corrections",
                note=correction.note,
                selector=correction.match,
                parameters={"set": correction.set},
            )
        )
    for index, exclusion in enumerate(config.row_exclusions, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"row_exclusion:{index:04d}",
                operation="suppress_observation",
                source_config="corrections.toml:row_exclusions",
                note=exclusion.note,
                selector=exclusion.match,
                parameters={},
            )
        )
    for index, override in enumerate(config.taxon_overrides, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"taxon_override:{index:04d}",
                operation="set_taxon",
                source_config="corrections.toml:taxon_overrides",
                note=override.note,
                selector=override.match,
                parameters={"genus": override.genus, "species": override.species, "scope": override.scope},
            )
        )
    for index, reassignment in enumerate(config.row_reassignments, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"row_reassignment:{index:04d}",
                operation="reassign_identity_row",
                source_config="identity.toml:row_reassignments",
                note=reassignment.note,
                selector=reassignment.match,
                parameters={
                    "public_tag": reassignment.public_tag,
                    "identity_tag": reassignment.identity_tag,
                    "tree_number": reassignment.tree_number,
                },
            )
        )
    for index, alias in enumerate(config.identity_aliases, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"identity_alias:{index:04d}",
                operation="alias_identity_window",
                source_config="identity.toml:aliases",
                note=alias.note,
                selector={
                    "site": alias.site,
                    "plot": alias.plot,
                    "tag": alias.tag,
                    "effective_from": alias.effective_from.isoformat(),
                    "effective_to": alias.effective_to.isoformat() if alias.effective_to else None,
                },
                parameters={"identity_tag": alias.identity_tag},
            )
        )
    for index, split in enumerate(config.split_operations, start=1):
        decisions.append(
            ConfiguredDecision(
                decision_id=f"identity_split:{index:04d}",
                operation="split_identity",
                source_config="identity.toml:splits",
                note=split.note,
                selector={"source": split.source, "selector": split.selector},
                parameters={
                    "target_identity_tag": split.target_identity_tag,
                    "target_identity_label": split.target_identity_label,
                    "target_public_tag": split.target_public_tag,
                    "target_tree_number": split.target_tree_number,
                },
            )
        )
    records = [decision.to_record() for decision in decisions]
    return pd.DataFrame(
        records,
        columns=["decision_id", "operation", "source_config", "note", "selector", "parameters"],
    )


def write_configured_decision_ledger(config: Config, out_dir: str | Path) -> dict[str, object]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger = build_configured_decision_ledger(config)
    csv_path = out_dir / "configured_decisions.csv"
    parquet_path = out_dir / "configured_decisions.parquet"
    ledger.to_csv(csv_path, index=False)
    ledger.to_parquet(parquet_path, index=False)
    summary = {
        "configured_decisions": int(len(ledger)),
        "by_operation": ledger.groupby("operation").size().astype(int).to_dict()
        if not ledger.empty
        else {},
        "outputs": {
            "csv": str(csv_path),
            "parquet": str(parquet_path),
        },
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["summary"] = str(summary_path)
    return summary


def apply_decisions(events: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Apply all accepted manual decisions in one explicit phase."""

    resolved = events.copy()
    if "identity_tag" not in resolved.columns:
        resolved["identity_tag"] = resolved["public_tag"]
    if "identity_label" not in resolved.columns:
        resolved["identity_label"] = ""
    if "correction_notes" not in resolved.columns:
        resolved["correction_notes"] = ""

    for correction in config.row_corrections:
        _apply_row_correction(resolved, correction)
    for exclusion in config.row_exclusions:
        resolved = _apply_row_exclusion(resolved, exclusion)

    resolved = apply_identity_operations(resolved, config)
    resolved = apply_taxon_overrides(resolved, config)
    return resolved


def _row_correction_operation(set_values: dict[str, object]) -> str:
    keys = set(set_values)
    if keys == {"dbh_mm"}:
        value = set_values.get("dbh_mm")
        return "suppress_field" if pd.isna(value) else "set_field"
    if keys == {"health_observed"}:
        return "set_field"
    if keys == {"alive_observed", "field_status"}:
        return "set_status"
    if keys == {"genus", "species", "taxon_code"}:
        return "set_row_taxon"
    if keys == {"dbh_mm", "health_observed", "alive_observed", "field_status"}:
        return "interpret_as_not_found"
    return "set_fields"


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(item) for item in value]
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value
