"""Experimental LLM transcription for scanned recent census datasheets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib
from typing import Any, Iterable, Literal

import pandas as pd
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .config import Config, load_config


DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_DATASHEET_FORMAT = "auto"
DEFAULT_PORTRAIT_MANIFEST_DIR = Path("output/datasheets_2026/json")
PORTRAIT_FORMAT = "portrait_2026"
LEGACY_FORMAT = "legacy"
ID_RE = re.compile(
    r"^\s*(?P<genus>[A-Za-z]+)\.(?P<species>[A-Za-z]+)\.(?P<tree>\d+)\.(?P<slot>\d+)\s*$"
)
FORBIDDEN_OUTPUT_KEYS = {"dhas", "dhas1", "dhas2", "dhas_1", "dhas_2", "dhas.1", "dhas.2"}
TRANSCRIPTION_COLUMNS = [
    "survey_id",
    "date",
    "site",
    "zone",
    "plot",
    "tree_number",
    "tree_code",
    "trunk_number",
    "genus",
    "spp",
    "dbh_mm",
    "health",
    "alive",
    "old_tag",
    "standing",
    "poison_ivy",
    "notes",
    "section",
    "species_update",
    "identity_source",
    "field_date",
    "source_page",
    "source_row",
    "source_row_label",
    "source_id_text",
    "source_page_title",
    "source_image",
    "source_json",
    "transcription_flags",
    "review_flags",
]
PAGE_METADATA_COLUMNS = [
    "survey_id",
    "date",
    "source_page",
    "source_page_title",
    "plot",
    "field_date",
    "crew",
    "problems_and_info",
    "difficulty",
    "page_flags",
    "observer",
    "recorder",
    "bonus_person",
    "recheck_answers",
    "field_note_feedback",
    "other_handwriting",
    "source_image",
    "source_json",
]
IMPORT_RECENT_COLUMNS = [
    "survey_id",
    "date",
    "site",
    "zone",
    "plot",
    "tree_number",
    "tree_code",
    "trunk_number",
    "genus",
    "spp",
    "dbh_mm",
    "health",
    "alive",
    "old_tag",
    "standing",
    "notes",
    "poison_ivy",
]
EDITABLE_REVIEW_FIELDS = {
    "tree_number",
    "trunk_number",
    "genus",
    "spp",
    "dbh_mm",
    "health",
    "standing",
    "poison_ivy",
    "species_update",
    "notes",
}


class RowTranscription(BaseModel):
    """One non-empty table row transcribed from a scanned datasheet."""

    model_config = ConfigDict(extra="forbid")

    row_label: str = Field(description="Printed leftmost row label, such as 1, 35, or 52.")
    id_text: str = Field(
        description=(
            "Printed id exactly as shown. Expected grammar is GEN.SPP.TREE.STEM, "
            "such as Ace.rub.929.1 or Uni.spp.963.1."
        )
    )
    dbh_mm: float | None = Field(
        default=None,
        description="Handwritten DBH in millimeters. Use null only when the dbh cell is blank or unreadable.",
    )
    health_observed: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Integer health score 0-10. 0 means dead. 1-10 means alive. Use null only when blank/unreadable.",
    )
    standing_observed: bool | None = Field(
        default=None,
        description="stnd column boolean. 1=true/standing, 0=false/not standing, blank=null.",
    )
    poison_ivy_observed: bool | None = Field(
        default=None,
        description="p column boolean for poison ivy. 1 or clear mark/circle=true, 0=false, blank=null.",
    )
    notes: str = Field(default="", description="Handwritten notes exactly as legible; empty string if blank.")
    flags: list[str] = Field(default_factory=list, description="Ambiguity or quality notes for human review.")

    @field_validator("row_label", "id_text", "notes", mode="before")
    @classmethod
    def _clean_string(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()


class PageTranscription(BaseModel):
    """Strict page-level output from the LLM."""

    model_config = ConfigDict(extra="forbid")

    page_title: str = Field(description="Printed page title, such as BRNV.R1 or (BRNV.R1...).")
    plot: str = Field(description="Plot code derived from the printed page title, such as R1.")
    rows: list[RowTranscription]

    @field_validator("page_title", "plot", mode="before")
    @classmethod
    def _clean_string(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()


class _GeminiRowTranscription(BaseModel):
    """Provider-facing schema; strictness is enforced after parsing."""

    row_label: str
    id_text: str = Field(
        description=(
            "Printed id exactly as shown. Expected grammar is GEN.SPP.TREE.STEM, "
            "such as Ace.rub.929.1 or Uni.spp.963.1."
        )
    )
    dbh_mm: float | None = Field(
        default=None,
        description="Handwritten DBH in millimeters. Use null only when the dbh cell is blank or unreadable.",
    )
    health_observed: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Integer health score 0-10. 0 means dead. 1-10 means alive. Use null only when blank/unreadable.",
    )
    standing_observed: bool | None = Field(
        default=None,
        description="stnd column boolean. 1=true/standing, 0=false/not standing, blank=null.",
    )
    poison_ivy_observed: bool | None = Field(
        default=None,
        description="p column boolean for poison ivy. 1 or clear mark/circle=true, 0=false, blank=null.",
    )
    notes: str = Field(default="", description="Handwritten notes exactly as legible; empty string if blank.")
    flags: list[str] = Field(default_factory=list)


class _GeminiPageTranscription(BaseModel):
    """Gemini-compatible schema without unsupported additionalProperties."""

    page_title: str
    plot: str
    rows: list[_GeminiRowTranscription]


class PortraitMainRowTranscription(BaseModel):
    """One printed existing-tree row from the portrait May 2026 datasheet."""

    model_config = ConfigDict(extra="forbid")

    row_label: str
    tag_text: str = ""
    species_text: str = ""
    stem_text: str = ""
    health_observed: int | None = Field(default=None, ge=0, le=10)
    standing_observed: bool | None = None
    poison_ivy_observed: bool | None = None
    species_update: str = ""
    notes: str = ""
    flags: list[str] = Field(default_factory=list)

    @field_validator(
        "row_label",
        "tag_text",
        "species_text",
        "stem_text",
        "species_update",
        "notes",
        mode="before",
    )
    @classmethod
    def _clean_string(cls, value: object) -> str:
        return "" if value is None else str(value).strip()


class PortraitRecruitRowTranscription(BaseModel):
    """One handwritten row from the portrait datasheet's Newly Tracked table."""

    model_config = ConfigDict(extra="forbid")

    row_label: str
    tag_text: str = ""
    species_text: str = ""
    stem_text: str = ""
    dbh_mm: float | None = None
    health_observed: int | None = Field(default=None, ge=0, le=10)
    standing_observed: bool | None = None
    poison_ivy_observed: bool | None = None
    notes: str = ""
    flags: list[str] = Field(default_factory=list)

    @field_validator("row_label", "tag_text", "species_text", "stem_text", "notes", mode="before")
    @classmethod
    def _clean_string(cls, value: object) -> str:
        return "" if value is None else str(value).strip()


class RecheckAnswer(BaseModel):
    question_number: int = Field(ge=1)
    answer: str = ""
    flags: list[str] = Field(default_factory=list)


class FieldNoteFeedback(BaseModel):
    note_number: int = Field(ge=1)
    helpful: bool | None = None
    confusing: bool | None = None
    incorrect: bool | None = None
    handwritten_notes: str = ""
    flags: list[str] = Field(default_factory=list)


class _StrictRecheckAnswer(RecheckAnswer):
    model_config = ConfigDict(extra="forbid")


class _StrictFieldNoteFeedback(FieldNoteFeedback):
    model_config = ConfigDict(extra="forbid")


class PortraitPageTranscription(BaseModel):
    """Strict page-level output for the evolving 2026 portrait datasheets."""

    model_config = ConfigDict(extra="forbid")

    page_title: str
    plot: str
    field_date: str = ""
    crew: list[str] = Field(default_factory=list)
    observer: str = ""
    recorder: str = ""
    bonus_person: str = ""
    recheck_answers: list[_StrictRecheckAnswer] = Field(default_factory=list)
    field_note_feedback: list[_StrictFieldNoteFeedback] = Field(default_factory=list)
    other_handwriting: str = ""
    main_rows: list[PortraitMainRowTranscription] = Field(default_factory=list)
    newly_tracked_rows: list[PortraitRecruitRowTranscription] = Field(default_factory=list)
    problems_and_info: str = ""
    difficulty: Literal["easy", "medium", "hard", "brutal"] | None = None
    flags: list[str] = Field(default_factory=list)

    @field_validator("page_title", "plot", "field_date", "problems_and_info", mode="before")
    @classmethod
    def _clean_string(cls, value: object) -> str:
        return "" if value is None else str(value).strip()


class _GeminiPortraitMainRow(BaseModel):
    row_label: str
    tag_text: str = ""
    species_text: str = ""
    stem_text: str = ""
    health_observed: int | None = Field(default=None, ge=0, le=10)
    standing_observed: bool | None = None
    poison_ivy_observed: bool | None = None
    species_update: str = ""
    notes: str = ""
    flags: list[str] = Field(default_factory=list)


class _GeminiPortraitRecruitRow(BaseModel):
    row_label: str
    tag_text: str = ""
    species_text: str = ""
    stem_text: str = ""
    dbh_mm: float | None = None
    health_observed: int | None = Field(default=None, ge=0, le=10)
    standing_observed: bool | None = None
    poison_ivy_observed: bool | None = None
    notes: str = ""
    flags: list[str] = Field(default_factory=list)


