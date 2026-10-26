"""Evidence ledger extraction for raw and historical forest census records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pandas as pd

from .config import Config


XLSX_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

CURRENT_INPUT_FILES = {
    "2023_and_prior.csv",
    "2024_spring.csv",
    "2024_fall.csv",
    "2025_spring.csv",
}

NOTE_KEYWORDS = {
    "dead": ("dead",),
    "fallen": ("fallen", "fall", "snapped", "broken"),
    "missing": ("missing", "unfound", "not found", "could not find", "couldn't find"),
    "tag": ("tag", "old tag", "new tag"),
    "tag_change": ("old tag", "new tag", "tag on trunk", "to "),
    "new": ("new", "new tree"),
    "old": ("old", "old tree"),
    "stem": ("stem", "stems", "trunk", "trunks", "multistem", "multi-stem", "split"),
    "poison_ivy": ("poison", "ivy"),
    "vine_or_parasite": ("vine", "liana", "parasite"),
    "knot": ("knot",),
    "non_circular": ("not circle", "non-circular", "non circular"),
    "dbh_uncertain": ("might be", "maybe", "approx", "check", "?"),
    "dbh_negated_note": ("not 450", "not 450", "not dbh", "not 50"),
    "no_second_stem": ("no second stem", "no 2nd stem"),
    "confirm": ("confirm", "check", "?"),
    "standing": ("standing", "stnd"),
    "alive": ("alive",),
}

SOURCE_CATALOG_COLUMNS = [
    "source_id",
    "source_path",
    "source_group",
    "source_kind",
    "evidence_rank",
    "canonical_role",
    "description",
    "sha256",
]

SHEET_CATALOG_COLUMNS = [
    "source_id",
    "source_path",
    "sheet_name",
    "sheet_role",
    "row_count",
    "column_count",
    "headers_json",
]

EVIDENCE_COLUMNS = [
    "evidence_id",
    "source_id",
    "source_path",
    "source_sheet",
    "source_row",
    "source_kind",
    "evidence_rank",
    "canonical_role",
    "observation_role",
    "survey_id",
    "date",
    "year",
    "month",
    "day",
    "site",
    "zone",
    "plot",
    "public_tag_raw",
    "tree_code_raw",
    "old_tag_raw",
    "datasheet_slot_raw",
    "genus_raw",
    "species_raw",
    "taxon_raw",
    "dbh_mm_raw",
    "health_raw",
    "alive_raw",
    "standing_raw",
    "poison_ivy_raw",
    "notes_raw",
    "note_flags",
    "raw_payload_json",
]

NOTE_COLUMNS = [
    "note_id",
    "evidence_id",
    "source_id",
    "source_path",
    "source_sheet",
    "source_row",
    "note_field",
    "survey_id",
    "plot",
    "public_tag_raw",
    "datasheet_slot_raw",
    "note_text",
    "note_flags",
]

TAG_CHANGE_COLUMNS = [
    "assertion_id",
    "source_id",
    "source_path",
    "source_sheet",
    "source_row",
    "old_tree_code",
    "new_tree_code",
    "old_plot",
    "old_tag",
    "old_taxon_hint",
    "new_plot",
    "new_tag",
    "new_taxon_hint",
    "change_type",
    "year_changed",
    "raw_payload_json",
]


@dataclass(frozen=True)
class SourceInfo:
    path: Path
    root: Path
    source_group: str
    source_kind: str
    evidence_rank: str
    canonical_role: str
    description: str

    @property
    def source_path(self) -> str:
        try:
            return str(self.path.relative_to(self.root))
        except ValueError:
            return str(self.path)

    @property
    def source_id(self) -> str:
        return _hash_id("source", self.source_path)


@dataclass(frozen=True)
class LedgerFrames:
    source_catalog: pd.DataFrame
    source_sheets: pd.DataFrame
    evidence_observations: pd.DataFrame
    evidence_notes: pd.DataFrame
    tag_change_assertions: pd.DataFrame


def build_evidence_ledger(
    raw_dir: str | Path,
    archive_dir: str | Path,
    config: Config,
) -> LedgerFrames:
    """Build queryable evidence tables without changing canonical interpretation."""

    raw_dir = Path(raw_dir)
    archive_dir = Path(archive_dir)
    sources: list[dict[str, object]] = []
    sheets: list[dict[str, object]] = []
    observations: list[dict[str, object]] = []
    notes: list[dict[str, object]] = []
    tag_changes: list[dict[str, object]] = []

    for source in _current_input_sources(raw_dir, config):
        _extract_source(source, config, sources, sheets, observations, notes, tag_changes)

    if archive_dir.exists():
        for source in _archive_sources(archive_dir):
            _extract_source(source, config, sources, sheets, observations, notes, tag_changes)

    return LedgerFrames(
        source_catalog=_frame(sources, SOURCE_CATALOG_COLUMNS),
        source_sheets=_frame(sheets, SHEET_CATALOG_COLUMNS),
        evidence_observations=_frame(observations, EVIDENCE_COLUMNS),
        evidence_notes=_frame(notes, NOTE_COLUMNS),
        tag_change_assertions=_frame(tag_changes, TAG_CHANGE_COLUMNS),
    )


def write_evidence_ledger(frames: LedgerFrames, out_dir: str | Path) -> dict[str, object]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, str] = {}
    for name, frame in [
        ("source_catalog", frames.source_catalog),
        ("source_sheets", frames.source_sheets),
        ("evidence_observations", frames.evidence_observations),
        ("evidence_notes", frames.evidence_notes),
        ("tag_change_assertions", frames.tag_change_assertions),
    ]:
        parquet_path = out_dir / f"{name}.parquet"
        csv_path = out_dir / f"{name}.csv"
        frame.to_parquet(parquet_path, index=False)
        frame.to_csv(csv_path, index=False)
        outputs[name] = str(parquet_path)

    summary = evidence_summary(frames)
    summary["outputs"] = outputs
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    summary["summary"] = str(summary_path)
    return summary


def evidence_summary(frames: LedgerFrames) -> dict[str, object]:
    observations = frames.evidence_observations
    return {
        "sources": int(len(frames.source_catalog)),
        "sheets": int(len(frames.source_sheets)),
        "observations": int(len(observations)),
        "notes": int(len(frames.evidence_notes)),
        "tag_change_assertions": int(len(frames.tag_change_assertions)),
        "observations_by_role": _value_counts(observations, "observation_role"),
        "observations_by_rank": _value_counts(observations, "evidence_rank"),
        "notes_by_flag": _note_flag_counts(frames.evidence_notes),
    }


def _extract_source(
    source: SourceInfo,
    config: Config,
    sources: list[dict[str, object]],
    sheets: list[dict[str, object]],
    observations: list[dict[str, object]],
    notes: list[dict[str, object]],
    tag_changes: list[dict[str, object]],
) -> None:
    sources.append(
        {
            "source_id": source.source_id,
            "source_path": source.source_path,
            "source_group": source.source_group,
            "source_kind": source.source_kind,
            "evidence_rank": source.evidence_rank,
            "canonical_role": source.canonical_role,
            "description": source.description,
            "sha256": _sha256(source.path),
        }
    )

    if source.path.suffix.lower() == ".csv":
        rows = _read_csv_rows(source.path)
        if rows:
            _add_sheet_catalog(sheets, source, "CSV", "table", rows)
            _extract_csv_rows(source, "CSV", rows, config, observations, notes)
        return

    if source.path.suffix.lower() != ".xlsx":
        return

    for sheet_name, rows in _read_xlsx_tables(source.path).items():
        sheet_role = _sheet_role(sheet_name)
        _add_sheet_catalog(sheets, source, sheet_name, sheet_role, rows)
        if sheet_role == "tag_changes":
            _extract_tag_changes(source, sheet_name, rows, tag_changes)
        elif sheet_role == "observations":
            _extract_xlsx_rows(source, sheet_name, rows, config, observations, notes)


def _current_input_sources(raw_dir: Path, config: Config) -> Iterable[SourceInfo]:
    if config.source_inputs:
        for item in config.source_inputs:
            path = _resolve_config_source_path(item.path, item.base, raw_dir, config)
            if not path.exists():
                if item.required:
                    raise FileNotFoundError(path)
                continue
            yield SourceInfo(
                path=path,
                root=Path.cwd(),
                source_group="current_pipeline_inputs",
                source_kind="accepted_input_csv" if item.origin == "historical" else f"{item.origin}_input_csv",
                evidence_rank="accepted_input",
                canonical_role="canonical_input",
                description=f"Configured canonical input {item.id} using {item.adapter}.",
            )
        return
    for path in sorted(raw_dir.glob("*.csv")):
        if path.name not in CURRENT_INPUT_FILES:
            continue
        yield SourceInfo(
            path=path,
            root=raw_dir,
            source_group="current_pipeline_inputs",
            source_kind="accepted_input_csv",
            evidence_rank="accepted_input",
            canonical_role="canonical_input",
            description="Current accepted raw input used by the canonical pipeline.",
        )


def _resolve_config_source_path(path: Path, base: str, raw_dir: Path, config: Config) -> Path:
    if path.is_absolute():
        return path
    if base == "raw_dir":
        return raw_dir / path
    if base == "config":
        return config.config_dir / path
    if base == "project":
        return config.config_dir.parent / path
    raise ValueError(f"Unknown source base {base!r}")


def _archive_sources(archive_dir: Path) -> Iterable[SourceInfo]:
    for path in sorted(archive_dir.rglob("*")):
        if path.suffix.lower() not in {".csv", ".xlsx"}:
            continue
        kind, rank, role, description = _classify_archive_source(path, archive_dir)
        yield SourceInfo(
            path=path,
            root=archive_dir,
            source_group="original_drive_records",
            source_kind=kind,
            evidence_rank=rank,
            canonical_role=role,
            description=description,
        )


def _classify_archive_source(path: Path, archive_dir: Path) -> tuple[str, str, str, str]:
    rel = path.relative_to(archive_dir)
    text = str(rel).lower()
    if text.startswith("2020/"):
        return ("original_csv", "primary", "evidence_only", "Uploaded 2020 tree data CSV.")
    if text.startswith("2022/"):
        return ("year_workbook", "primary", "evidence_only", "2022 tree workbook with QAQC/current and paired context sheets.")
    if "dated_reu_tree_entries" in text:
        return ("dated_entry_workbook", "primary", "evidence_only", "Dated 2023 REU entry workbook.")
    if "raw" in text:
        return ("raw_merge_workbook", "strong_secondary", "evidence_only", "Raw merged 2023 export.")
    if "qaqc" in text:
        return ("qaqc_workbook", "strong_secondary", "evidence_only", "QAQC in-progress 2023 workbook.")
    if "inprogress" in text:
        return ("in_progress_workbook", "strong_secondary", "evidence_only", "All-years in-progress workbook with tag-change notes.")
    if "cleaned" in text:
        return ("cleaned_all_years_workbook", "weak_secondary", "evidence_only", "Cleaned all-years workbook; derived comparison evidence.")
    if "outdated" in text or "all_years" in text:
        return ("all_years_workbook", "weak_secondary", "evidence_only", "Derived all-years workbook.")
    return ("reference_workbook", "secondary", "evidence_only", "Reference workbook from Drive archive.")


def _extract_csv_rows(
    source: SourceInfo,
    sheet_name: str,
    rows: list[list[str]],
    config: Config,
    observations: list[dict[str, object]],
    notes: list[dict[str, object]],
) -> None:
    if not rows:
        return
    header = [_clean_header(item) for item in rows[0]]
    for row_index, row in enumerate(rows[1:], start=2):
        payload = _payload(header, row)
        if not _payload_has_values(payload):
            continue
        if source.source_group == "current_pipeline_inputs":
            mapped = _map_current_input_payload(source.path.name, payload, config)
        else:
            mapped = _map_observation_payload(payload, source.path.name, observation_role="observed_current")
            if source.source_path.startswith("2020/"):
                mapped.update({"survey_id": "June_2020", "year": "2020", "date": "2020-06-15"})
        _add_observation(source, sheet_name, row_index, mapped, payload, observations, notes)


def _extract_xlsx_rows(
    source: SourceInfo,
    sheet_name: str,
    rows: list[list[str]],
    config: Config,
    observations: list[dict[str, object]],
    notes: list[dict[str, object]],
) -> None:
    if not rows:
        return
    header = [_clean_header(item) for item in rows[0]]
    for row_index, row in enumerate(rows[1:], start=2):
        payload = _payload(header, row)
        if not _payload_has_values(payload):
            continue
        for mapped in _map_xlsx_payloads(source, sheet_name, payload, config):
            _add_observation(source, sheet_name, row_index, mapped, payload, observations, notes)


def _map_current_input_payload(filename: str, payload: dict[str, str], config: Config) -> dict[str, str]:
    if filename == "2023_and_prior.csv":
        year = _pick(payload, "year")
        month = _pick(payload, "month")
        day = _pick(payload, "day")
        return {
            "observation_role": "accepted_input_observation",
            "survey_id": _survey_from_parts(year, month, day, config),
            "date": _date_from_parts(year, month, day),
            "year": year,
            "month": month,
            "day": day,
            "site": "BRNV",
            "zone": _pick(payload, "level"),
            "plot": _pick(payload, "plot"),
            "public_tag_raw": _pick(payload, "tree_number"),
            "tree_code_raw": _pick(payload, "tree_code"),
            "old_tag_raw": _pick(payload, "old_tag"),
            "datasheet_slot_raw": _pick(payload, "trunk_number"),
            "taxon_raw": _pick(payload, "spp"),
            "dbh_mm_raw": _pick(payload, "dbh_mm"),
            "health_raw": _pick(payload, "health"),
            "alive_raw": _pick(payload, "alive"),
            "standing_raw": _pick(payload, "standing"),
            "notes_raw": _pick(payload, "notes"),
        }
    if filename == "2024_fall.csv":
        return {
            "observation_role": "accepted_input_observation",
            "survey_id": "October_2024",
            "date": "2024-10-02",
            "year": "2024",
            "month": "10",
            "day": "2",
            "site": "BRNV",
            "zone": _pick(payload, "zone"),
            "plot": _plot_from_zone_number(_pick(payload, "zone"), _pick(payload, "plot")),
            "public_tag_raw": _pick(payload, "tree_number"),
            "tree_code_raw": _pick(payload, "id"),
            "old_tag_raw": _pick(payload, "oldtag"),
            "datasheet_slot_raw": _pick(payload, "stem_number"),
            "genus_raw": _pick(payload, "new_genus") or _pick(payload, "genus"),
            "species_raw": _pick(payload, "new_species") or _pick(payload, "spp"),
            "dbh_mm_raw": _pick(payload, "dbh"),
            "health_raw": _pick(payload, "health"),
            "alive_raw": _pick(payload, "alive"),
            "standing_raw": _pick(payload, "standing"),
            "notes_raw": _pick(payload, "notes"),
        }
    return {
        "observation_role": "accepted_input_observation",
        "survey_id": _pick(payload, "survey_id") or ("April_2025" if filename == "2025_spring.csv" else ""),
        "date": _pick(payload, "date"),
        "site": _pick(payload, "site") or "BRNV",
        "zone": _pick(payload, "zone"),
        "plot": _plot_from_zone_number(_pick(payload, "zone"), _pick(payload, "plot")),
        "public_tag_raw": _pick(payload, "tree_number"),
        "tree_code_raw": _pick(payload, "tree_code") or _pick(payload, "id"),
        "old_tag_raw": _pick(payload, "old_tag"),
        "datasheet_slot_raw": _pick(payload, "trunk_number"),
        "genus_raw": _pick(payload, "genus"),
        "species_raw": _pick(payload, "spp"),
        "dbh_mm_raw": _pick(payload, "dbh_mm"),
        "health_raw": _pick(payload, "health"),
        "alive_raw": _pick(payload, "alive"),
        "standing_raw": _pick(payload, "standing"),
        "notes_raw": _pick(payload, "notes"),
    }


def _map_xlsx_payloads(
    source: SourceInfo,
    sheet_name: str,
    payload: dict[str, str],
    config: Config,
) -> list[dict[str, str]]:
    headers = set(payload)
    if "2023_dbh_mm" in headers or "2023_health" in headers:
        return [
            _map_paired_year_payload(payload, "2022", "carried_forward_context", config),
            _map_paired_year_payload(payload, "2023", "observed_current", config),
        ]
    if "2021 dbh (mm)" in headers and "2022 dbh (cm)" in headers:
        return [
            _map_observation_payload(payload, source.path.name, observation_role="carried_forward_context")
            | {
                "survey_id": "June_2021",
                "year": "2021",
                "dbh_mm_raw": _pick(payload, "2021 dbh (mm)"),
                "health_raw": _pick(payload, "2021 health (dead=0)"),
                "alive_raw": _pick(payload, "2021 alive:1 or dead:0"),
                "notes_raw": _pick(payload, "2021 notes"),
            },
            _map_observation_payload(payload, source.path.name, observation_role="observed_current")
            | {
                "survey_id": "June_2022",
                "year": _pick(payload, "year") or "2022",
                "month": _pick(payload, "month"),
                "day": _pick(payload, "day"),
                "date": _date_from_parts(_pick(payload, "year") or "2022", _pick(payload, "month"), _pick(payload, "day")),
                "dbh_mm_raw": _cm_to_mm_raw(_pick(payload, "2022 dbh (cm)")),
                "health_raw": _pick(payload, "2022 health (dead=0)"),
                "alive_raw": _pick(payload, "2022 alive:1 or dead:0"),
                "notes_raw": _pick(payload, "2022 notes"),
            },
        ]
    if "2022 dbh (cm)" in headers or "2022 health (dead=0)" in headers:
        mapped = _map_observation_payload(payload, source.path.name, observation_role="observed_current")
        mapped.update(
            {
                "survey_id": "June_2022",
                "year": _pick(payload, "year") or "2022",
                "month": _pick(payload, "month"),
                "day": _pick(payload, "day"),
                "date": _date_from_parts(_pick(payload, "year") or "2022", _pick(payload, "month"), _pick(payload, "day")),
                "dbh_mm_raw": _cm_to_mm_raw(_pick(payload, "2022 dbh (cm)")),
                "health_raw": _pick(payload, "2022 health (dead=0)"),
                "alive_raw": _pick(payload, "2022 alive:1 or dead:0"),
                "notes_raw": _pick(payload, "2022 notes"),
            }
        )
        return [mapped]
    if "survey_id" in headers and "tree_number" in headers:
        return [_map_recent_cleaned_payload(payload, observation_role="derived_cleaned")]
    return [_map_observation_payload(payload, source.path.name, observation_role=_default_observation_role(source, sheet_name))]


def _map_paired_year_payload(
    payload: dict[str, str],
    year_prefix: str,
    observation_role: str,
    config: Config,
) -> dict[str, str]:
    year = _pick(payload, f"{year_prefix}_year") or year_prefix
    month = _pick(payload, f"{year_prefix}_month")
    day = _pick(payload, f"{year_prefix}_day")
    plot = _pick(payload, f"{year_prefix}_plot") or _pick(payload, "plot")
    return {
        "observation_role": observation_role,
        "survey_id": _survey_from_parts(year, month, day, config),
        "date": _date_from_parts(year, month, day),
        "year": year,
        "month": month,
        "day": day,
        "site": "BRNV",
        "zone": _pick(payload, f"{year_prefix}_zone") or _zone_from_plot(plot),
        "plot": plot,
        "public_tag_raw": _pick(payload, f"{year_prefix}_tree_number"),
        "tree_code_raw": _pick(payload, f"{year_prefix}_tree_code"),
        "old_tag_raw": _pick(payload, f"{year_prefix}_old_tag"),
        "datasheet_slot_raw": _pick(payload, f"{year_prefix}_trunk_number"),
        "taxon_raw": _pick(payload, f"{year_prefix}_species"),
        "dbh_mm_raw": _pick(payload, f"{year_prefix}_dbh_mm"),
        "health_raw": _pick(payload, f"{year_prefix}_health"),
        "alive_raw": _pick(payload, f"{year_prefix}_alive:1 or dead:0"),
        "standing_raw": _pick(payload, f"{year_prefix}_standing:1 or fallen:0"),
        "notes_raw": _pick(payload, f"{year_prefix}_notes"),
    }


def _map_observation_payload(payload: dict[str, str], filename: str, observation_role: str) -> dict[str, str]:
    plot = _pick(payload, "plot")
    species = _pick(payload, "species") or _pick(payload, "spp")
    year = _pick(payload, "year")
    month = _pick(payload, "month") or _pick(payload, "moth")
    day = _pick(payload, "day")
    return {
        "observation_role": observation_role,
        "survey_id": _survey_id_from_year(year),
        "date": _date_from_parts(year, month, day),
        "year": year,
        "month": month,
        "day": day,
        "site": _pick(payload, "site") or "BRNV",
        "zone": _pick(payload, "zone") or _zone_from_plot(plot),
        "plot": plot,
        "public_tag_raw": _pick(payload, "tree number") or _pick(payload, "tree_number"),
        "tree_code_raw": _pick(payload, "tree code") or _pick(payload, "tree_code"),
        "old_tag_raw": _pick(payload, "old_tree_number") or _pick(payload, "old_tag"),
        "datasheet_slot_raw": _pick(payload, "trunk number") or _pick(payload, "trunk_number"),
        "taxon_raw": species,
        "dbh_mm_raw": _pick(payload, "dbh (mm)") or _pick(payload, "dbh_mm") or _pick(payload, "dbh_mm"),
        "health_raw": _pick(payload, "health (dead=0)") or _pick(payload, "health"),
        "alive_raw": _pick(payload, "alive:1 or dead:0") or _pick(payload, "alive"),
        "standing_raw": _pick(payload, "standing:1_or_fallen:0") or _pick(payload, "standing"),
        "notes_raw": _pick(payload, "notes"),
    }


def _map_recent_cleaned_payload(payload: dict[str, str], observation_role: str) -> dict[str, str]:
    return {
        "observation_role": observation_role,
        "survey_id": _pick(payload, "survey_id"),
        "date": _pick(payload, "date"),
        "site": _pick(payload, "site") or "BRNV",
        "zone": _pick(payload, "zone"),
        "plot": _pick(payload, "plot"),
        "public_tag_raw": _pick(payload, "tree_number"),
        "tree_code_raw": _pick(payload, "tree_code"),
        "old_tag_raw": _pick(payload, "old_tag"),
        "datasheet_slot_raw": _pick(payload, "trunk_number"),
        "genus_raw": _pick(payload, "genus"),
        "species_raw": _pick(payload, "spp"),
        "dbh_mm_raw": _pick(payload, "dbh_mm"),
        "health_raw": _pick(payload, "health"),
        "alive_raw": _pick(payload, "alive"),
        "standing_raw": _pick(payload, "standing"),
        "notes_raw": _pick(payload, "notes"),
    }


def _extract_tag_changes(
    source: SourceInfo,
    sheet_name: str,
    rows: list[list[str]],
    tag_changes: list[dict[str, object]],
) -> None:
    if not rows:
        return
    header = [_clean_header(item) for item in rows[0]]
    for row_index, row in enumerate(rows[1:], start=2):
        payload = _payload(header, row)
        if not _payload_has_values(payload):
            continue
        old_code = _pick(payload, "old_tree_code")
        new_code = _pick(payload, "new_tree_code")
        old = _parse_tree_code(old_code)
        new = _parse_tree_code(new_code)
        raw_payload = _json(payload)
        tag_changes.append(
            {
                "assertion_id": _hash_id("tag_change", source.source_id, sheet_name, str(row_index), raw_payload),
                "source_id": source.source_id,
                "source_path": source.source_path,
                "source_sheet": sheet_name,
                "source_row": row_index,
                "old_tree_code": old_code,
                "new_tree_code": new_code,
                "old_plot": old.get("plot", ""),
                "old_tag": old.get("tag", ""),
                "old_taxon_hint": old.get("taxon_hint", ""),
                "new_plot": new.get("plot", ""),
                "new_tag": new.get("tag", ""),
                "new_taxon_hint": new.get("taxon_hint", ""),
                "change_type": _pick(payload, "change_type"),
                "year_changed": _pick(payload, "year_changed"),
                "raw_payload_json": raw_payload,
            }
        )


def _add_observation(
    source: SourceInfo,
    sheet_name: str,
    row_index: int,
    mapped: dict[str, str],
    payload: dict[str, str],
    observations: list[dict[str, object]],
    notes: list[dict[str, object]],
) -> None:
    if not _mapped_has_observation(mapped):
        return
    raw_payload = _json(payload)
    role = mapped.get("observation_role", "")
    evidence_id = _hash_id("evidence", source.source_id, sheet_name, str(row_index), role, raw_payload)
    note_text = mapped.get("notes_raw", "")
    note_flags = "|".join(_note_flags(note_text))
    observation = {
        "evidence_id": evidence_id,
        "source_id": source.source_id,
        "source_path": source.source_path,
        "source_sheet": sheet_name,
        "source_row": row_index,
        "source_kind": source.source_kind,
        "evidence_rank": source.evidence_rank,
        "canonical_role": source.canonical_role,
        "observation_role": role,
        "note_flags": note_flags,
        "raw_payload_json": raw_payload,
    }
    for column in EVIDENCE_COLUMNS:
        if column not in observation:
            observation[column] = mapped.get(column, "")
    observations.append(observation)
    if note_text:
        notes.append(
            {
                "note_id": _hash_id("note", evidence_id, "notes_raw", note_text),
                "evidence_id": evidence_id,
                "source_id": source.source_id,
                "source_path": source.source_path,
                "source_sheet": sheet_name,
                "source_row": row_index,
                "note_field": "notes_raw",
                "survey_id": observation.get("survey_id", ""),
                "plot": observation.get("plot", ""),
                "public_tag_raw": observation.get("public_tag_raw", ""),
                "datasheet_slot_raw": observation.get("datasheet_slot_raw", ""),
                "note_text": note_text,
                "note_flags": note_flags,
            }
        )


def _add_sheet_catalog(
    sheets: list[dict[str, object]],
    source: SourceInfo,
    sheet_name: str,
    sheet_role: str,
    rows: list[list[str]],
) -> None:
    header = rows[0] if rows else []
    data_rows = rows[1:] if rows else []
    nonempty_count = sum(1 for row in data_rows if any(_clean_value(value) for value in row))
    sheets.append(
        {
            "source_id": source.source_id,
            "source_path": source.source_path,
            "sheet_name": sheet_name,
            "sheet_role": sheet_role,
            "row_count": nonempty_count,
            "column_count": len(header),
            "headers_json": _json([_clean_value(item) for item in header]),
        }
    )


def _read_csv_rows(path: Path) -> list[list[str]]:
    df = pd.read_csv(path, dtype="string", keep_default_na=False)
    return [list(df.columns)] + df.astype(str).values.tolist()


def _read_xlsx_tables(path: Path) -> dict[str, list[list[str]]]:
    with ZipFile(path) as archive:
        shared = _load_shared_strings(archive)
        result: dict[str, list[list[str]]] = {}
        for sheet_name, target in _xlsx_sheet_targets(archive):
            root = ET.fromstring(archive.read(target))
            rows: list[list[str]] = []
            for row in root.findall(".//main:row", XLSX_NS):
                values: dict[int, str] = {}
                for cell in row.findall("main:c", XLSX_NS):
                    values[_xlsx_col_index(cell.attrib.get("r", "A"))] = _xlsx_cell_value(cell, shared)
                if not values:
                    continue
                max_col = max(values)
                row_values = [values.get(index, "") for index in range(1, max_col + 1)]
                if any(_clean_value(value) for value in row_values):
                    rows.append(row_values)
            result[sheet_name] = rows
        return result


def _load_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall("main:si", XLSX_NS):
        values.append("".join(text.text or "" for text in item.findall(".//main:t", XLSX_NS)))
    return values


def _xlsx_sheet_targets(archive: ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target_by_id = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
    targets: list[tuple[str, str]] = []
    sheets = workbook.find("main:sheets", XLSX_NS)
    if sheets is None:
        return targets
    for sheet in sheets:
        name = sheet.attrib["name"]
        relationship_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        target = target_by_id[relationship_id]
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        if target not in archive.namelist():
            target = f"xl/worksheets/{Path(target).name}"
        targets.append((name, target))
    return targets


def _xlsx_col_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 1
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value


def _xlsx_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return _clean_value("".join(text.text or "" for text in cell.findall(".//main:t", XLSX_NS)))
    value = cell.find("main:v", XLSX_NS)
    if value is None:
        return ""
    raw = value.text or ""
    if cell_type == "s":
        try:
            return _clean_value(shared_strings[int(raw)])
        except (ValueError, IndexError):
            return _clean_value(raw)
    return _clean_value(raw)


def _payload(headers: list[str], row: list[str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    for index, header in enumerate(headers):
        if not header:
            continue
        key = header
        duplicate = 2
        while key in payload:
            key = f"{header}_{duplicate}"
            duplicate += 1
        payload[key] = _clean_value(row[index]) if index < len(row) else ""
    return payload


def _payload_has_values(payload: dict[str, str]) -> bool:
    return any(value for value in payload.values())


def _mapped_has_observation(mapped: dict[str, str]) -> bool:
    return any(
        mapped.get(key, "")
        for key in [
            "public_tag_raw",
            "tree_code_raw",
            "dbh_mm_raw",
            "health_raw",
            "alive_raw",
            "standing_raw",
            "notes_raw",
        ]
    )


def _clean_header(value: object) -> str:
    text = _clean_value(value).lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _clean_value(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "<na>"}:
        return ""
    return text


def _pick(payload: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = payload.get(_clean_header(key), "")
        if value:
            return value
    return ""


def _sheet_role(sheet_name: str) -> str:
    text = sheet_name.lower().strip()
    if "tag_changes" in text:
        return "tag_changes"
    if "metadata" in text or "meta_data" in text:
        return "metadata"
    if "cleaning" in text:
        return "cleaning_log"
    if "plot corners" in text:
        return "plot_metadata"
    if "pivot" in text or "basal area" in text:
        return "summary"
    return "observations"


def _default_observation_role(source: SourceInfo, sheet_name: str) -> str:
    if source.source_kind in {"cleaned_all_years_workbook", "all_years_workbook"}:
        return "derived_cleaned"
    if sheet_name.lower() in {"clean data", "clean_data", "tree_census", "all_years_data"}:
        return "derived_compilation"
    return "observed_current"


def _survey_from_parts(year: str, month: str, day: str, config: Config) -> str:
    parsed = _date_from_parts(year, month, day)
    if parsed:
        try:
            return config.survey_for_date(date.fromisoformat(parsed))
        except Exception:
            pass
    return _survey_id_from_year(year)


def _survey_id_from_year(year: str) -> str:
    year_text = _clean_year(year)
    if not year_text:
        return ""
    return f"June_{year_text}"


def _date_from_parts(year: str, month: str, day: str) -> str:
    year_text = _clean_year(year)
    if not year_text:
        return ""
    month_text = _clean_int(month) or "6"
    day_text = _clean_int(day) or "15"
    try:
        return date(int(year_text), int(month_text), int(day_text)).isoformat()
    except ValueError:
        return ""


def _clean_year(value: str) -> str:
    number = _clean_int(value)
    return number if len(number) == 4 else ""


def _clean_int(value: str) -> str:
    text = _clean_value(value)
    if not text or text.lower() in {"na", "n/a", "not recorded", "not recorded- dead"}:
        return ""
    try:
        number = float(text)
    except ValueError:
        return ""
    if number.is_integer():
        return str(int(number))
    return ""


def _cm_to_mm_raw(value: str) -> str:
    text = _clean_value(value)
    if not text or text.lower().startswith("not recorded"):
        return text
    try:
        return str(round(float(text) * 10, 3)).removesuffix(".0")
    except ValueError:
        return text


def _plot_from_zone_number(zone: str, plot: str) -> str:
    zone_text = _clean_value(zone).upper()
    plot_text = _clean_int(plot) or _clean_value(plot).upper()
    if len(plot_text) >= 2 and plot_text[0] in {"H", "L", "M", "R"}:
        return plot_text
    if zone_text and plot_text:
        return f"{zone_text}{plot_text}"
    return plot_text


def _zone_from_plot(plot: str) -> str:
    text = _clean_value(plot).upper()
    return text[:1] if text[:1] in {"H", "L", "M", "R"} else ""


def _parse_tree_code(value: str) -> dict[str, str]:
    text = _clean_value(value)
    match = re.match(r"(?P<plot>[A-Z]\d+)_(?P<tag>\d+)_(?P<taxon>[A-Za-z]+)", text)
    if not match:
        return {}
    return {
        "plot": match.group("plot"),
        "tag": match.group("tag"),
        "taxon_hint": match.group("taxon"),
    }


def _note_flags(note: str) -> list[str]:
    text = _clean_value(note).lower()
    if not text:
        return []
    flags = []
    for flag, needles in NOTE_KEYWORDS.items():
        if any(needle in text for needle in needles):
            flags.append(flag)
    return flags


def _note_flag_counts(notes: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    if notes.empty or "note_flags" not in notes:
        return counts
    for value in notes["note_flags"].dropna():
        for flag in str(value).split("|"):
            if flag:
                counts[flag] = counts.get(flag, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame:
        return {}
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).items()}


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)


def _hash_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("\0".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame(rows: list[dict[str, object]], columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in columns:
        if column not in frame:
            frame[column] = pd.Series(dtype="string")
    return frame[columns].fillna("")
