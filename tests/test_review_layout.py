from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from forestcensus.review_layout import portrait_tables, rebuild_review_layouts


def page_image(*, slope: float = 0.0) -> Image.Image:
    image = Image.new("L", (2550, 3300), "white")
    draw = ImageDraw.Draw(image)
    # Equal-size Main and Newly Tracked grids must remain distinct tables.
    for start, step in ((600, 56), (1200, 60)):
        for index in range(7):
            y = start + index * step
            draw.line((230, y, 2350, round(y + slope * 2120)), fill="black", width=3)
    return image


def page_records() -> list[dict[str, str]]:
    return [
        {"source_page": "1", "source_row_label": str(i), "source_id_text": f"{i}|ILEOPA|1", "section": "main"}
        for i in range(41, 47)
    ] + [
        {"source_page": "1", "source_row_label": label, "source_id_text": f"{label}|ILEOPA|1", "section": "newly_tracked"}
        for label in ("N2", "N6")
    ]


def test_october_twenty_point_header_and_twelve_new_slots():
    image = Image.new("L", (2550, 3300), "white")
    draw = ImageDraw.Draw(image)
    for start, count in ((450, 8), (1300, 13)):
        for i in range(count):
            y = start + i * 83
            draw.line((120, y, 2350, y), fill="black", width=3)
    records = page_records()[:6] + [{"source_row_label": "N12", "section": "newly_tracked"}]
    main, new = portrait_tables(image, records, newly_tracked_slots=12, main_header_same_height=True)
    assert main["rows"][0]["source_row_label"] == "41"
    assert abs(main["rows"][0]["box"]["y"] - 534) < 3
    assert len(new["rows"]) == 12
    assert new["rows"][-1]["source_row_label"] == "N12"
    assert main["rows"][0]["box"]["x"] == 120


def test_crossed_out_note_does_not_split_main_grid():
    image = Image.new("L", (2550, 3300), "white")
    draw = ImageDraw.Draw(image)
    for i in range(18):
        y = 300 + i * 80
        draw.line((120, y, 2400, y), fill="black", width=3)
    draw.line((1400, 1220, 2450, 1220), fill="black", width=7)
    records = [{"source_row_label": str(n), "section": "main"} for n in range(31, 47)]
    tables = portrait_tables(image, records, main_header_same_height=True, newly_tracked_slots=12)
    assert len(tables[0]["rows"]) == 16
    assert tables[0]["rows"][0]["source_row_label"] == "31"


@pytest.mark.parametrize("slope", [0.0, -0.05, 0.02])
def test_separate_tables_keep_slot_labels_and_column_order(slope: float) -> None:
    tables = portrait_tables(page_image(slope=slope), page_records())
    assert [t["section"] for t in tables] == ["main", "newly_tracked"]
    main, recruits = tables
    assert [r["source_row_label"] for r in main["rows"]] == [str(i) for i in range(41, 47)]
    # Blank N1/N3/N4/N5 slots must not shift N2 or N6 up the page.
    assert [r["source_row_label"] for r in recruits["rows"]] == [f"N{i}" for i in range(1, 7)]
    assert abs(recruits["rows"][1]["box"]["y"] - 1260) <= 5
    assert abs(recruits["rows"][5]["box"]["y"] - 1500) <= 5
    assert abs(recruits["rows"][0]["box"]["skew_y"] - slope) < 0.003
    main_columns = [c["name"] for c in main["columns"]]
    new_columns = [c["name"] for c in recruits["columns"]]
    assert main_columns.index("health") < main_columns.index("printed_dbh")
    assert new_columns.index("dbh_mm") < new_columns.index("health")


def write_run(tmp_path: Path) -> tuple[Path, Path]:
    image_path = tmp_path / "page.png"
    page_image().save(image_path)
    (tmp_path / "run_metadata.json").write_text('{"datasheet_format":"portrait_2026"}')
    records = page_records()
    for row in records:
        row["source_image"] = str(image_path)
    csv_path = tmp_path / "transcription.csv"
    with csv_path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    layout_path = tmp_path / "layout_manifest.json"
    layout_path.write_text(json.dumps({"pages": [{"source_page": 1, "columns": [], "rows": []}]}))
    return image_path, layout_path


def test_rebuild_changes_only_geometry_and_is_repeatable(tmp_path: Path) -> None:
    _, layout_path = write_run(tmp_path)
    csv_bytes = (tmp_path / "transcription.csv").read_bytes()
    (tmp_path / "review_decisions.jsonl").write_text('{"key":"original-review-key"}\n')
    decisions = (tmp_path / "review_decisions.jsonl").read_bytes()
    original_layout = layout_path.read_bytes()
    result = rebuild_review_layouts(tmp_path)
    assert result["pages_updated"] == 1
    assert result["unmapped_rows"] == []
    rebuilt = layout_path.read_bytes()
    rebuild_review_layouts(tmp_path)
    assert layout_path.read_bytes() == rebuilt
    assert json.loads((tmp_path / "layout_manifest.before_tables.json").read_bytes()) == json.loads(original_layout)
    assert (tmp_path / "transcription.csv").read_bytes() == csv_bytes
    assert (tmp_path / "review_decisions.jsonl").read_bytes() == decisions


@pytest.mark.parametrize("mismatch", ["image", "row"])
def test_overrides_reject_mismatched_source_without_writing(tmp_path: Path, mismatch: str) -> None:
    image_path, layout_path = write_run(tmp_path)
    original_layout = layout_path.read_bytes()
    overrides = tmp_path / "overrides.json"
    overrides.write_text(json.dumps({"pages": [{
        "source_page": 1,
        "image_sha256": "wrong" if mismatch == "image" else hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "rows": [{"source_row_label": "N2", "source_id_text": "wrong"}],
    }]}))
    with pytest.raises(ValueError, match=f"override {mismatch} mismatch"):
        rebuild_review_layouts(tmp_path, overrides_path=overrides)
    assert layout_path.read_bytes() == original_layout


def test_prose_override_does_not_invent_table_columns(tmp_path: Path) -> None:
    image_path, layout_path = write_run(tmp_path)
    overrides = tmp_path / "overrides.json"
    overrides.write_text(json.dumps({"pages": [{
        "source_page": 1,
        "image_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "columns": [],
        "rows": [{
            "source_row_label": "N2", "source_id_text": "N2|ILEOPA|1",
            "box": {"x": 1200, "y": 2300, "width": 800, "height": 100},
        }],
    }]}))
    result = rebuild_review_layouts(tmp_path, overrides_path=overrides)
    assert not result["unmapped_rows"]
    table = json.loads(layout_path.read_text())["pages"][0]["tables"][-1]
    assert table["columns"] == []
    assert table["rows"][0]["box"]["x"] == 1200
