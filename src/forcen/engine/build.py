"""Rebuild workspace artifacts from ledger state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from ..config import load_config_bundle
from ..exceptions import ForcenError
from ..ledger.storage import Ledger


@dataclass
class BuildResult:
    version_seq: int
    tx_count: int


class BuildError(ForcenError):
    pass


def build_workspace(config_dir: Path, workspace: Path) -> BuildResult:
    config_dir = Path(config_dir)
    workspace = Path(workspace)

    config = load_config_bundle(config_dir)
    ledger = Ledger(workspace)

    if not ledger.observations_csv.exists():
        raise BuildError("No observations found; submit a transaction first")

    records = ledger.read_transactions()
    tx_ids = [record.get("tx_id") for record in records if "tx_id" in record]
    if not tx_ids:
        raise BuildError("No transactions recorded; nothing to build")

    validation_summary = _aggregate_validation(records)
    config_hashes = _hash_config(config_dir)

    version_seq = ledger.write_version(
        tx_ids=tx_ids,
        validation_summary=validation_summary,
        config_hashes=config_hashes,
        input_hashes={},
        code_version="unknown",
    )

    return BuildResult(version_seq=version_seq, tx_count=len(tx_ids))


def _aggregate_validation(records: list[dict]) -> Dict[str, int]:
    total_errors = 0
    total_warnings = 0
    for record in records:
        summary = record.get("validation_summary") or {}
        total_errors += int(summary.get("errors", 0))
        total_warnings += int(summary.get("warnings", 0))
    return {"errors": total_errors, "warnings": total_warnings}


def _hash_config(config_dir: Path) -> Dict[str, str]:
    return {
        path.name: _sha256_file(path)
        for path in sorted(config_dir.glob("*.toml"))
    }


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()
