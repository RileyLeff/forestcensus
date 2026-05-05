"""Experimental LLM transcription for scanned recent census datasheets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

import pandas as pd
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .config import Config, load_config


DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
ID_RE = re.compile(
    r"^\s*(?P<genus>[A-Za-z]+)\.(?P<species>[A-Za-z]+)\.(?P<tree>\d+)\.(?P<slot>\d+)\s*$"
)
FORBIDDEN_OUTPUT_KEYS = {"dhas", "dhas1", "dhas2", "dhas_1", "dhas_2", "dhas.1", "dhas.2"}


class RowTranscription(BaseModel):
    """One non-empty table row transcribed from a scanned datasheet."""

    model_config = ConfigDict(extra="forbid")

    row_label: str = Field(description="Printed leftmost row label, such as 1, 35, or 52.")
    id_text: str = Field(description="Printed id exactly as shown, such as Ace.rub.929.1.")
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
    id_text: str
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


@dataclass(frozen=True)
class TranscriptionResult:
    output_dir: Path
    raw_json_dir: Path
    rendered_dir: Path
    crops_dir: Path
    transcription_csv: Path
    import_csv: Path
    review_csv: Path
    rejected_json: Path
    pages_requested: list[int]
    rows: int
    rejected_pages: int


def transcribe_pdf(
    pdf_path: str | Path,
    *,
    survey_id: str = "October_2025",
    config_dir: str | Path = "config",
    output_dir: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    pages: str | None = "1",
    dpi: int = 180,
    media_resolution: str = "MEDIA_RESOLUTION_HIGH",
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
    output_dir = Path(output_dir) if output_dir else Path("output/llm_transcription") / pdf_path.stem
    rendered_dir = output_dir / "pages"
    raw_json_dir = output_dir / "raw_json"
    crops_dir = output_dir / "crops"
    for path in (rendered_dir, raw_json_dir, crops_dir):
        path.mkdir(parents=True, exist_ok=True)

    page_numbers = _parse_page_selection(pages, _pdf_page_count(pdf_path))
    handwriting_example_paths = _resolve_image_paths(handwriting_examples or [])
    rendered_pages = _render_pages(pdf_path, rendered_dir, page_numbers, dpi)
    for page_number, image_path in rendered_pages.items():
        _write_review_crops(image_path, crops_dir / f"page_{page_number:03d}", save_cell_crops)

    records: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    client = None
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
        try:
            page = _transcribe_page(
                client,
                image_path,
                model=model,
                media_resolution=media_resolution,
                handwriting_examples=handwriting_example_paths,
            )
        except Exception as exc:  # noqa: BLE001 - persist page-level failures for review.
            rejected.append(
                {
                    "source_page": page_number,
                    "image_path": str(image_path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        raw_json_path = raw_json_dir / f"page_{page_number:03d}.json"
        raw_json_path.write_text(page.model_dump_json(indent=2) + "\n", encoding="utf-8")
        records.extend(
            _page_to_records(
                page,
                page_number=page_number,
                image_path=image_path,
                raw_json_path=raw_json_path,
                survey_id=survey_id,
                survey_date=survey_date,
            )
        )

    rejected_json = output_dir / "rejected_pages.json"
    rejected_json.write_text(json.dumps(rejected, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    transcription_csv = output_dir / "transcription.csv"
    import_csv = output_dir / "import_recent_format.csv"
    review_csv = output_dir / "review_rows.csv"
    _write_csvs(records, transcription_csv, import_csv, review_csv)
    return TranscriptionResult(
        output_dir=output_dir,
        raw_json_dir=raw_json_dir,
        rendered_dir=rendered_dir,
        crops_dir=crops_dir,
        transcription_csv=transcription_csv,
        import_csv=import_csv,
        review_csv=review_csv,
        rejected_json=rejected_json,
        pages_requested=page_numbers,
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
        "--pages",
        default="1",
        help="Pages to process, e.g. 1, 1-3, 1,10,58, or all. Defaults to page 1.",
    )
    parser.add_argument("--dpi", type=int, default=180)
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


def run_transcribe_command(args: argparse.Namespace) -> None:
    result = transcribe_pdf(
        args.pdf,
        survey_id=args.survey_id,
        config_dir=args.config_dir,
        output_dir=args.out_dir,
        model=args.model,
        pages=args.pages,
        dpi=args.dpi,
        media_resolution=args.media_resolution,
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
                "rejected_json": str(result.rejected_json),
            },
            sort_keys=True,
        )
    )


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


def _transcribe_page(
    client: Any,
    image_path: Path,
    *,
    model: str,
    media_resolution: str,
    handwriting_examples: list[Path],
) -> PageTranscription:
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=_gemini_contents(types, image_path, handwriting_examples),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GeminiPageTranscription,
            temperature=0,
            media_resolution=getattr(types.MediaResolution, media_resolution),
        ),
    )
    raw = response.text or ""
    if raw:
        data = _loads_strict_json(raw)
        if _contains_forbidden_key(data):
            raise ValueError("LLM output included forbidden dhas-related keys")
        return PageTranscription.model_validate(data)
    parsed = getattr(response, "parsed", None)
    if parsed is None:
        raise ValueError("Gemini response had neither text nor parsed structured output")
    if isinstance(parsed, PageTranscription):
        return parsed
    return PageTranscription.model_validate(parsed)


def _gemini_contents(types: Any, image_path: Path, handwriting_examples: list[Path]) -> list[Any]:
    contents: list[Any] = [_page_prompt()]
    if handwriting_examples:
        contents.append(
            "Handwriting calibration examples follow. Use these only to understand local digit style; "
            "do not transcribe them as census rows."
        )
        for example_path in handwriting_examples:
            contents.append(types.Part.from_bytes(data=example_path.read_bytes(), mime_type=_image_mime_type(example_path)))
        contents.append("Now transcribe the target datasheet page below.")
    contents.append(types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png"))
    return contents


def _page_prompt() -> str:
    return (
        "You are decoding a scanned forest census datasheet into a strict data schema. "
        "This is not free-form OCR: every cell must be interpreted according to the known column domains below. "
        "\n\n"
        "Columns to transcribe:\n"
        "- row_label: printed row number at far left. Copy exactly.\n"
        "- id_text: printed tree id, e.g. Ace.rub.929.1. Copy exactly from the id column; never infer from row order.\n"
        "- dbh_mm: handwritten tree diameter in millimeters. Valid output is a number or null if blank/unreadable.\n"
        "- health_observed: handwritten health score. Valid values are integers 0 through 10 only. "
        "0 means dead; 1 through 10 mean alive. Use null if blank/unreadable.\n"
        "- standing_observed: stnd column. Valid values are true, false, or null. "
        "Handwritten 1 means true/standing; handwritten 0 means false/not standing; blank means null.\n"
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
        "- Use neighboring rows and the printed grid as context to distinguish blanks from 0/1 marks."
    )


def _page_to_records(
    page: PageTranscription,
    *,
    page_number: int,
    image_path: Path,
    raw_json_path: Path,
    survey_id: str,
    survey_date: date,
) -> list[dict[str, object]]:
    records = []
    plot = _clean_plot(page.plot or _plot_from_title(page.page_title))
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


def _write_csvs(
    records: list[dict[str, object]],
    transcription_csv: Path,
    import_csv: Path,
    review_csv: Path,
) -> None:
    transcription_csv.parent.mkdir(parents=True, exist_ok=True)
    transcription_columns = [
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
        "standing",
        "poison_ivy",
        "notes",
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
    import_columns = [
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
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=sorted(set(transcription_columns) | set(import_columns)))
    df.to_csv(transcription_csv, index=False, columns=transcription_columns)
    df.to_csv(import_csv, index=False, columns=import_columns)
    review = df.loc[
        df["transcription_flags"].fillna("").ne("") | df["review_flags"].fillna("").ne(""),
        transcription_columns,
    ]
    review.to_csv(review_csv, index=False)


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


def _write_review_crops(image_path: Path, output_dir: Path, save_cell_crops: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as image:
        table_box = _detect_table_box(image)
        if table_box is None:
            return
        table = image.crop(table_box)
        table_path = output_dir / "table.png"
        table.save(table_path)
        row_lines = _detect_grid_lines(table, axis="y")
        col_lines = _detect_grid_lines(table, axis="x") if save_cell_crops else []
        row_dir = output_dir / "rows"
        row_dir.mkdir(exist_ok=True)
        for row_number, (top, bottom) in enumerate(_line_bands(row_lines), start=1):
            if bottom - top < 8:
                continue
            row_crop = table.crop((0, top, table.width, bottom))
            row_crop.save(row_dir / f"row_{row_number:03d}.png")
            if save_cell_crops:
                cell_dir = output_dir / "cells" / f"row_{row_number:03d}"
                cell_dir.mkdir(parents=True, exist_ok=True)
                for col_number, (left, right) in enumerate(_line_bands(col_lines), start=1):
                    if right - left < 8:
                        continue
                    table.crop((left, top, right, bottom)).save(cell_dir / f"col_{col_number:02d}.png")


def _detect_table_box(image: Image.Image) -> tuple[int, int, int, int] | None:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    points: list[tuple[int, int]] = []
    for y in range(int(height * 0.28), int(height * 0.92), 2):
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


def _detect_grid_lines(image: Image.Image, axis: str) -> list[int]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    totals = []
    if axis == "y":
        for y in range(height):
            totals.append(sum(1 for x in range(width) if pixels[x, y] < 150))
        threshold = max(12, int(width * 0.25))
    else:
        for x in range(width):
            totals.append(sum(1 for y in range(height) if pixels[x, y] < 150))
        threshold = max(12, int(height * 0.25))
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


def _line_bands(lines: list[int]) -> list[tuple[int, int]]:
    return [(start + 1, end) for start, end in zip(lines, lines[1:]) if end > start + 1]


def _survey_start(config: Config, survey_id: str) -> date:
    for survey in config.surveys:
        if survey.id == survey_id:
            return survey.start
    raise ValueError(f"Unknown survey_id {survey_id!r}; add it to config/surveys.toml first")


def _plot_from_title(title: str) -> str:
    match = re.search(r"BRNV\.([LMHR]\d+)", title, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _clean_plot(value: object) -> str:
    return str(value or "").strip().upper().removeprefix("BRNV.")


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
    "DEFAULT_MODEL",
    "PageTranscription",
    "RowTranscription",
    "TranscriptionResult",
    "add_transcribe_parser",
    "parse_tree_id",
    "run_transcribe_command",
    "transcribe_pdf",
]
