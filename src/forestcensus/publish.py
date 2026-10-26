"""Build and publish canonical forest census artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd

from .adapters import load_historical_events
from .assembly import assemble_events
from .config import Config, load_config
from .validate import Issue, validate_census, write_diagnostics


def promote_candidate(candidate: str | Path, destination: str | Path) -> dict[str, object]:
    """Promote an approved, unchanged build, preserving the previous publication."""
    source, target = Path(candidate), Path(destination)
    manifest = json.loads(source.with_name("manifest.json").read_text())
    if _sha256(source) != manifest["artifact_sha256"]:
        raise ValueError("Candidate does not match its manifest")
    for section in ("inputs", "config"):
        for name, expected in manifest[section].items():
            if _sha256(Path(name)) != expected:
                raise ValueError(f"Candidate is stale: {name} changed")
    if manifest["diagnostics"]["by_severity"].get("error", 0):
        raise ValueError("Cannot publish a candidate with validation errors")
    census = pd.read_parquet(source)
    if len(census) != manifest["rows"]:
        raise ValueError("Candidate row count does not match its manifest")
    target.parent.mkdir(parents=True, exist_ok=True)
    companions = [
        path for directory in ("diagnostics", "decisions")
        for path in sorted((source.parent / directory).glob("*")) if path.is_file()
    ]
    if target.exists():
        backup = target.parent / "publication_history" / _sha256(target)[:16]
        backup.mkdir(parents=True, exist_ok=True)
        previous = [target, target.with_name("manifest.json")]
        previous.extend(target.parent / path.relative_to(source.parent) for path in companions)
        for old in previous:
            saved = backup / old.relative_to(target.parent)
            if old.exists() and not saved.exists():
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old, saved)
    manifest["promoted_from"] = str(source)
    manifest["artifact"] = str(target)
    manifest["companion_artifacts"] = {
        str(path.relative_to(source.parent)): _sha256(path) for path in companions
    }
    # Stage complete files on the same filesystem before replacing publication.
    with tempfile.TemporaryDirectory(dir=target.parent) as staging:
        staged = Path(staging)
        shutil.copy2(source, staged / target.name)
        for path in companions:
            relative = path.relative_to(source.parent)
            (staged / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, staged / relative)
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        (staged / target.name).replace(target)
        for path in companions:
            relative = path.relative_to(source.parent)
            (target.parent / relative).parent.mkdir(parents=True, exist_ok=True)
            (staged / relative).replace(target.parent / relative)
        (staged / "manifest.json").replace(target.with_name("manifest.json"))
    return manifest


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
            for path in _input_paths(config, raw_dir)
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


def _input_paths(config: Config, raw_dir: Path) -> list[Path]:
    if not config.source_inputs:
        return sorted(raw_dir.glob("*.csv"))
    paths = []
    for source in config.source_inputs:
        if source.path.is_absolute():
            path = source.path
        elif source.base == "raw_dir":
            path = raw_dir / source.path
        elif source.base == "config":
            path = config.config_dir / source.path
        elif source.base == "project":
            path = config.config_dir.parent / source.path
        else:
            continue
        if path.exists():
            paths.append(path)
    return sorted(paths)
