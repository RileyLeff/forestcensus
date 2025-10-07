"""Utilities for inspecting version manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..exceptions import ForcenError
from ..ledger.storage import Ledger


class VersionNotFoundError(ForcenError):
    """Raised when a requested version manifest does not exist."""


def load_manifest(workspace: Path, seq: int) -> Dict[str, Any]:
    """Load manifest for version *seq* from *workspace* or raise VersionNotFoundError."""

    ledger = Ledger(workspace)
    try:
        return ledger.read_manifest(seq)
    except FileNotFoundError as exc:  # pragma: no cover - handled by caller tests
        raise VersionNotFoundError(f"version {seq} not found") from exc


def diff_manifests(manifest_a: Dict[str, Any], manifest_b: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a structured diff between two manifests."""

    checksums_a = manifest_a.get("artifact_checksums", {}) or {}
    checksums_b = manifest_b.get("artifact_checksums", {}) or {}
    sizes_a = manifest_a.get("artifact_sizes", {}) or {}
    sizes_b = manifest_b.get("artifact_sizes", {}) or {}
    row_counts_a = manifest_a.get("row_counts", {}) or {}
    row_counts_b = manifest_b.get("row_counts", {}) or {}
    validation_a = manifest_a.get("validation_summary", {}) or {}
    validation_b = manifest_b.get("validation_summary", {}) or {}

    return {
        "seq_a": manifest_a.get("version_seq"),
        "seq_b": manifest_b.get("version_seq"),
        "tx_ids": _diff_sets(manifest_a.get("tx_ids", []), manifest_b.get("tx_ids", [])),
        "artifact_checksums": _diff_dicts(checksums_a, checksums_b),
        "artifact_sizes": _diff_dicts(sizes_a, sizes_b),
        "row_counts": {
            "a": row_counts_a,
            "b": row_counts_b,
            "delta": _diff_numeric(row_counts_a, row_counts_b),
        },
        "validation_summary": {
            "a": validation_a,
            "b": validation_b,
            "delta": _diff_numeric(validation_a, validation_b),
        },
    }


def _diff_sets(values_a: Any, values_b: Any) -> Dict[str, Any]:
    set_a = set(values_a or [])
    set_b = set(values_b or [])
    return {
        "only_in_a": sorted(set_a - set_b),
        "only_in_b": sorted(set_b - set_a),
    }


def _diff_dicts(dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    diff: Dict[str, Dict[str, Any]] = {}
    keys = set(dict_a.keys()) | set(dict_b.keys())
    for key in sorted(keys):
        val_a = dict_a.get(key)
        val_b = dict_b.get(key)
        if val_a != val_b:
            diff[key] = {"a": val_a, "b": val_b}
    return diff


def _diff_numeric(dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> Dict[str, int]:
    diff: Dict[str, int] = {}
    keys = set(dict_a.keys()) | set(dict_b.keys())
    for key in sorted(keys):
        try:
            val_a = int(dict_a.get(key, 0))
        except (TypeError, ValueError):
            val_a = 0
        try:
            val_b = int(dict_b.get(key, 0))
        except (TypeError, ValueError):
            val_b = 0
        delta = val_b - val_a
        if delta != 0:
            diff[key] = delta
    return diff

