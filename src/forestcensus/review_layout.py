"""Locate separate portrait tables without changing transcribed observations."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from statistics import median

from PIL import Image

from .llm_transcribe import PORTRAIT_FORMAT, _column_name, _detect_grid_lines, _fallback_column_boundaries


def _grid_runs(image: Image.Image) -> list[tuple[int, list[int]]]:
    scale = image.width / 2550
    candidates = []
    # Narrow strips retain grid lines on tilted scans; a wide projection blurs them.
    for fraction in (0.86, 0.90, 0.80, 0.75, 0.62, 0.45, 0.36, 0.22):
        x = round(image.width * fraction)
        half_width = max(4, round(20 * scale))
        strip = image.crop((x - half_width, 0, x + half_width, image.height))
        lines = _detect_grid_lines(strip, axis="y", dark_threshold=185, minimum_coverage=0.7)
        current: list[int] = []
        for line in [*lines, image.height + round(200 * scale)]:
            if current and not 45 * scale <= line - current[-1] <= 90 * scale:
                if len(current) > 1 and median(b - a for a, b in zip(current, current[1:])) > 50 * scale:
                    candidates.append((x, current))
                current = []
            current.append(line)
    return candidates


def _table_layout(
    image: Image.Image,
    x: int,
    lines: list[int],
    section: str,
    records: list[dict[str, str]],
    main_column_widths: list[float] | None = None,
) -> dict[str, object]:
    scale = image.width / 2550
    reference_x = x - round(120 * scale)
    strip = image.crop((reference_x - 10, 0, reference_x + 10, image.height))
    adjacent_lines = _detect_grid_lines(strip, axis="y", dark_threshold=185, minimum_coverage=0.7)
    slopes = []
    for y in lines:
        nearby = [v for v in adjacent_lines if abs(v - y) < 15 * scale]
        if nearby:
            slopes.append((min(nearby, key=lambda v: abs(v - y)) - y) / (reference_x - x))
    slope = median(slopes) if slopes else 0.0
    # Refine over a longer baseline so pixel rounding does not shift the overlay
    # by several rows at the opposite edge of a tilted page.
    refined_slopes = []
    for distance in (240, 400, 600):
        reference_x = x - round(distance * scale)
        strip = image.crop((reference_x - 10, 0, reference_x + 10, image.height))
        adjacent_lines = _detect_grid_lines(strip, axis="y", dark_threshold=185, minimum_coverage=0.7)
        for y in lines:
            predicted_y = y + slope * (reference_x - x)
            nearby = [v for v in adjacent_lines if abs(v - predicted_y) < 12 * scale]
            if nearby:
                matched = min(nearby, key=lambda v: abs(v - predicted_y))
                refined_slopes.append((matched - y) / (reference_x - x))
    if refined_slopes:
        slope = median(refined_slopes)
    pixels = image.convert("L").load()
    assert pixels is not None
    left_edges, right_edges = [], []
    for y in (lines[0], lines[len(lines) // 2], lines[-1]):
        dark = []
        for px in range(round(image.width * 0.02), round(image.width * 0.98)):
            py = round(y + slope * (px - x))
            if 4 <= py < image.height - 4 and min(pixels[px, py + offset] for offset in range(-3, 4)) < 185:
                dark.append(px)
        if dark:
            left_edges.append(min(dark))
            right_edges.append(max(dark))
    left = round(median(left_edges)) if left_edges else round(image.width * 0.09)
    right = round(median(right_edges)) if right_edges else round(image.width * 0.92)
    boundaries = _fallback_column_boundaries(left, right, datasheet_format=PORTRAIT_FORMAT, portrait_main=section == "main", main_column_widths=main_column_widths)
    columns = [
        {
            "index": i,
            "name": _column_name(i, len(boundaries) - 1, PORTRAIT_FORMAT),
            "box": {"x": a, "y": lines[0], "width": b - a, "height": lines[-1] - lines[0]},
        }
        for i, (a, b) in enumerate(zip(boundaries, boundaries[1:]), start=1)
    ]
    first_label = min(int(r["source_row_label"]) for r in records) if section == "main" else 1
    rows = []
    for i, (top, bottom) in enumerate(zip(lines, lines[1:])):
        rows.append({
            "source_row_label": str(first_label + i) if section == "main" else f"N{i + 1}",
            "box": {
                "x": left,
                "y": round(top + slope * (left - x)) + 1,
                "width": right - left,
                "height": bottom - top - 1,
                "skew_y": slope,
            },
        })
    return {"section": section, "columns": columns, "rows": rows}


def portrait_tables(image: Image.Image, records: list[dict[str, str]], *, newly_tracked_slots: int = 6,
                    main_header_same_height: bool = False, main_column_widths: list[float] | None = None) -> list[dict[str, object]]:
    main = [r for r in records if r.get("section") == "main"]
    new = [r for r in records if r.get("section") == "newly_tracked"]
    candidates = _grid_runs(image)
    tables = []
    main_end = 0
    if main:
        labels = sorted(int(r["source_row_label"]) for r in main if str(r["source_row_label"]).isdigit())
        consecutive = labels == list(range(labels[0], labels[0] + len(main))) if labels else False
        matches = [(x, lines[1:] if main_header_same_height and len(lines) == len(main) + 2 else lines)
                   for x, lines in candidates if consecutive and len(lines) - 1 in
                   ({len(main), len(main) + 1} if main_header_same_height else {len(main)})]
        if matches:
            x, lines = min(matches, key=lambda item: item[1][0])
            tables.append(_table_layout(image, x, lines, "main", main, main_column_widths))
            main_end = lines[-1]
    if new:
        matches = [(x, lines[1:] if len(lines) == newly_tracked_slots + 2 else lines)
                   for x, lines in candidates if len(lines) in {newly_tracked_slots + 1, newly_tracked_slots + 2} and lines[0] > main_end]
        if matches and (not main or tables):
            # Slot labels refer to physical rows, including blank/crossed-out slots.
            x, lines = max(matches, key=lambda item: item[1][0])
            tables.append(_table_layout(image, x, lines, "newly_tracked", new))
    return tables


def rebuild_review_layouts(run_dir: str | Path, *, overrides_path: str | Path | None = None) -> dict[str, object]:
    """Rebuild display geometry only; retain CSVs, model responses, and review keys."""
    run_dir = Path(run_dir)
    metadata = json.loads((run_dir / "run_metadata.json").read_text())
    if metadata.get("datasheet_format") != PORTRAIT_FORMAT:
        raise ValueError("Layout rebuilding requires a portrait_2026 run")
    with (run_dir / "transcription.csv").open(newline="") as source:
        records = list(csv.DictReader(source))
    overrides = json.loads(Path(overrides_path).read_text()) if overrides_path else {"pages": []}
    layout_path = run_dir / "layout_manifest.json"
    original = json.loads(layout_path.read_text())
    layout = json.loads(json.dumps(original))
    unmapped = []
    updated = 0
    applied_overrides = set()
    for page in layout["pages"]:
        page_records = [r for r in records if int(r["source_page"]) == page["source_page"]]
        if not page_records:
            continue
        image_path = Path(page_records[0]["source_image"])
        with Image.open(image_path) as image:
            tables = portrait_tables(image, page_records, **metadata.get("portrait_layout", {}))
        if not tables:
            # Legacy geometry remains available, but expose unresolved recruit
            # locations instead of silently claiming a complete rebuild.
            unmapped.extend({k: r[k] for k in ("source_page", "source_row_label", "section", "source_id_text")} for r in page_records)
            if metadata.get("portrait_layout"):
                page["tables"] = []
                page["rows"] = []
                page["columns"] = []
            continue
        # Keep legacy Main geometry only if the new detector could not locate it.
        if not any(t["section"] == "main" for t in tables) and any(r["section"] == "main" for r in page_records):
            tables.insert(0, {"section": "main", "columns": page["columns"], "rows": page["rows"]})
        for override in overrides["pages"]:
            if override["source_page"] != page["source_page"]:
                continue
            if hashlib.sha256(image_path.read_bytes()).hexdigest() != override["image_sha256"]:
                raise ValueError(f"Layout override image mismatch on page {page['source_page']}")
            valid_keys = {(r["source_row_label"], r["source_id_text"]) for r in page_records if r["section"] == "newly_tracked"}
            for row in override["rows"]:
                if (row["source_row_label"], row["source_id_text"]) not in valid_keys:
                    raise ValueError(f"Layout override row mismatch on page {page['source_page']}")
            # Prose observations have a source rectangle but no table columns.
            columns = json.loads(json.dumps(override.get("columns", tables[0]["columns"])))
            for column in columns:
                column["name"] = override.get("column_names", {}).get(column["name"], column["name"])
            tables.append({"section": "newly_tracked", "columns": columns, "rows": override["rows"], "method": "visually_verified_handwritten_additions"})
            applied_overrides.add(page["source_page"])
        page["tables"] = tables
        for row in page_records:
            if not any(t["section"] == row["section"] and any(r.get("source_row_label") == row["source_row_label"] for r in t["rows"]) for t in tables):
                unmapped.append({k: row[k] for k in ("source_page", "source_row_label", "section", "source_id_text")})
        updated += 1
    expected_overrides = {p["source_page"] for p in overrides["pages"]}
    if expected_overrides != applied_overrides:
        raise ValueError(f"Could not apply layout overrides for pages {sorted(expected_overrides - applied_overrides)}")
    backup_path = run_dir / "layout_manifest.before_tables.json"
    if not backup_path.exists():
        backup_path.write_text(json.dumps(original, indent=2) + "\n")
    layout["version"] = 2
    layout_path.write_text(json.dumps(layout, indent=2) + "\n")
    return {"pages_updated": updated, "unmapped_rows": unmapped, "layout_manifest": str(layout_path)}