class _GeminiPortraitPage(BaseModel):
    page_title: str
    plot: str
    field_date: str = ""
    crew: list[str] = Field(default_factory=list)
    observer: str = ""
    recorder: str = ""
    bonus_person: str = ""
    recheck_answers: list[RecheckAnswer] = Field(default_factory=list)
    field_note_feedback: list[FieldNoteFeedback] = Field(default_factory=list)
    other_handwriting: str = ""
    main_rows: list[_GeminiPortraitMainRow] = Field(default_factory=list)
    newly_tracked_rows: list[_GeminiPortraitRecruitRow] = Field(default_factory=list)
    problems_and_info: str = ""
    difficulty: Literal["easy", "medium", "hard", "brutal"] | None = None
    flags: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class TranscriptionResult:
    output_dir: Path
    raw_json_dir: Path
    rendered_dir: Path
    crops_dir: Path
    transcription_csv: Path
    import_csv: Path
    review_csv: Path
    page_metadata_csv: Path
    layout_manifest: Path
    run_metadata: Path
    rejected_json: Path
    pages_requested: list[int]
    rows: int
    rejected_pages: int


@dataclass(frozen=True)
class HandwritingContext:
    name: str
    description: str
    examples: tuple[Path, ...]


def transcribe_pdf(
    pdf_path: str | Path,
    *,
    survey_id: str = "October_2025",
    config_dir: str | Path = "config",
    output_dir: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    datasheet_format: str = DEFAULT_DATASHEET_FORMAT,
    datasheet_manifest_dir: str | Path | None = None,
    pages: str | None = "1",
    dpi: int = 300,
    media_resolution: str = "MEDIA_RESOLUTION_HIGH",
    handwriting_profiles: list[str] | None = None,
    handwriting_examples: list[str | Path] | None = None,
    save_cell_crops: bool = False,
    render_only: bool = False,
) -> TranscriptionResult:
    """Render a scanned PDF, transcribe selected pages, and write review/import CSVs."""

    pdf_path = Path(pdf_path).expanduser()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    config = load_config(config_dir)
    survey_date = _survey_start(config, survey_id)
    resolved_format = _resolve_datasheet_format(datasheet_format, survey_id)
    manifest_dir = _resolve_manifest_dir(datasheet_manifest_dir, resolved_format, survey_id)
    manifest_rows = _load_datasheet_manifest_rows(manifest_dir) if manifest_dir else {}
    from .transcription_packet import load_packet_context, validate_packet_page

    packet_context = load_packet_context(pdf_path, manifest_dir, survey_id) if resolved_format == PORTRAIT_FORMAT else {}
    output_dir = Path(output_dir) if output_dir else Path("output/llm_transcription") / pdf_path.stem
    if ((output_dir / "transcription.csv").exists() or (output_dir / "review_decisions.jsonl").exists()
            or any((output_dir / "raw_json").glob("page_*.json"))):
        raise ValueError(f"Run already exists at {output_dir}; use a fresh directory to preserve transcriptions and review edits")
    rendered_dir = output_dir / "pages"
    raw_json_dir = output_dir / "raw_json"
    crops_dir = output_dir / "crops"
    for path in (rendered_dir, raw_json_dir, crops_dir):
        path.mkdir(parents=True, exist_ok=True)

    page_numbers = _parse_page_selection(pages, _pdf_page_count(pdf_path))
    handwriting_contexts = _load_handwriting_contexts(
        config.config_dir,
        handwriting_profiles or [],
        handwriting_examples or [],
    )
    rendered_pages = _render_pages(pdf_path, rendered_dir, page_numbers, dpi)
    page_layouts = []
    for page_number, image_path in rendered_pages.items():
        layout = _write_review_crops(
            image_path,
            crops_dir / f"page_{page_number:03d}",
            save_cell_crops,
            datasheet_format=resolved_format,
        )
        if not layout:
            with Image.open(image_path) as image:
                layout = {"page_image_width": image.width, "page_image_height": image.height, "columns": [], "rows": []}
        layout["source_page"] = page_number
        layout["image_path"] = str(image_path)
        page_layouts.append(layout)

    records: list[dict[str, object]] = []
    page_metadata: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    client = None
    service_error = ""
    if not render_only:
        api_key = _load_gemini_api_key()
        if not api_key:
            raise RuntimeError(
                "No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY in the environment or a .env file."
            )
        from google import genai

        client = genai.Client(api_key=api_key)

    for page_number, image_path in rendered_pages.items():
        if render_only:
            continue
        assert client is not None
        if service_error:
            rejected.append({"source_page": page_number, "image_path": str(image_path),
                             "error": f"Not attempted after service failure: {service_error}"})
            continue
        try:
            page = _transcribe_page(
                client,
                image_path,
                model=model,
                media_resolution=media_resolution,
                handwriting_contexts=handwriting_contexts,
                datasheet_format=resolved_format,
                page_context=packet_context.get(page_number),
                usage_path=output_dir / "usage" / f"page_{page_number:03d}.json",
            )
            raw_json_path = raw_json_dir / f"page_{page_number:03d}.json"
            raw_json_path.write_text(page.model_dump_json(indent=2) + "\n", encoding="utf-8")
            if page_number in packet_context:
                validate_packet_page(page, packet_context[page_number])
        except Exception as exc:  # noqa: BLE001 - persist page-level failures for review.
            if getattr(exc, "code", None) in {401, 402, 403}:
                service_error = f"{type(exc).__name__}: {exc}"
            rejected.append(
                {
                    "source_page": page_number,
                    "image_path": str(image_path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        page_records = _page_to_records(
            page,
            page_number=page_number,
            image_path=image_path,
            raw_json_path=raw_json_path,
            survey_id=survey_id,
            survey_date=survey_date,
            manifest_rows=manifest_rows,
        )
        records.extend(page_records)
        page_metadata.append(
            _page_to_metadata(
                page,
                page_number=page_number,
                image_path=image_path,
                raw_json_path=raw_json_path,
                survey_id=survey_id,
                survey_date=survey_date,
                page_context=packet_context.get(page_number),
            )
        )

    rejected_json = output_dir / "rejected_pages.json"
    rejected_json.write_text(json.dumps(rejected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    layout_manifest = output_dir / "layout_manifest.json"
    layout_manifest.write_text(
        json.dumps({"pages": page_layouts}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    transcription_csv = output_dir / "transcription.csv"
    import_csv = output_dir / "import_recent_format.csv"
    review_csv = output_dir / "review_rows.csv"
    page_metadata_csv = output_dir / "page_metadata.csv"
    _write_csvs(records, transcription_csv, import_csv, review_csv)
    _write_page_metadata(page_metadata, page_metadata_csv)
    run_metadata = output_dir / "run_metadata.json"
    run_metadata.write_text(
        json.dumps(
            {
                "pdf": str(pdf_path),
                "survey_id": survey_id,
                "model": model,
                "datasheet_format": resolved_format,
                "datasheet_manifest_dir": str(manifest_dir) if manifest_dir else "",
                "dpi": dpi,
                "media_resolution": media_resolution,
                "pages": page_numbers,
                "status": "render_only" if render_only else "incomplete" if rejected else "transcribed_pending_review",
                "pages_transcribed": [item["source_page"] for item in page_metadata],
                "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                "packet_context": {str(n): packet_context[n] for n in page_numbers if n in packet_context},
                "portrait_layout": {"newly_tracked_slots": 12, "main_header_same_height": True,
                    "main_column_widths": [0.25, 0.44, 0.52, 0.20, 0.38, 0.28, 0.25, 0.39, 0.52, 0.52, 0.78, 3.32]} if packet_context else {},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if resolved_format == PORTRAIT_FORMAT and records:
        from .review_layout import rebuild_review_layouts

        layout_report = rebuild_review_layouts(output_dir)
        (output_dir / "layout_report.json").write_text(json.dumps(layout_report, indent=2) + "\n")
    return TranscriptionResult(
        output_dir=output_dir,
        raw_json_dir=raw_json_dir,
        rendered_dir=rendered_dir,
        crops_dir=crops_dir,
        transcription_csv=transcription_csv,
        import_csv=import_csv,
        review_csv=review_csv,
        page_metadata_csv=page_metadata_csv,
        layout_manifest=layout_manifest,
        run_metadata=run_metadata,
        rejected_json=rejected_json,
        pages_requested=page_numbers,
        rows=len(records),
        rejected_pages=len(rejected),
    )


def rematerialize_portrait_run(
    source_run_dir: str | Path,
    *,
    output_dir: str | Path,
    datasheet_manifest_dir: str | Path,
    config_dir: str | Path = "config",
    page_additions_path: str | Path | None = None,
) -> TranscriptionResult:
    """Rebuild CSV artifacts from saved portrait JSON without calling the model."""

    source_run_dir = Path(source_run_dir).expanduser()
    output_dir = Path(output_dir).expanduser()
    metadata_path = source_run_dir / "run_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(metadata_path)
    source_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if source_metadata.get("datasheet_format") != PORTRAIT_FORMAT:
        raise ValueError("Only portrait_2026 runs can be rematerialized")

    survey_id = str(source_metadata["survey_id"])
    output_metadata_path = output_dir / "run_metadata.json"
    if page_additions_path is None and output_metadata_path.exists():
        previous_metadata = json.loads(output_metadata_path.read_text(encoding="utf-8"))
        page_additions_path = previous_metadata.get("page_additions_path")
    additions: dict[int, dict[str, Any]] = {}
    if page_additions_path:
        page_additions_path = Path(page_additions_path).resolve()
        document = json.loads(page_additions_path.read_text(encoding="utf-8"))
        if document["survey_id"] != survey_id:
            raise ValueError("Page additions survey does not match the source run")
        for addition in document["pages"]:
            number = int(addition["source_page"])
            if number in additions:
                raise ValueError(f"Duplicate page additions for page {number}")
            additions[number] = addition
    config = load_config(config_dir)
    survey_date = _survey_start(config, survey_id)
    manifest_dir = Path(datasheet_manifest_dir).expanduser()
    manifest_rows = _load_datasheet_manifest_rows(manifest_dir)
    raw_json_dir = source_run_dir / "raw_json"
    raw_json_paths = sorted(raw_json_dir.glob("page_*.json"))
    if not raw_json_paths:
        raise FileNotFoundError(f"No saved page JSON found under {raw_json_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    page_metadata: list[dict[str, object]] = []
    materialized_pages: list[int] = []
    for raw_json_path in raw_json_paths:
        match = re.fullmatch(r"page_(\d+)\.json", raw_json_path.name)
        if match is None:
            continue
        page_number = int(match.group(1))
        page = PortraitPageTranscription.model_validate_json(
            raw_json_path.read_text(encoding="utf-8")
        )
        page_context = source_metadata.get("packet_context", {}).get(str(page_number))
        if page_context:
            from .transcription_packet import validate_packet_page

            path = manifest_dir / f"BRNV_{page_context['plot']}.json"
            if hashlib.sha256(path.read_bytes()).hexdigest() != page_context["manifest_sha256"]:
                raise ValueError(f"Printed manifest changed for {page_context['plot']}")
            validate_packet_page(page, page_context)
        added_labels: set[str] = set()
        if addition := additions.get(page_number):
            if hashlib.sha256(raw_json_path.read_bytes()).hexdigest() != addition["source_json_sha256"]:
                raise ValueError(f"Page additions source mismatch on page {page_number}")
            evidence = page.problems_and_info
            if parent_label := addition.get("source_row_label"):
                parents = [r for r in page.main_rows if r.row_label == parent_label]
                if len(parents) != 1:
                    raise ValueError(f"Page additions parent row mismatch on page {page_number}")
                evidence = parents[0].notes
            if page.plot != addition["plot"] or not addition["source_text"] or addition["source_text"] not in evidence:
                raise ValueError(f"Page additions evidence mismatch on page {page_number}")
            existing_labels = {r.row_label for r in [*page.main_rows, *page.newly_tracked_rows]}
            for item in addition["newly_tracked_rows"]:
                row = PortraitRecruitRowTranscription.model_validate(item)
                if row.row_label in existing_labels or not _portrait_recruit_has_input(row):
                    raise ValueError(f"Invalid or duplicate added row on page {page_number}: {row.row_label}")
                existing_labels.add(row.row_label)
                added_labels.add(row.row_label)
                page.newly_tracked_rows.append(row)
        image_path = source_run_dir / "pages" / f"page_{page_number:03d}.png"
        page_records = _page_to_records(
            page,
            page_number=page_number,
            image_path=image_path,
            raw_json_path=raw_json_path,
            survey_id=survey_id,
            survey_date=survey_date,
            manifest_rows=manifest_rows,
        )
        for record in page_records:
            if record["source_row_label"] in added_labels:
                record["source_json"] = str(page_additions_path)
                record["identity_source"] = "reviewed_page_note"
        records.extend(page_records)
        page_metadata.append(
            _page_to_metadata(
                page,
                page_number=page_number,
                image_path=image_path,
                raw_json_path=raw_json_path,
                survey_id=survey_id,
                survey_date=survey_date,
                page_context=page_context,
            )
        )
        materialized_pages.append(page_number)

    if missing_pages := additions.keys() - set(materialized_pages):
        raise ValueError(f"Page additions reference absent pages: {sorted(missing_pages)}")

    transcription_csv = output_dir / "transcription.csv"
    import_csv = output_dir / "import_recent_format.csv"
    review_csv = output_dir / "review_rows.csv"
    page_metadata_csv = output_dir / "page_metadata.csv"
    _write_csvs(records, transcription_csv, import_csv, review_csv)
    _write_page_metadata(page_metadata, page_metadata_csv)

    layout_manifest = output_dir / "layout_manifest.json"
    source_layout_manifest = source_run_dir / "layout_manifest.json"
    if source_layout_manifest.exists():
        shutil.copy2(source_layout_manifest, layout_manifest)
    else:
        layout_manifest.write_text('{"pages": []}\n', encoding="utf-8")

    rejected_json = output_dir / "rejected_pages.json"
    source_rejected_json = source_run_dir / "rejected_pages.json"
    if source_rejected_json.exists():
        shutil.copy2(source_rejected_json, rejected_json)
        rejected = json.loads(rejected_json.read_text(encoding="utf-8"))
    else:
        rejected = []
        rejected_json.write_text("[]\n", encoding="utf-8")

    run_metadata = output_dir / "run_metadata.json"
    run_metadata.write_text(
        json.dumps(
            {
                **source_metadata,
                "datasheet_manifest_dir": str(manifest_dir),
                "materialized_pages": materialized_pages,
                "rematerialized_from": str(source_run_dir),
                "page_additions_path": str(page_additions_path) if page_additions_path else None,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    requested_pages = [int(value) for value in source_metadata.get("pages", materialized_pages)]
    return TranscriptionResult(
        output_dir=output_dir,
        raw_json_dir=raw_json_dir,
        rendered_dir=source_run_dir / "pages",
        crops_dir=source_run_dir / "crops",
        transcription_csv=transcription_csv,
        import_csv=import_csv,
        review_csv=review_csv,
        page_metadata_csv=page_metadata_csv,
        layout_manifest=layout_manifest,
        run_metadata=run_metadata,
        rejected_json=rejected_json,
        pages_requested=requested_pages,
        rows=len(records),
        rejected_pages=len(rejected),
    )


def add_transcribe_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "transcribe-pdf",
        help="Experimentally transcribe scanned recent datasheets with Gemini",
    )
    parser.add_argument("pdf")
    parser.add_argument("--survey-id", default="October_2025")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--datasheet-format",
        default=DEFAULT_DATASHEET_FORMAT,
        choices=[DEFAULT_DATASHEET_FORMAT, LEGACY_FORMAT, PORTRAIT_FORMAT],
        help="Datasheet layout. auto selects portrait_2026 for May/October 2026 and legacy otherwise.",
    )
    parser.add_argument(
        "--datasheet-manifest-dir",
        default=None,
        help="Directory of per-plot JSON payloads used to print portrait datasheets.",
    )
    parser.add_argument(
        "--pages",
        default="1",
        help="Pages to process, e.g. 1, 1-3, 1,10,58, or all. Defaults to page 1.",
    )
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument(
        "--media-resolution",
        default="MEDIA_RESOLUTION_HIGH",
        choices=[
            "MEDIA_RESOLUTION_UNSPECIFIED",
            "MEDIA_RESOLUTION_LOW",
            "MEDIA_RESOLUTION_MEDIUM",
            "MEDIA_RESOLUTION_HIGH",
        ],
    )
    parser.add_argument("--save-cell-crops", action="store_true")
    parser.add_argument(
        "--handwriting-profile",
        action="append",
        default=[],
        help=(
            "Named handwriting calibration profile from config/handwriting_profiles.toml. "
            "Repeat to include several profiles."
        ),
    )
    parser.add_argument(
        "--handwriting-example",
        action="append",
        default=[],
        help=(
            "Optional calibration image to include before each target page. "
            "Repeat for several examples, such as Juan 1/7 crops."
        ),
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Render pages and review crops without calling Gemini.",
    )

    rematerialize = subparsers.add_parser(
        "rematerialize-llm-run",
        help="Rebuild portrait transcription CSVs from saved raw JSON and a manifest",
    )
    rematerialize.add_argument("source_run_dir")
    rematerialize.add_argument("--out-dir", required=True)
    rematerialize.add_argument("--datasheet-manifest-dir", required=True)
    rematerialize.add_argument("--config-dir", default="config")
    rematerialize.add_argument("--page-additions", default=None, help="Reviewed, source-guarded rows omitted from the model extraction")

    layout = subparsers.add_parser(
        "rebuild-review-layout",
        help="Rebuild portrait review overlays without changing extracted data or decisions",
    )
    layout.add_argument("run_dir")
    layout.add_argument("--overrides", default=None)

    review = subparsers.add_parser(
        "materialize-llm-review",
        help="Apply append-only LLM review decisions and write reviewed import CSVs",
    )
    review.add_argument(
        "--selection",
        default="docs/oct_2025_reviewed_run_manifest.json",
        help="JSON manifest with a dirs array of reviewed transcription run directories.",
    )
    review.add_argument("--out-dir", default="output/llm_transcription/oct_2025_reviewed")


def run_transcribe_command(args: argparse.Namespace) -> None:
    result = transcribe_pdf(
        args.pdf,
        survey_id=args.survey_id,
        config_dir=args.config_dir,
        output_dir=args.out_dir,
        model=args.model,
        datasheet_format=args.datasheet_format,
        datasheet_manifest_dir=args.datasheet_manifest_dir,
        pages=args.pages,
        dpi=args.dpi,
        media_resolution=args.media_resolution,
        handwriting_profiles=args.handwriting_profile,
        handwriting_examples=args.handwriting_example,
        save_cell_crops=args.save_cell_crops,
        render_only=args.render_only,
    )
    print(
        json.dumps(
            {
                "rows": result.rows,
                "rejected_pages": result.rejected_pages,
                "pages": result.pages_requested,
                "output_dir": str(result.output_dir),
                "transcription_csv": str(result.transcription_csv),
                "import_csv": str(result.import_csv),
                "review_csv": str(result.review_csv),
                "page_metadata_csv": str(result.page_metadata_csv),
                "layout_manifest": str(result.layout_manifest),
                "run_metadata": str(result.run_metadata),
                "rejected_json": str(result.rejected_json),
            },
            sort_keys=True,
        )
    )
    if result.rejected_pages:
        raise SystemExit(1)


def run_materialize_review_command(args: argparse.Namespace) -> None:
    summary = materialize_llm_review(args.selection, args.out_dir)
    print(json.dumps(summary, sort_keys=True))


def run_rematerialize_command(args: argparse.Namespace) -> None:
    result = rematerialize_portrait_run(
        args.source_run_dir,
        output_dir=args.out_dir,
        datasheet_manifest_dir=args.datasheet_manifest_dir,
        config_dir=args.config_dir,
        page_additions_path=args.page_additions,
    )
    print(
        json.dumps(
            {
                "rows": result.rows,
                "rejected_pages": result.rejected_pages,
                "pages": result.pages_requested,
                "output_dir": str(result.output_dir),
                "transcription_csv": str(result.transcription_csv),
                "review_csv": str(result.review_csv),
            },
            sort_keys=True,
        )
    )


def materialize_llm_review(
    selection: str | Path,
    out_dir: str | Path,
) -> dict[str, object]:
    selection_path = Path(selection).expanduser()
    manifest = json.loads(selection_path.read_text(encoding="utf-8"))
    run_dirs = [_resolve_run_dir(value) for value in manifest.get("dirs", [])]
    if not run_dirs:
        raise ValueError(f"No run dirs found in {selection_path}")

    transcription_frames = []
    page_metadata_frames = []
    decision_records: list[dict[str, object]] = []
    missing_decision_logs = 0
    rejected_pages: list[dict[str, object]] = []

    for run_dir in run_dirs:
        transcription_path = run_dir / "transcription.csv"
        if not transcription_path.exists():
            raise FileNotFoundError(transcription_path)
        frame = pd.read_csv(transcription_path, dtype="string", keep_default_na=False)
        frame["source_run_dir"] = str(run_dir)
        transcription_frames.append(frame)
        metadata_path = run_dir / "page_metadata.csv"
        if metadata_path.exists():
            metadata_frame = pd.read_csv(metadata_path, dtype="string", keep_default_na=False)
            metadata_frame["source_run_dir"] = str(run_dir)
            page_metadata_frames.append(metadata_frame)

        decisions_path = run_dir / "review_decisions.jsonl"
        if decisions_path.exists():
            for line_number, line in enumerate(decisions_path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                record["_source_run_dir"] = str(run_dir)
                record["_decision_line"] = line_number
                decision_records.append(record)
        else:
            missing_decision_logs += 1

        rejected_path = run_dir / "rejected_pages.json"
        if rejected_path.exists():
            rejected = json.loads(rejected_path.read_text(encoding="utf-8"))
            for item in rejected:
                if item:
                    rejected_pages.append({"source_run_dir": str(run_dir), **item})

    transcription = pd.concat(transcription_frames, ignore_index=True)
    for column in TRANSCRIPTION_COLUMNS:
        if column not in transcription:
            transcription[column] = ""
    transcription["_review_key"] = _review_key(transcription)
    key_counts = transcription["_review_key"].value_counts()
    duplicate_keys = key_counts[key_counts > 1]
    if not duplicate_keys.empty:
        examples = duplicate_keys.head(10).index.astype(str).tolist()
        raise ValueError(f"Review keys must identify exactly one transcription row; duplicate keys: {examples}")

    latest_edits, skipped_decisions = _latest_review_edits(decision_records)
    edits_applied = 0
    unmatched_decisions = []
    edited_rows: set[int] = set()
    transcription_by_key = {key: index for index, key in transcription["_review_key"].items()}
    for (key, field), decision in latest_edits.items():
        index = transcription_by_key.get(key)
        if index is None:
            unmatched_decisions.append(decision)
            continue
        transcription.at[index, field] = str(decision.get("chosen_value", ""))
        edits_applied += 1
        edited_rows.add(int(index))

    if unmatched_decisions:
        examples = [
            {
                "key": item.get("key", ""),
                "chosen_field": item.get("chosen_field", ""),
                "source_run_dir": item.get("_source_run_dir", ""),
            }
            for item in unmatched_decisions[:10]
        ]
        raise ValueError(f"Review decisions did not match transcription rows: {examples}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    reviewed_transcription = transcription.drop(columns=["_review_key"])
    transcription_output = out_path / "transcription_reviewed.csv"
    import_output = out_path / "import_recent_format_reviewed.csv"
    summary_output = out_path / "review_application_summary.json"
    rejected_output = out_path / "rejected_pages_reviewed_runs.json"

    reviewed_transcription.to_csv(transcription_output, index=False, columns=[*TRANSCRIPTION_COLUMNS, "source_run_dir"])
    import_frame = _reviewed_transcription_to_import(reviewed_transcription)
    import_frame.to_csv(import_output, index=False, columns=IMPORT_RECENT_COLUMNS)
    metadata_output = out_path / "page_metadata.csv"
    metadata_frame = (pd.concat(page_metadata_frames, ignore_index=True) if page_metadata_frames
                      else pd.DataFrame(columns=[*PAGE_METADATA_COLUMNS, "source_run_dir"]))
    metadata_frame.reindex(columns=[*PAGE_METADATA_COLUMNS, "source_run_dir"], fill_value="").to_csv(metadata_output, index=False)
    rejected_output.write_text(json.dumps(rejected_pages, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "selection": str(selection_path),
        "selection_name": manifest.get("name", ""),
        "run_dirs": len(run_dirs),
        "rows_loaded": int(len(transcription)),
        "page_metadata_rows": int(len(metadata_frame)),
        "page_metadata_csv": str(metadata_output),
        "decisions_loaded": len(decision_records),
        "edit_decisions_loaded": sum(1 for item in decision_records if item.get("action") == "edit"),
        "edits_deduped": len(latest_edits),
        "edits_applied": edits_applied,
        "edited_rows": len(edited_rows),
        "unmatched_decisions": len(unmatched_decisions),
        "skipped_non_edit_decisions": skipped_decisions,
        "missing_decision_logs": missing_decision_logs,
        "rejected_pages": len(rejected_pages),
        "outputs": {
            "transcription": str(transcription_output),
            "import": str(import_output),
            "summary": str(summary_output),
            "rejected_pages": str(rejected_output),
        },
    }
    summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _resolve_run_dir(value: object) -> Path:
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _review_key(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["source_page"].astype(str)
        + ":"
        + frame["source_row"].astype(str)
        + ":"
        + frame["source_id_text"].astype(str)
    )


def _latest_review_edits(
    decision_records: list[dict[str, object]],
) -> tuple[dict[tuple[str, str], dict[str, object]], int]:
    latest: dict[tuple[str, str], dict[str, object]] = {}
    skipped = 0
    for record in decision_records:
        if record.get("action") != "edit":
            skipped += 1
            continue
        key = str(record.get("key", ""))
        field = str(record.get("chosen_field", ""))
        if not key or field not in EDITABLE_REVIEW_FIELDS:
            skipped += 1
            continue
        current = latest.get((key, field))
        if current is None or str(record.get("decided_at", "")) >= str(current.get("decided_at", "")):
            latest[(key, field)] = record
    return latest, skipped


def _reviewed_transcription_to_import(transcription: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    for column in IMPORT_RECENT_COLUMNS:
        if column in transcription:
            out[column] = transcription[column]
        else:
            out[column] = ""
    if "alive" not in out:
        out["alive"] = ""
    if "old_tag" not in out:
        out["old_tag"] = ""
    if "species_update" in transcription:
        out["notes"] = [
            _notes_with_species_update(notes, update)
            for notes, update in zip(out["notes"], transcription["species_update"])
        ]
    return out[IMPORT_RECENT_COLUMNS]


def parse_tree_id(id_text: str) -> dict[str, str]:
    match = ID_RE.match(id_text)
    if not match:
        raise ValueError(f"Cannot parse tree id {id_text!r}")
    return {
        "genus": match.group("genus"),
        "spp": match.group("species"),
        "tree_number": match.group("tree"),
        "trunk_number": match.group("slot"),
    }


def _resolve_datasheet_format(value: str, survey_id: str) -> str:
    normalized = str(value or DEFAULT_DATASHEET_FORMAT).strip().lower()
    if normalized == DEFAULT_DATASHEET_FORMAT:
        return PORTRAIT_FORMAT if survey_id.lower() in {"may_2026", "spring_2026", "october_2026"} else LEGACY_FORMAT
    if normalized not in {LEGACY_FORMAT, PORTRAIT_FORMAT}:
        raise ValueError(f"Unknown datasheet format {value!r}")
    return normalized


def _resolve_manifest_dir(value: str | Path | None, datasheet_format: str, survey_id: str = "") -> Path | None:
    if value is not None:
        path = Path(value).expanduser()
        if not path.exists():
            raise FileNotFoundError(path)
        return path
    if survey_id == "October_2026":
        raise ValueError("October_2026 requires --datasheet-manifest-dir pointing to the exact printed packet")
    if datasheet_format == PORTRAIT_FORMAT and DEFAULT_PORTRAIT_MANIFEST_DIR.exists():
        return DEFAULT_PORTRAIT_MANIFEST_DIR
    return None


def _load_datasheet_manifest_rows(manifest_dir: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for manifest_path in sorted(manifest_dir.glob("*.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        plot = _clean_plot(payload.get("plot", ""))
        for page_rows in ([payload["rows"]] if "rows" in payload else payload.get("row_pages", [])):
            for row in page_rows:
                row_label = _clean_row_label(row.get("row", ""))
                key = (plot, row_label)
                if not plot or not row_label:
                    raise ValueError(f"Manifest row missing plot/row in {manifest_path}")
                if key in rows:
                    raise ValueError(f"Duplicate datasheet manifest row {plot}/{row_label}")
                rows[key] = {
                    "tag": _clean_tag_text(row.get("tag", "")),
                    "species": str(row.get("spp", "") or "").strip(),
                    "stem": _clean_stem_text(row.get("stem", "")),
                    "manifest_path": str(manifest_path),
                }
    return rows


def _clean_row_label(value: object) -> str:
    text = str(value or "").strip()
    match = re.search(r"\d+", text)
    return str(int(match.group())) if match else text.upper()


def _clean_tag_text(value: object) -> str:
    text = str(value or "").strip()
    match = re.search(r"\d+", text)
    return str(int(match.group())) if match else ""


def _clean_stem_text(value: object) -> str:
    text = str(value or "").strip()
    match = re.match(r"\s*(\d+)", text)
    return str(int(match.group(1))) if match else ""


def _compact_taxon(value: object) -> str:
    return re.sub(r"[^A-Za-z]", "", str(value or "")).upper()


def _split_compact_taxon(value: object) -> tuple[str, str]:
    text = str(value or "").strip()
    separated = [part for part in re.split(r"[.\s/_-]+", text) if part]
    if len(separated) >= 2:
        return separated[0], separated[1]
    compact = _compact_taxon(text)
    if len(compact) >= 6:
        return compact[:3].title(), compact[3:6].lower()
    if compact:
        return compact[:3].title(), ""
    return "", ""


def _normalize_species_update(value: str) -> str:
    text = value.strip()
    return "" if text.casefold() in {"na", "n/a"} else text


def _notes_with_species_update(notes: str, species_update: str) -> str:
    notes = notes.strip()
    species_update = _normalize_species_update(species_update)
    if not species_update:
        return notes
    update_note = f"species update: {species_update}"
    return f"{notes}; {update_note}" if notes else update_note


def _portrait_recruit_has_input(row: PortraitRecruitRowTranscription) -> bool:
    return any(
        value not in (None, "")
        for value in [
            row.tag_text,
            row.species_text,
            row.stem_text,
            row.dbh_mm,
            row.health_observed,
            row.standing_observed,
            row.poison_ivy_observed,
            row.notes,
        ]
    )


def _transcribe_page(
    client: Any,
    image_path: Path,
    *,
    model: str,
    media_resolution: str,
    handwriting_contexts: list[HandwritingContext],
    datasheet_format: str,
    page_context: dict[str, Any] | None = None,
    usage_path: Path | None = None,
) -> PageTranscription | PortraitPageTranscription:
    from google.genai import types

    if datasheet_format == PORTRAIT_FORMAT:
        prompt = _portrait_page_prompt()
        response_schema: type[BaseModel] = _GeminiPortraitPage
        result_schema: type[BaseModel] = PortraitPageTranscription
    else:
        prompt = _page_prompt()
        response_schema = _GeminiPageTranscription
        result_schema = PageTranscription

    if page_context:
        prompt += "\n\nVerified PRINTED page context (not observations). Include exactly these main row labels and recheck questions. " + json.dumps(page_context)

    config_kwargs: dict[str, object] = {
        "response_mime_type": "application/json",
        "response_schema": response_schema,
        "media_resolution": getattr(types.MediaResolution, media_resolution),
    }
    if _uses_latest_gemini_config(model):
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.HIGH,
        )
    else:
        config_kwargs["temperature"] = 0

    response = client.models.generate_content(
        model=model,
        contents=_gemini_contents(types, image_path, handwriting_contexts, prompt),
        config=types.GenerateContentConfig(**config_kwargs),
    )
    if usage_path is not None and response.usage_metadata is not None:
        usage_path.parent.mkdir(parents=True, exist_ok=True)
        usage_path.write_text(json.dumps({
            "requested_model": model,
            "model_version": response.model_version,
            "usage": response.usage_metadata.model_dump(mode="json", exclude_none=True),
        }, indent=2) + "\n", encoding="utf-8")
    raw = response.text or ""
    if raw:
        data = _loads_strict_json(raw)
        if _contains_forbidden_key(data):
            raise ValueError("LLM output included forbidden dhas-related keys")
        return result_schema.model_validate(data)  # type: ignore[return-value]
    parsed = getattr(response, "parsed", None)
    if parsed is None:
        raise ValueError("Gemini response had neither text nor parsed structured output")
    if isinstance(parsed, result_schema):
        return parsed  # type: ignore[return-value]
    if isinstance(parsed, BaseModel):
        parsed = parsed.model_dump()
    return result_schema.model_validate(parsed)  # type: ignore[return-value]


def _gemini_contents(
    types: Any,
    image_path: Path,
    handwriting_contexts: list[HandwritingContext],
    prompt: str,
) -> list[Any]:
    contents: list[Any] = [prompt]
    if handwriting_contexts:
        contents.append("Handwriting calibration examples follow. Do not transcribe them as census rows.")
        for context in handwriting_contexts:
            contents.append(f"Handwriting profile: {context.name}\n{context.description.strip()}")
            for example_path in context.examples:
                contents.append(
                    types.Part.from_bytes(data=example_path.read_bytes(), mime_type=_image_mime_type(example_path))
                )
        contents.append("Now transcribe the target datasheet page below.")
    contents.append(types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png"))
    return contents


def _uses_latest_gemini_config(model: str) -> bool:
    match = re.search(r"gemini-(\d+)\.(\d+)", model)
    if not match:
        return False
    return (int(match.group(1)), int(match.group(2))) >= (3, 6)


def _page_prompt() -> str:
    return (
        "You are decoding a scanned forest census datasheet into a strict data schema. "
        "This is not free-form OCR: every cell must be interpreted according to the known column domains below. "
        "\n\n"
        "Columns to transcribe:\n"
        "- row_label: printed row number at far left. Copy exactly.\n"
        "- id_text: printed tree id. Copy exactly from the id column; never infer from row order.\n"
        "  Expected grammar: GEN.SPP.TREE.STEM, e.g. Ace.rub.929.1, Pin.tae.954.1, Uni.spp.963.1.\n"
        "  GEN and SPP are alphabetic abbreviations; TREE and STEM are digits. Do not include spaces.\n"
        "  Do not read handwritten notes as part of id_text, even if a note contains text like Pru.ser.1.\n"
        "  If the printed id is partly illegible, copy the visible text as best as possible and add a flag.\n"
        "- dbh_mm: handwritten tree diameter in millimeters. Valid output is a number or null if blank/unreadable.\n"
        "- health_observed: handwritten health score. Valid values are integers 0 through 10 only. "
        "0 means dead; 1 through 10 mean alive. Use null if blank/unreadable.\n"
        "- standing_observed: stnd column. Valid values are true, false, or null. "
        "Handwritten 1 means true/standing; handwritten 0 means false/not standing; blank means null.\n"
        "  Do not move a 0 or 1 from the stnd column into health. If health is blank and stnd contains 0, output "
        "health_observed=null and standing_observed=false.\n"
        "- poison_ivy_observed: p column. Valid values are true, false, or null. "
        "Handwritten 1 or a clear mark/circle/check in the p cell means true/present; handwritten 0 means false/absent; "
        "blank means null. Do not borrow marks from adjacent rows.\n"
        "- notes: handwritten notes in the notes column only. Preserve legible wording; use empty string if blank.\n"
        "- flags: short review notes for ambiguous handwriting, overwritten/crossed-out cells, or values you are not sure about.\n"
        "\n"
        "Important constraints:\n"
        "- Include only rows with a printed id or a handwritten value/note.\n"
        "- Do not transcribe dhas.1 or dhas.2. They are field-worker context only. "
        "Do not include any dhas fields in the JSON.\n"
        "- Do not use the handwritten page date for import.\n"
        "- If a note starts on a row and visually dangles downward into the row below or the right margin, "
        "associate that contiguous note with its parent row where it begins, not merely the nearest vertical row.\n"
        "- For typed numeric/boolean columns, horizontal slashes, diagonal slashes, dashes, cross-outs, or strike marks "
        "are missing values, not data values. For example, health is only 0-10 or null; stnd and p are only true/false/null. "
        "If a mark is not a valid value for that column, output null and add a flag if it may need review.\n"
        "- Treat faint pencil marks that appear erased as missing values. Output null for the affected typed cell and add a "
        "flag mentioning erased/faint pencil.\n"
        "- If a value is crossed out and a replacement value is written nearby in the same cell or clearly associated with "
        "that cell, use the replacement value and add a flag noting the crossed-out original. If there is no clear "
        "replacement, output null and flag it as crossed out.\n"
        "- Slashes or dashes may be prose punctuation inside notes; preserve them only when they are part of a handwritten note.\n"
        "- Prefer null plus a flag over guessing when a cell is genuinely illegible.\n"
        "- Use neighboring rows and the printed grid as context to distinguish blanks from 0/1 marks.\n"
        "- dhas.1 and dhas.2 may explain why a field worker expected a tree to be dead or alive, but do not infer "
        "current health or standing from dhas values. Current values must come from the current dbh, health, stnd, "
        "and p cells only."
    )


def _portrait_page_prompt() -> str:
    return (
        "You are transcribing one scanned page from a 2026 portrait forest census datasheet into a strict "
        "schema. Preserve the distinction between printed historical context and handwritten current-survey data.\n\n"
        "Page-level fields:\n"
        "- page_title and plot: copy the printed BRNV plot heading, such as BRNV R1 and R1.\n"
        "- field_date: copy the handwritten date exactly when present; otherwise use an empty string.\n"
        "- crew: copy each non-empty handwritten crew name.\n"
        "- observer, recorder, bonus_person: copy names under these roles when printed, empty otherwise.\n"
        "- problems_and_info: transcribe handwriting in that plot-level section exactly; empty string when blank.\n"
        "- difficulty: easy, medium, hard, or brutal only when its current Difficulty checkbox is clearly marked; otherwise null. "
        "Never copy Avg. difficulty from the header: that is historical.\n"
        "- recheck_answers: include each printed Q number on this page, with only the handwritten answer (empty if unanswered). "
        "Never copy the printed question or its supporting context as an answer.\n"
        "- field_note_feedback: use the note_number from supplied printed context for each visible Field Notes bullet. "
        "Helpful, Confusing and Incorrect are independent, not mutually exclusive: true when checked, null when blank. "
        "Preserve handwritten annotations as handwritten_notes. Do not copy printed notes as current data.\n"
        "- other_handwriting: preserve unassigned margin or other handwriting, with its location. Do not discard tagged prose. "
        "Do not create extra stem observations from recheck answers or page-level prose.\n\n"
        "Main table (existing trees):\n"
        "- Include every printed Main row on the page, even when all current-survey cells are blank. A blank existing "
        "row is evidence that the tree was not found or not reported.\n"
        "- Copy row_label, tag_text, species_text, and stem_text from their printed columns. stem_text may look like "
        "1, 1/2, or 2/2.\n"
        "- * and + after printed tags are pointers to questions/field notes, not digits, new tags, or current observations.\n"
        "- Transcribe only handwritten current values into health_observed, standing_observed, poison_ivy_observed, "
        "species_update, and notes.\n"
        "- health_observed is an integer 0-10 or null. 0 means dead; 1-10 means alive.\n"
        "- standing_observed and poison_ivy_observed are true for a clear check/mark, false only for an explicit "
        "handwritten 0 or written 'no', and null when blank or unclear.\n"
        "- species_update and notes are separate handwritten columns. Do not move one into the other.\n"
        "- NA or N/A in species_update means no species change: return an empty string. "
        "Preserve meaningful prose in notes.\n"
        "- CRITICAL: dbh, hsp.1, and hsp.2 in Main are printed historical/reference context. Do not transcribe any of "
        "those values as current measurements, and do not emit fields for them.\n\n"
        "Newly Tracked table:\n"
        "- Include every slot containing handwriting, N1-N12 on the October sheets (N1-N6 on older sheets). "
        "Keep the printed slot label even when earlier slots are blank. Do not assume these are biologically new plants.\n"
        "- tag_text, species_text, stem_text, dbh_mm, health_observed, standing_observed, poison_ivy_observed, and notes "
        "are all current-survey handwritten inputs. DBH is in millimeters.\n"
        "- A newly tracked row can be incomplete; preserve what is present and flag missing or ambiguous identity.\n\n"
        "General constraints:\n"
        "- Do not transcribe the printed Existing tags list as observations.\n"
        "- Do not infer current values from printed dbh, hsp.1, hsp.2, tree counts, or living counts.\n"
        "- Treat slashes, dashes, cross-outs, and erased marks in typed numeric/boolean cells as null unless a clear "
        "replacement is written nearby. Add a concise flag for ambiguity, overwrite, or cross-out.\n"
        "- Handwritten NA or N/A means missing, not zero, in numeric/boolean inputs. Blank standing does not imply fallen.\n"
        "- Prefer null plus a flag over guessing. Use neighboring grid rows only to maintain alignment, never to borrow values."
    )


def _page_to_records(
    page: PageTranscription | PortraitPageTranscription,
    *,
    page_number: int,
    image_path: Path,
    raw_json_path: Path,
    survey_id: str,
    survey_date: date,
    manifest_rows: dict[tuple[str, str], dict[str, str]] | None = None,
) -> list[dict[str, object]]:
    if isinstance(page, PortraitPageTranscription):
        return _portrait_page_to_records(
            page,
            page_number=page_number,
            image_path=image_path,
            raw_json_path=raw_json_path,
            survey_id=survey_id,
            survey_date=survey_date,
            manifest_rows=manifest_rows or {},
        )

    records = []
    plot = _clean_plot(_plot_from_title(page.page_title) or page.plot)
    zone = plot[:1]
    for row_index, row in enumerate(page.rows, start=1):
        if not row.id_text and not _row_has_observation(row):
            continue
        try:
            parsed = parse_tree_id(row.id_text)
            parse_error = ""
        except ValueError as exc:
            parsed = {"genus": "", "spp": "", "tree_number": "", "trunk_number": ""}
            parse_error = str(exc)
        flags = list(row.flags)
        if parse_error:
            flags.append(parse_error)
        review_flags = _review_flags(row, parse_error=parse_error)
        records.append(
            {
                "survey_id": survey_id,
                "date": survey_date.isoformat(),
                "site": "BRNV",
                "zone": zone,
                "plot": plot,
                "tree_number": parsed["tree_number"],
                "tree_code": f"{plot}_{parsed['tree_number']}_{parsed['genus']}" if parsed["tree_number"] else "",
                "trunk_number": parsed["trunk_number"],
                "genus": parsed["genus"],
                "spp": parsed["spp"],
                "dbh_mm": row.dbh_mm,
                "health": row.health_observed,
                "alive": "",
                "old_tag": "",
                "standing": _bool_to_recent_value(row.standing_observed),
                "poison_ivy": _bool_to_recent_value(row.poison_ivy_observed),
                "notes": row.notes,
                "section": "legacy",
                "species_update": "",
                "identity_source": "printed_id",
                "field_date": "",
                "source_page": page_number,
                "source_row": row_index,
                "source_row_label": row.row_label,
                "source_id_text": row.id_text,
                "source_page_title": page.page_title,
                "source_image": str(image_path),
                "source_json": str(raw_json_path),
                "transcription_flags": "; ".join(flags),
                "review_flags": "; ".join(review_flags),
            }
        )
    return records


def _portrait_page_to_records(
    page: PortraitPageTranscription,
    *,
    page_number: int,
    image_path: Path,
    raw_json_path: Path,
    survey_id: str,
    survey_date: date,
    manifest_rows: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    plot = _clean_plot(_plot_from_title(page.page_title) or page.plot)

    for row in page.main_rows:
        is_handwritten_extension = (
            (plot, _clean_row_label(row.row_label)) not in manifest_rows
            and any(_clean_flag(flag) == "handwritten_row_added" for flag in row.flags)
        )
        if is_handwritten_extension:
            identity, identity_flags, review_identity_flags = _portrait_recruit_identity(row)
            records.append(
                _portrait_record(
                    page=page,
                    row=row,
                    identity=identity,
                    section="newly_tracked",
                    dbh_mm=None,
                    notes=row.notes,
                    species_update=row.species_update,
                    identity_flags=identity_flags,
                    extra_review_flags=[
                        *review_identity_flags,
                        "newly_tracked_row",
                        "handwritten_main_extension",
                    ],
                    page_number=page_number,
                    image_path=image_path,
                    raw_json_path=raw_json_path,
                    survey_id=survey_id,
                    survey_date=survey_date,
                    source_row=len(records) + 1,
                )
            )
            continue
        identity, identity_flags, review_identity_flags = _portrait_main_identity(
            plot,
            row,
            manifest_rows,
        )
        records.append(
            _portrait_record(
                page=page,
                row=row,
                identity=identity,
                section="main",
                dbh_mm=None,
                notes=row.notes,
                species_update=row.species_update,
                identity_flags=identity_flags,
                extra_review_flags=review_identity_flags,
                page_number=page_number,
                image_path=image_path,
                raw_json_path=raw_json_path,
                survey_id=survey_id,
                survey_date=survey_date,
                source_row=len(records) + 1,
            )
        )

    for row in page.newly_tracked_rows:
        if not _portrait_recruit_has_input(row):
            continue
        identity, identity_flags, review_identity_flags = _portrait_recruit_identity(row)
        records.append(
            _portrait_record(
                page=page,
                row=row,
                identity=identity,
                section="newly_tracked",
                dbh_mm=row.dbh_mm,
                notes=row.notes,
                species_update="",
                identity_flags=identity_flags,
                extra_review_flags=[*review_identity_flags, "newly_tracked_row"],
                page_number=page_number,
                image_path=image_path,
                raw_json_path=raw_json_path,
                survey_id=survey_id,
                survey_date=survey_date,
                source_row=len(records) + 1,
            )
        )
    return records


def _portrait_record(
    *,
    page: PortraitPageTranscription,
    row: PortraitMainRowTranscription | PortraitRecruitRowTranscription,
    identity: dict[str, str],
    section: str,
    dbh_mm: float | None,
    notes: str,
    species_update: str,
    identity_flags: list[str],
    extra_review_flags: list[str],
    page_number: int,
    image_path: Path,
    raw_json_path: Path,
    survey_id: str,
    survey_date: date,
    source_row: int,
) -> dict[str, object]:
    species_update = _normalize_species_update(species_update)
    source_id_text = "|".join([row.tag_text, row.species_text, row.stem_text])
    parse_error = "" if identity["tree_number"] and identity["trunk_number"] else "Incomplete portrait row identity"
    review_row = RowTranscription(
        row_label=row.row_label,
        id_text=source_id_text,
        dbh_mm=dbh_mm,
        health_observed=row.health_observed,
        standing_observed=row.standing_observed,
        poison_ivy_observed=row.poison_ivy_observed,
        notes=notes,
        flags=row.flags,
    )
    review_flags = _review_flags(review_row, parse_error=parse_error)
    review_flags.extend(extra_review_flags)
    if species_update:
        review_flags.append("species_update_present")

    flags = [*row.flags, *identity_flags]
    if parse_error:
        flags.append(parse_error)
    plot = _clean_plot(_plot_from_title(page.page_title) or page.plot)
    return {
        "survey_id": survey_id,
        "date": survey_date.isoformat(),
        "site": "BRNV",
        "zone": plot[:1],
        "plot": plot,
        "tree_number": identity["tree_number"],
        "tree_code": (
            f"{plot}_{identity['tree_number']}_{identity['genus']}" if identity["tree_number"] else ""
        ),
        "trunk_number": identity["trunk_number"],
        "genus": identity["genus"],
        "spp": identity["spp"],
        "dbh_mm": dbh_mm,
        "health": row.health_observed,
        "alive": (
            "0"
            if section == "main" and dbh_mm is None and row.health_observed is None
            and row.standing_observed is None
            else ""
        ),
        "old_tag": "",
        "standing": _bool_to_recent_value(row.standing_observed),
        "poison_ivy": _bool_to_recent_value(row.poison_ivy_observed),
        "notes": notes,
        "section": section,
        "species_update": species_update,
        "identity_source": identity["identity_source"],
        "field_date": page.field_date,
        "source_page": page_number,
        "source_row": source_row,
        "source_row_label": row.row_label,
        "source_id_text": source_id_text,
        "source_page_title": page.page_title,
        "source_image": str(image_path),
        "source_json": str(raw_json_path),
        "transcription_flags": "; ".join(dict.fromkeys(flags)),
        "review_flags": "; ".join(dict.fromkeys(review_flags)),
    }


def _portrait_main_identity(
    plot: str,
    row: PortraitMainRowTranscription,
    manifest_rows: dict[tuple[str, str], dict[str, str]],
) -> tuple[dict[str, str], list[str], list[str]]:
    manifest = manifest_rows.get((plot, _clean_row_label(row.row_label)))
    if manifest is None:
        identity = _identity_from_portrait_text(row.tag_text, row.species_text, row.stem_text)
        identity["identity_source"] = "printed_ocr"
        return identity, ["No datasheet manifest row matched this Main row"], ["manifest_row_not_found"]

    identity = _identity_from_portrait_text(manifest["tag"], manifest["species"], manifest["stem"])
    identity["identity_source"] = "datasheet_manifest"
    mismatches = []
    if row.tag_text and _clean_tag_text(row.tag_text) != manifest["tag"]:
        mismatches.append(f"tag OCR {row.tag_text!r} != manifest {manifest['tag']!r}")
    if row.species_text and _compact_taxon(row.species_text) != _compact_taxon(manifest["species"]):
        mismatches.append(f"species OCR {row.species_text!r} != manifest {manifest['species']!r}")
    if row.stem_text and _clean_stem_text(row.stem_text) != manifest["stem"]:
        mismatches.append(f"stem OCR {row.stem_text!r} != manifest {manifest['stem']!r}")
    return identity, mismatches, ["manifest_identity_mismatch"] if mismatches else []


def _portrait_recruit_identity(
    row: PortraitMainRowTranscription | PortraitRecruitRowTranscription,
) -> tuple[dict[str, str], list[str], list[str]]:
    identity = _identity_from_portrait_text(row.tag_text, row.species_text, row.stem_text)
    identity["identity_source"] = "newly_tracked_handwriting"
    missing = [
        name
        for name, value in [
            ("tag", identity["tree_number"]),
            ("species", row.species_text),
            ("stem", identity["trunk_number"]),
        ]
        if not value
    ]
    if not missing:
        return identity, [], []
    message = f"Newly Tracked row missing identity fields: {', '.join(missing)}"
    return identity, [message], ["recruit_identity_incomplete"]


def _identity_from_portrait_text(tag: str, species: str, stem: str) -> dict[str, str]:
    genus, spp = _split_compact_taxon(species)
    return {
        "tree_number": _clean_tag_text(tag),
        "trunk_number": _clean_stem_text(stem),
        "genus": genus,
        "spp": spp,
        "identity_source": "",
    }


def _page_to_metadata(
    page: PageTranscription | PortraitPageTranscription,
    *,
    page_number: int,
    image_path: Path,
    raw_json_path: Path,
    survey_id: str,
    survey_date: date,
    page_context: dict[str, Any] | None = None,
) -> dict[str, object]:
    plot = _clean_plot(_plot_from_title(page.page_title) or page.plot)
    if isinstance(page, PortraitPageTranscription):
        field_date = page.field_date
        crew = " | ".join(item for item in page.crew if item.strip())
        problems = page.problems_and_info
        difficulty = page.difficulty or ""
        page_flags = "; ".join(page.flags)
    else:
        field_date = crew = problems = difficulty = page_flags = ""
    return {
        "survey_id": survey_id,
        "date": survey_date.isoformat(),
        "source_page": page_number,
        "source_page_title": page.page_title,
        "plot": plot,
        "field_date": field_date,
        "crew": crew,
        "problems_and_info": problems,
        "difficulty": difficulty,
        "page_flags": page_flags,
        **({
            "observer": page.observer, "recorder": page.recorder, "bonus_person": page.bonus_person,
            "recheck_answers": json.dumps([
                {**next((item for item in (page_context or {}).get("rechecks", []) if item["number"] == q.question_number), {}), **q.model_dump()}
                for q in page.recheck_answers]),
            "field_note_feedback": json.dumps([
                {**next((item for item in (page_context or {}).get("field_notes", []) if item["note_number"] == n.note_number), {}), **n.model_dump()}
                for n in page.field_note_feedback]),
            "other_handwriting": page.other_handwriting,
        } if isinstance(page, PortraitPageTranscription) else {}),
        "source_image": str(image_path),
        "source_json": str(raw_json_path),
    }


def _write_csvs(
    records: list[dict[str, object]],
    transcription_csv: Path,
    import_csv: Path,
    review_csv: Path,
) -> None:
    transcription_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=sorted(set(TRANSCRIPTION_COLUMNS) | set(IMPORT_RECENT_COLUMNS)))
    for column in set(TRANSCRIPTION_COLUMNS) | set(IMPORT_RECENT_COLUMNS):
        if column not in df:
            df[column] = ""
    df.to_csv(transcription_csv, index=False, columns=TRANSCRIPTION_COLUMNS)
    _reviewed_transcription_to_import(df).to_csv(
        import_csv,
        index=False,
        columns=IMPORT_RECENT_COLUMNS,
    )
    review = df.loc[
        df["transcription_flags"].fillna("").ne("") | df["review_flags"].fillna("").ne(""),
        TRANSCRIPTION_COLUMNS,
    ]
    review.to_csv(review_csv, index=False)


def _write_page_metadata(records: list[dict[str, object]], output_csv: Path) -> None:
    frame = pd.DataFrame(records)
    if frame.empty:
        frame = pd.DataFrame(columns=PAGE_METADATA_COLUMNS)
    for column in PAGE_METADATA_COLUMNS:
        if column not in frame:
            frame[column] = ""
    frame.to_csv(output_csv, index=False, columns=PAGE_METADATA_COLUMNS)


def _loads_strict_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(raw[start : end + 1])


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_OUTPUT_KEYS:
                return True
            if _contains_forbidden_key(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _parse_page_selection(selection: str | None, page_count: int) -> list[int]:
    if not selection or selection.lower() == "all":
        return list(range(1, page_count + 1))
    pages: set[int] = set()
    for part in selection.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    invalid = [page for page in pages if page < 1 or page > page_count]
    if invalid:
        raise ValueError(f"Pages outside PDF range 1-{page_count}: {invalid}")
    return sorted(pages)


def _resolve_image_paths(paths: Iterable[str | Path]) -> list[Path]:
    resolved = []
    for value in paths:
        path = Path(value).expanduser()
        if not path.exists():
            raise FileNotFoundError(path)
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError(f"Handwriting example must be an image: {path}")
        resolved.append(path)
    return resolved


def _load_handwriting_contexts(
    config_dir: Path,
    profile_names: Iterable[str],
    example_paths: Iterable[str | Path],
) -> list[HandwritingContext]:
    contexts = []
    profile_config_path = config_dir / "handwriting_profiles.toml"
    profiles = _read_handwriting_profiles(profile_config_path)
    project_root = config_dir.parent

    for profile_name in profile_names:
        try:
            profile = profiles[profile_name]
        except KeyError as exc:
            available = ", ".join(sorted(profiles)) or "none"
            raise ValueError(f"Unknown handwriting profile {profile_name!r}; available profiles: {available}") from exc
        contexts.append(
            HandwritingContext(
                name=profile_name,
                description=str(profile.get("description", "")).strip(),
                examples=tuple(
                    _resolve_image_paths(
                        _resolve_relative_paths(profile.get("examples", []), project_root),
                    )
                ),
            )
        )

    manual_examples = _resolve_image_paths(example_paths)
    if manual_examples:
        contexts.append(
            HandwritingContext(
                name="manual",
                description=(
                    "Additional handwriting calibration examples supplied on the command line. "
                    "Use these only as local style references."
                ),
                examples=tuple(manual_examples),
            )
        )
    return contexts


def _read_handwriting_profiles(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError(f"Invalid handwriting profile config: {path}")
    return profiles


def _resolve_relative_paths(paths: Iterable[str | Path], base_dir: Path) -> list[Path]:
    resolved = []
    for value in paths:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = base_dir / path
        resolved.append(path)
    return resolved


def _image_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def _pdf_page_count(pdf_path: Path) -> int:
    proc = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not determine page count for {pdf_path}")


def _render_pages(pdf_path: Path, rendered_dir: Path, page_numbers: Iterable[int], dpi: int) -> dict[int, Path]:
    rendered: dict[int, Path] = {}
    for page_number in page_numbers:
        prefix = rendered_dir / f"page_{page_number:03d}"
        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-singlefile",
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                "-r",
                str(dpi),
                str(pdf_path),
                str(prefix),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered[page_number] = prefix.with_suffix(".png")
    return rendered


def _write_review_crops(
    image_path: Path,
    output_dir: Path,
    save_cell_crops: bool,
    *,
    datasheet_format: str = LEGACY_FORMAT,
) -> dict[str, object] | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as image:
        image_width, image_height = image.size
        table_box = _detect_table_box(image)
        if table_box is None:
            return None
        table = image.crop(table_box)
        table_path = output_dir / "table.png"
        table.save(table_path)
        if datasheet_format == PORTRAIT_FORMAT:
            row_lines = _portrait_horizontal_grid_lines(table)
        else:
            row_lines = _detect_grid_lines(table, axis="y")
        row_bands = _line_bands(row_lines)
        table_left, table_top, table_right, table_bottom = table_box
        col_bands = _detect_column_ranges(table, row_lines, datasheet_format=datasheet_format)
        column_count = len(col_bands)
        columns = [
            {
                "index": column_number,
                "name": _column_name(column_number, column_count, datasheet_format),
                "box": {
                    "x": table_left + left,
                    "y": table_top,
                    "width": right - left,
                    "height": table_bottom - table_top,
                },
            }
            for column_number, (left, right) in enumerate(col_bands, start=1)
            if right - left >= 8
        ]
        rows = []
        row_dir = output_dir / "rows"
        row_dir.mkdir(exist_ok=True)
        for row_number, (top, bottom) in enumerate(row_bands, start=1):
            if bottom - top < 8:
                continue
            row_crop = table.crop((0, top, table.width, bottom))
            row_path = row_dir / f"row_{row_number:03d}.png"
            row_crop.save(row_path)
            rows.append(
                {
                    "crop_index": row_number,
                    "source_row": row_number - 1,
                    "crop_path": str(row_path),
                    "box": {
                        "x": table_left,
                        "y": table_top + top,
                        "width": table_right - table_left,
                        "height": bottom - top,
                    },
                }
            )
            if save_cell_crops:
                cell_dir = output_dir / "cells" / f"row_{row_number:03d}"
                cell_dir.mkdir(parents=True, exist_ok=True)
                for col_number, (left, right) in enumerate(col_bands, start=1):
                    if right - left < 8:
                        continue
                    table.crop((left, top, right, bottom)).save(cell_dir / f"col_{col_number:02d}.png")
        return {
            "page_image_width": image_width,
            "page_image_height": image_height,
            "table_path": str(table_path),
            "table_box": {
                "x": table_left,
                "y": table_top,
                "width": table_right - table_left,
                "height": table_bottom - table_top,
            },
            "columns": columns,
            "rows": rows,
        }


def _column_name(column_number: int, column_count: int, datasheet_format: str) -> str:
    if datasheet_format == PORTRAIT_FORMAT and column_count >= 12:
        names = [
            "row_label",
            "tag_text",
            "species_text",
            "stem_text",
            "health",
            "standing",
            "poison_ivy",
            "printed_dbh",
            "hsp_1",
            "hsp_2",
            "species_update",
            "notes",
        ]
    elif datasheet_format == PORTRAIT_FORMAT:
        names = [
            "row_label",
            "tag_text",
            "species_text",
            "stem_text",
            "dbh_mm",
            "health",
            "standing",
            "poison_ivy",
            "notes",
        ]
    else:
        names = [
            "row_label",
            "id_text",
            "dbh_mm",
            "health",
            "standing",
            "poison_ivy",
            "dhas_1",
            "dhas_2",
            "notes",
        ]
    if 1 <= column_number <= len(names):
        return names[column_number - 1]
    return f"column_{column_number}"


def _detect_column_ranges(
    table: Image.Image,
    row_lines: list[int],
    *,
    datasheet_format: str = LEGACY_FORMAT,
) -> list[tuple[int, int]]:
    grid_left, _grid_right = _horizontal_table_bounds(table, row_lines)
    grid_right = table.width
    separators = [
        separator
        for separator in _vertical_table_separators(table)
        if grid_left + 20 < separator < grid_right - 20
    ]
    expected_separator_counts = {8, 11} if datasheet_format == PORTRAIT_FORMAT else {8}
    if len(separators) in expected_separator_counts:
        boundaries = [grid_left, *separators, grid_right]
    else:
        portrait_main = datasheet_format == PORTRAIT_FORMAT and len(row_lines) > 12
        boundaries = _fallback_column_boundaries(
            grid_left,
            grid_right,
            datasheet_format=datasheet_format,
            portrait_main=portrait_main,
        )
    return [(left, right) for left, right in zip(boundaries, boundaries[1:]) if right > left + 1]


def _horizontal_table_bounds(table: Image.Image, row_lines: list[int]) -> tuple[int, int]:
    gray = table.convert("L")
    width, _height = gray.size
    pixels = gray.load()
    left_edges: list[int] = []
    right_edges: list[int] = []
    for y in row_lines:
        dark_xs = [x for x in range(width) if pixels[x, y] < 180]
        if len(dark_xs) < width * 0.15:
            continue
        left_edges.append(min(dark_xs))
        right_edges.append(max(dark_xs))
    if not left_edges or not right_edges:
        return 0, width

    left = _median_int(left_edges)
    sorted_rights = sorted(right_edges)
    right = sorted_rights[min(int(len(sorted_rights) * 0.75), len(sorted_rights) - 1)]
    return max(left, 0), min(max(right, left + 1), width)


def _vertical_table_separators(table: Image.Image) -> list[int]:
    gray = table.convert("L")
    width, height = gray.size
    pixels = gray.load()
    candidates = []
    for x in range(width):
        dark_count = 0
        run = 0
        max_run = 0
        for y in range(height):
            if pixels[x, y] < 180:
                dark_count += 1
                run += 1
                max_run = max(max_run, run)
            else:
                run = 0
        if dark_count > height * 0.18 and max_run > height * 0.10:
            candidates.append(x)

    groups: list[list[int]] = []
    current: list[int] = []
    previous: int | None = None
    for x in candidates:
        if previous is None or x <= previous + 14:
            current.append(x)
        else:
            groups.append(current)
            current = [x]
        previous = x
    if current:
        groups.append(current)
    return [round((group[0] + group[-1]) / 2) for group in groups]


def _fallback_column_boundaries(
    left: int,
    right: int,
    *,
    datasheet_format: str = LEGACY_FORMAT,
    portrait_main: bool = False,
    main_column_widths: list[float] | None = None,
) -> list[int]:
    if datasheet_format == PORTRAIT_FORMAT and portrait_main:
        widths = main_column_widths or [0.25, 0.44, 0.52, 0.20, 0.38, 0.28, 0.25, 0.39, 0.46, 0.46, 0.78, 3.44]
        total = sum(widths)
        proportions = [item / total for item in widths]
    elif datasheet_format == PORTRAIT_FORMAT:
        widths = [0.30, 0.56, 0.62, 0.25, 0.52, 0.46, 0.30, 0.28, 4.57]
        total = sum(widths)
        proportions = [item / total for item in widths]
    else:
        proportions = [0.06, 0.185, 0.085, 0.114, 0.093, 0.056, 0.159, 0.156, 0.092]
    width = max(right - left, 1)
    boundaries = [left]
    running = left
    for proportion in proportions[:-1]:
        running += round(width * proportion)
        boundaries.append(running)
    boundaries.append(right)
    return boundaries


def _median_int(values: list[int]) -> int:
    values = sorted(values)
    midpoint = len(values) // 2
    if len(values) % 2:
        return values[midpoint]
    return round((values[midpoint - 1] + values[midpoint]) / 2)


def _detect_table_box(image: Image.Image) -> tuple[int, int, int, int] | None:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    points: list[tuple[int, int]] = []
    for y in range(int(height * 0.10), int(height * 0.92), 2):
        for x in range(int(width * 0.08), int(width * 0.92), 2):
            if pixels[x, y] < 135:
                points.append((x, y))
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (
        max(min(xs) - 10, 0),
        max(min(ys) - 10, 0),
        min(max(xs) + 10, width),
        min(max(ys) + 10, height),
    )


def _detect_grid_lines(
    image: Image.Image,
    axis: str,
    *,
    dark_threshold: int = 150,
    minimum_coverage: float = 0.25,
) -> list[int]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    totals = []
    if axis == "y":
        for y in range(height):
            totals.append(sum(1 for x in range(width) if pixels[x, y] < dark_threshold))
        threshold = max(12, int(width * minimum_coverage))
    else:
        for x in range(width):
            totals.append(sum(1 for y in range(height) if pixels[x, y] < dark_threshold))
        threshold = max(12, int(height * minimum_coverage))
    groups: list[list[int]] = []
    current: list[int] = []
    for index, total in enumerate(totals):
        if total >= threshold:
            current.append(index)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return [group[len(group) // 2] for group in groups]


def _portrait_horizontal_grid_lines(table: Image.Image) -> list[int]:
    gray = table.convert("L")
    width, height = gray.size
    pixels = gray.load()
    start_x = int(width * 0.58)
    means = [
        sum(pixels[x, y] for x in range(start_x, width)) / max(width - start_x, 1)
        for y in range(height)
    ]
    groups: list[list[int]] = []
    current: list[int] = []
    for index, mean in enumerate(means):
        if mean < 205:
            current.append(index)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    centers = [group[len(group) // 2] for group in groups]
    return _longest_regular_line_run(centers)


def _longest_regular_line_run(lines: list[int]) -> list[int]:
    if len(lines) < 2:
        return lines
    best: list[int] = []
    current = [lines[0]]
    for line in lines[1:]:
        gap = line - current[-1]
        if 30 <= gap <= 90:
            current.append(line)
        else:
            if len(current) > len(best):
                best = current
            current = [line]
    if len(current) > len(best):
        best = current
    return best


def _line_bands(lines: list[int]) -> list[tuple[int, int]]:
    return [(start + 1, end) for start, end in zip(lines, lines[1:]) if end > start + 1]


def _survey_start(config: Config, survey_id: str) -> date:
    for survey in config.surveys:
        if survey.id == survey_id:
            return survey.start
    raise ValueError(f"Unknown survey_id {survey_id!r}; add it to config/surveys.toml first")


def _plot_from_title(title: str) -> str:
    match = re.search(r"\bBRNV(?:\s|\.)+([A-Z]\d+)\b", title, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _clean_plot(value: object) -> str:
    text = str(value or "").strip().upper()
    return re.sub(r"^BRNV(?:\s|\.)+", "", text)


def _clean_flag(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _row_has_observation(row: RowTranscription) -> bool:
    return any(
        value not in (None, "")
        for value in [
            row.dbh_mm,
            row.health_observed,
            row.standing_observed,
            row.poison_ivy_observed,
            row.notes,
        ]
    )


def _review_flags(row: RowTranscription, *, parse_error: str = "") -> list[str]:
    flags: list[str] = []
    has_health = row.health_observed is not None
    has_note = bool(row.notes.strip())

    if parse_error:
        flags.append("id_parse_error")
    if bool(row.flags):
        flags.append("model_flagged_ambiguity")
    if not has_health and row.dbh_mm is not None:
        flags.append("dbh_without_health")
    if has_health and row.standing_observed is None:
        flags.append("measurement_without_standing")
        if row.health_observed == 0:
            flags.append("dead_health_without_standing")
    if not has_health and row.standing_observed is not None:
        flags.append("standing_without_measurement")
    if row.health_observed is not None and row.health_observed > 0 and row.standing_observed is False:
        flags.append("alive_health_not_standing")
    if has_note:
        flags.append("notes_present")
    return flags


def _bool_to_recent_value(value: bool | None) -> str:
    if value is None:
        return ""
    return "1" if value else "0"


def _load_gemini_api_key() -> str | None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


__all__ = [
    "DEFAULT_DATASHEET_FORMAT",
    "DEFAULT_MODEL",
    "PageTranscription",
    "PortraitMainRowTranscription",
    "PortraitPageTranscription",
    "PortraitRecruitRowTranscription",
    "RowTranscription",
    "TranscriptionResult",
    "add_transcribe_parser",
    "parse_tree_id",
    "rematerialize_portrait_run",
    "run_rematerialize_command",
    "run_transcribe_command",
    "transcribe_pdf",
]
