"""Build and publish canonical forest census artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from .adapters import load_historical_events
from .assembly import assemble_events
from .config import Config, load_config
from .validate import Issue, validate_census, write_diagnostics


def build_census(
    raw_dir: str | Path = "data/raw/forest_census",
    config_dir: str | Path = "config",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    config = load_config(config_dir)
    events = load_historical_events(raw_dir, config)
    census = assemble_events(events, config)
    issues = validate_census(census, config)

    parquet_path = Path(output_path) if output_path is not None else config.output_parquet
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    census.to_parquet(parquet_path, index=False)
    manifest_path = (
        parquet_path.with_name("manifest.json")
        if output_path is not None
        else config.output_manifest
    )
    _write_manifest(
        census,
        issues=issues,
        raw_dir=Path(raw_dir),
        config=config,
        parquet_path=parquet_path,
        manifest_path=manifest_path,
    )
    diagnostics_dir = parquet_path.parent / "diagnostics"
    write_diagnostics(issues, diagnostics_dir)
    return census


def _write_manifest(
    census: pd.DataFrame,
    issues: list[Issue],
    raw_dir: Path,
    config: Config,
    parquet_path: Path,
    manifest_path: Path,
) -> None:
    issues_df = pd.DataFrame([issue.to_record() for issue in issues])
    manifest = {
        "artifact": str(parquet_path),
        "artifact_sha256": _sha256(parquet_path),
        "rows": int(len(census)),
        "surveys": census.groupby("survey_id").size().astype(int).to_dict(),
        "field_status": census.groupby("field_status").size().astype(int).to_dict(),
        "interpreted_status": census.groupby("interpreted_status").size().astype(int).to_dict(),
        "diagnostics": {
            "total": int(len(issues)),
            "by_severity": issues_df.groupby("severity").size().astype(int).to_dict()
            if not issues_df.empty
            else {},
            "by_code": issues_df.groupby("code").size().astype(int).to_dict()
            if not issues_df.empty
            else {},
        },
        "inputs": {
            str(path): _sha256(path)
            for path in sorted(raw_dir.glob("*.csv"))
        },
        "config": {
            str(path): _sha256(path)
            for path in sorted(config.config_dir.glob("*.toml"))
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
