"""Transaction submission pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ..config import load_config_bundle
from ..exceptions import ConfigError, ForcenError
from ..ledger.storage import Ledger
from ..transactions import NormalizationConfig, load_transaction
from ..transactions.txid import compute_tx_id
from ..validators import ValidationIssue
from .lint import lint_transaction


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
    normalization = normalization or NormalizationConfig()

    lint_report = lint_transaction(
        transaction_dir=transaction_dir,
        config_dir=config_dir,
        normalization=normalization,
    )

    if lint_report.has_errors:
        raise SubmitError("transaction rejected due to validation errors")

    config = load_config_bundle(config_dir)
    tx_data = load_transaction(transaction_dir, normalization=normalization)
    tx_id = lint_report.tx_id

    ledger = Ledger(workspace)
    if ledger.has_transaction(tx_id):
        return SubmitResult(tx_id=tx_id, accepted=False, version_seq=None, warnings=lint_report.warning_count)

    rows_added, row_counts = ledger.append_observations(config, tx_data.measurements, tx_id)
    dsl_lines_added = ledger.append_updates(transaction_dir)

    config_hashes = _hash_config(config_dir)
    input_hashes = _hash_transaction_inputs(transaction_dir)

    ledger.append_transaction_entry(
        tx_id=tx_id,
        code_version=_detect_code_version(),
        config_hashes=config_hashes,
        input_hashes=input_hashes,
        rows_added=rows_added,
        dsl_lines_added=dsl_lines_added,
        issues=_rebuild_issues(lint_report.issues),
    )

    version_seq = ledger.write_version(
        tx_id=tx_id,
        issues=_rebuild_issues(lint_report.issues),
        config_hashes=config_hashes,
        input_hashes=input_hashes,
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
