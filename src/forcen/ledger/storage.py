"""Ledger storage helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from ..dsl.types import Command
from ..dsl.serialization import deserialize_command, serialize_command
from ..assembly.survey import SurveyCatalog
from ..validators import ValidationIssue


class Ledger:
    """Filesystem-backed ledger for accepted transactions."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.observations_raw_csv = self.root / "observations_raw.csv"
        self.observations_csv = self.root / "observations_long.csv"
        self.observations_parquet = self.root / "observations_long.parquet"
        self.updates_log = self.root / "updates_log.tdl"
        self.trees_view = self.root / "trees_view.csv"
        self.retag_suggestions = self.root / "retag_suggestions.csv"
        self.validation_report = self.root / "validation_report.json"
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

    def load_raw_measurements(self) -> List[MeasurementRow]:
        if not self.observations_raw_csv.exists():
            return []
        df = pd.read_csv(self.observations_raw_csv)
        rows: List[MeasurementRow] = []
        for record in df.to_dict(orient="records"):
            rows.append(
                MeasurementRow(
                    row_number=int(record.get("row_number", 0)),
                    site=str(record.get("site", "")),
                    plot=str(record.get("plot", "")),
                    tag=str(record.get("tag", "")),
                    date=pd.to_datetime(record.get("date")).date(),
                    dbh_mm=_maybe_int(record.get("dbh_mm")),
                    health=_maybe_int(record.get("health")),
                    standing=_maybe_bool(record.get("standing")),
                    notes=str(record.get("notes", "")),
                    genus=record.get("genus") or None,
                    species=record.get("species") or None,
                    code=record.get("code") or None,
                    origin=str(record.get("origin", "field")),
                    normalization_flags=[],
                    raw={},
                    tree_uid=None,
                    public_tag=None,
                    source_tx=record.get("source_tx") or None,
                )
            )
        return rows

    def write_raw_measurements(self, rows: Iterable[MeasurementRow]) -> None:
        records = [
            {
                "row_number": row.row_number,
                "site": row.site,
                "plot": row.plot,
                "tag": row.tag,
                "date": row.date.isoformat(),
                "dbh_mm": row.dbh_mm,
                "health": row.health,
                "standing": row.standing,
                "notes": row.notes,
                "genus": row.genus,
                "species": row.species,
                "code": row.code,
                "origin": row.origin,
                "source_tx": row.source_tx,
            }
            for row in rows
        ]
        df = pd.DataFrame(records)
        if not df.empty:
            df["standing"] = df["standing"].astype("boolean")
        df.to_csv(self.observations_raw_csv, index=False)

    def write_observations(
        self, config: ConfigBundle, measurements: List[MeasurementRow]
    ) -> Dict[str, int]:
        catalog = SurveyCatalog.from_config(config)
        records = []
        for row in measurements:
            survey_id = catalog.survey_for_date(row.date)
            if survey_id is None:
                continue
            obs_id = _observation_id(row)
            records.append(
                {
                    "obs_id": obs_id,
                    "survey_id": survey_id,
                    "date": row.date.isoformat(),
                    "site": row.site,
                    "plot": row.plot,
                    "tag": row.tag,
                    "public_tag": row.public_tag or row.tag,
                    "dbh_mm": row.dbh_mm,
                    "health": row.health,
                    "standing": row.standing,
                    "notes": row.notes,
                    "origin": row.origin,
                    "source_tx": row.source_tx,
                    "tree_uid": row.tree_uid,
                    "genus": row.genus,
                    "species": row.species,
                    "code": row.code,
                }
            )

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values(
                ["survey_id", "site", "plot", "tag", "obs_id"],
                kind="mergesort",
            ).reset_index(drop=True)
            df["standing"] = df["standing"].astype("boolean")
            for column in [
                "site",
                "plot",
                "tag",
                "public_tag",
                "notes",
                "origin",
                "source_tx",
                "tree_uid",
                "genus",
                "species",
                "code",
            ]:
                df[column] = df[column].astype("string")

        df.to_csv(self.observations_csv, index=False)
        df.to_parquet(self.observations_parquet, index=False)

        by_origin = (
            df["origin"].value_counts().sort_index().to_dict() if not df.empty else {}
        )
        return {str(k): int(v) for k, v in by_origin.items()}

    def append_transaction_entry(
        self,
        tx_id: str,
        code_version: str,
        config_hashes: Dict[str, str],
        input_hashes: Dict[str, str],
        rows_added: int,
        dsl_lines_added: int,
        row_counts: Dict[str, int],
        issues: Iterable[ValidationIssue],
        commands: Iterable[Command],
    ) -> None:
        record = {
            "tx_id": tx_id,
            "accepted_at": datetime.now(timezone.utc).isoformat(),
            "code_version": code_version,
            "config_hashes": config_hashes,
            "input_checksums": input_hashes,
            "rows_added": rows_added,
            "dsl_lines_added": dsl_lines_added,
            "row_counts": row_counts,
            "validation_summary": _summarize_issues(list(issues)),
            "commands": [serialize_command(cmd) for cmd in commands],
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

    def load_commands(self) -> List[Command]:
        commands: List[Command] = []
        for record in self.read_transactions():
            for data in record.get("commands", []):
                try:
                    commands.append(deserialize_command(data))
                except Exception:
                    continue
        return commands

    def list_versions(self) -> List[int]:
        versions = [
            int(path.name)
            for path in self.versions_dir.iterdir()
            if path.is_dir() and path.name.isdigit()
        ]
        return sorted(versions)

    def write_tree_outputs(self, tree_rows: List[dict], retag_rows: List[dict]) -> None:
        import pandas as pd

        tree_columns = [
            "tree_uid",
            "survey_id",
            "public_tag",
            "site",
            "plot",
            "genus",
            "species",
            "code",
            "origin",
        ]
        retag_columns = [
            "survey_id",
            "plot",
            "lost_tree_uid",
            "lost_public_tag",
            "lost_max_dbh_mm",
            "new_tree_uid",
            "new_public_tag",
            "new_max_dbh_mm",
            "delta_mm",
            "delta_pct",
            "suggested_alias_line",
        ]

        pd.DataFrame(tree_rows, columns=tree_columns).to_csv(
            self.trees_view, index=False
        )
        pd.DataFrame(retag_rows, columns=retag_columns).to_csv(
            self.retag_suggestions, index=False
        )

    def write_validation_report(self, payload: dict) -> None:
        self.validation_report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_version(
        self,
        tx_ids: List[str],
        validation_summary: Dict[str, int],
        config_hashes: Dict[str, str],
        input_hashes: Dict[str, str],
        code_version: str,
        row_counts: Dict[str, int],
    ) -> int:
        seq = self._next_version_seq()
        version_dir = self.versions_dir / f"{seq:04d}"
        version_dir.mkdir(parents=True, exist_ok=True)

        observations_dest = version_dir / "observations_long.csv"
        parquet_dest = version_dir / "observations_long.parquet"
        trees_dest = version_dir / "trees_view.csv"
        retag_dest = version_dir / "retag_suggestions.csv"
        updates_dest = version_dir / "updates_log.tdl"
        validation_dest = version_dir / "validation_report.json"
        manifest_path = version_dir / "manifest.json"

        _copy_file(self.observations_csv, observations_dest)
        _copy_file(self.observations_parquet, parquet_dest)
        if self.trees_view.exists():
            _copy_file(self.trees_view, trees_dest)
        if self.retag_suggestions.exists():
            _copy_file(self.retag_suggestions, retag_dest)
        if self.updates_log.exists():
            _copy_file(self.updates_log, updates_dest)
        if self.validation_report.exists():
            _copy_file(self.validation_report, validation_dest)

        manifest = {
            "version_seq": seq,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "code_version": code_version,
            "tx_ids": tx_ids,
            "config_hashes": config_hashes,
            "input_checksums": input_hashes,
            "validation_summary": validation_summary,
            "row_counts": row_counts,
            "artifact_checksums": {
                "observations_long.csv": _sha256_file(observations_dest),
                "observations_long.parquet": _sha256_file(parquet_dest),
                **(
                    {"trees_view.csv": _sha256_file(trees_dest)}
                    if trees_dest.exists()
                    else {}
                ),
                **(
                    {"retag_suggestions.csv": _sha256_file(retag_dest)}
                    if retag_dest.exists()
                    else {}
                ),
                **(
                    {"updates_log.tdl": _sha256_file(updates_dest)}
                    if updates_dest.exists()
                    else {}
                ),
                **(
                    {"validation_report.json": _sha256_file(validation_dest)}
                    if validation_dest.exists()
                    else {}
                ),
            },
            "artifact_sizes": {
                "observations_long.csv": _file_size(observations_dest),
                "observations_long.parquet": _file_size(parquet_dest),
                **(
                    {"trees_view.csv": _file_size(trees_dest)}
                    if trees_dest.exists()
                    else {}
                ),
                **(
                    {"retag_suggestions.csv": _file_size(retag_dest)}
                    if retag_dest.exists()
                    else {}
                ),
                **(
                    {"updates_log.tdl": _file_size(updates_dest)}
                    if updates_dest.exists()
                    else {}
                ),
                **(
                    {"validation_report.json": _file_size(validation_dest)}
                    if validation_dest.exists()
                    else {}
                ),
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


def _observation_id(row: MeasurementRow) -> str:
    seed = "|".join(
        [
            str(row.source_tx or "unknown"),
            str(row.row_number),
            row.site,
            row.plot,
            row.tag,
            row.date.isoformat(),
        ]
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _maybe_int(value) -> Optional[int]:
    if value is None or pd.isna(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _maybe_bool(value) -> Optional[bool]:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).lower()
    if text in {"true", "t", "1", "yes"}:
        return True
    if text in {"false", "f", "0", "no"}:
        return False
    return None


def _file_size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0
