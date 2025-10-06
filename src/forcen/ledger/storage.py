"""Ledger storage helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

from ..assembly import assemble_observations
from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from ..validators import ValidationIssue


class Ledger:
    """Filesystem-backed ledger for accepted transactions."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.observations_csv = self.root / "observations_long.csv"
        self.observations_parquet = self.root / "observations_long.parquet"
        self.updates_log = self.root / "updates_log.tdl"
        self.transactions_log = self.root / "transactions.jsonl"
        self.versions_dir = self.root / "versions"
        self.versions_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    def has_transaction(self, tx_id: str) -> bool:
        if not self.transactions_log.exists():
            return False
        with self.transactions_log.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("tx_id") == tx_id:
                    return True
        return False

    def append_updates(self, tx_dir: Path) -> int:
        updates_path = tx_dir / "updates.tdl"
        if not updates_path.exists():
            return 0
        text = updates_path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        with self.updates_log.open("a", encoding="utf-8") as fh:
            if text and not text.endswith("\n"):
                text += "\n"
            fh.write(text)
        return len(lines)

    def append_observations(
        self,
        config: ConfigBundle,
        measurements: List[MeasurementRow],
        tx_id: str,
    ) -> Tuple[int, Dict[str, int]]:
        rows = assemble_observations(measurements, config, tx_id)
        df_new = pd.DataFrame(rows)
        df_new["standing"] = df_new["standing"].astype("boolean")

        if self.observations_csv.exists():
            df_existing = pd.read_csv(self.observations_csv)
            combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            combined = df_new

        combined = combined.sort_values(
            ["survey_id", "site", "plot", "tag", "obs_id"],
            kind="mergesort",
        ).reset_index(drop=True)

        combined.to_csv(self.observations_csv, index=False)
        combined.to_parquet(self.observations_parquet, index=False)

        by_origin = (
            combined["origin"].value_counts().sort_index().to_dict()  # type: ignore[return-value]
        )
        return len(rows), {str(k): int(v) for k, v in by_origin.items()}

    def append_transaction_entry(
        self,
        tx_id: str,
        code_version: str,
        config_hashes: Dict[str, str],
        input_hashes: Dict[str, str],
        rows_added: int,
        dsl_lines_added: int,
        issues: Iterable[ValidationIssue],
    ) -> None:
        record = {
            "tx_id": tx_id,
            "accepted_at": datetime.now(timezone.utc).isoformat(),
            "code_version": code_version,
            "config_hashes": config_hashes,
            "input_checksums": input_hashes,
            "rows_added": rows_added,
            "dsl_lines_added": dsl_lines_added,
            "validation_summary": _summarize_issues(list(issues)),
        }
        with self.transactions_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    def read_transactions(self) -> List[dict]:
        if not self.transactions_log.exists():
            return []
        records: List[dict] = []
        with self.transactions_log.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def list_versions(self) -> List[int]:
        versions = [
            int(path.name)
            for path in self.versions_dir.iterdir()
            if path.is_dir() and path.name.isdigit()
        ]
        return sorted(versions)

    def write_version(
        self,
        tx_ids: List[str],
        validation_summary: Dict[str, int],
        config_hashes: Dict[str, str],
        input_hashes: Dict[str, str],
        code_version: str,
    ) -> int:
        seq = self._next_version_seq()
        version_dir = self.versions_dir / f"{seq:04d}"
        version_dir.mkdir(parents=True, exist_ok=True)

        observations_dest = version_dir / "observations_long.csv"
        parquet_dest = version_dir / "observations_long.parquet"
        manifest_path = version_dir / "manifest.json"

        _copy_file(self.observations_csv, observations_dest)
        _copy_file(self.observations_parquet, parquet_dest)

        manifest = {
            "version_seq": seq,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "code_version": code_version,
            "tx_ids": tx_ids,
            "config_hashes": config_hashes,
            "input_checksums": input_hashes,
            "validation_summary": validation_summary,
            "artifact_checksums": {
                "observations_long.csv": _sha256_file(observations_dest),
                "observations_long.parquet": _sha256_file(parquet_dest),
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return seq

    # ------------------------------------------------------------------
    def _next_version_seq(self) -> int:
        existing = [
            int(path.name)
            for path in self.versions_dir.iterdir()
            if path.is_dir() and path.name.isdigit()
        ]
        return (max(existing) + 1) if existing else 1


def _copy_file(src: Path, dest: Path) -> None:
    dest.write_bytes(src.read_bytes())


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _summarize_issues(issues: List[ValidationIssue]) -> dict:
    return {
        "errors": sum(1 for issue in issues if issue.is_error()),
        "warnings": sum(1 for issue in issues if not issue.is_error()),
    }
