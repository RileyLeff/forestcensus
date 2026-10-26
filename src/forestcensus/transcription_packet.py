"""Bind scanned pages to the printed packet, never to inferred tree histories."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


def load_packet_context(pdf: Path, manifest_dir: Path | None, survey_id: str) -> dict[int, dict[str, Any]]:
    companion = pdf.with_suffix(".manifest.json")
    if not companion.exists():
        if survey_id == "October_2026":
            raise ValueError("October scans require the audited .manifest.json page map beside the PDF")
        return {}
    audit = json.loads(companion.read_text())
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != audit["sha256"]:
        raise ValueError("Scanned PDF does not match its audited page map")
    if manifest_dir is None:
        raise ValueError("An audited scan requires its printed datasheet manifest directory")
    contexts = {}
    for plot in sorted({p["plot"] for p in audit["page_map"]}):
        path = manifest_dir / f"BRNV_{plot}.json"
        packet = json.loads(path.read_text())
        if packet["survey_id"] != survey_id or packet["packet_id"] != audit["printed_packet_id"]:
            raise ValueError(f"Printed packet mismatch for {plot}")
        blank_pdf = manifest_dir.parent / "pdf" / f"BRNV_{plot}.pdf"
        pages = subprocess.run(["pdftotext", "-layout", str(blank_pdf), "-"], check=True, capture_output=True, text=True).stdout.split("\f")
        seen = []
        for mapping in (p for p in audit["page_map"] if p["plot"] == plot):
            number = int(mapping["combined_page"])
            if number in contexts:
                raise ValueError(f"Duplicate page {number} in scan map")
            printed = pages[int(mapping["plot_page"]) - 1]
            labels = re.findall(r"^\s*(\d+)\s+\d+[*+]*\s+[A-Z]{6}\b", printed, re.MULTILINE)
            rows = [r for r in packet["rows"] if str(r["row"]) in labels]
            if len(rows) != len(labels):
                raise ValueError(f"Printed row/manifest mismatch on {plot} page {mapping['plot_page']}")
            seen.extend(labels)
            contexts[number] = {
                "plot": plot, "plot_page": mapping["plot_page"], "packet_id": packet["packet_id"],
                "main_rows": [{k: r[k] for k in ("row", "tag", "spp", "stem")} for r in rows],
                "newly_tracked_labels": re.findall(r"^\s*(N\d+)\s*$", printed, re.MULTILINE),
                "rechecks": [q for q in packet.get("rechecks", []) if re.search(rf"\bQ{q['number']}\s*\|", printed)],
                # Full plot context identifies unnumbered bullets even when notes span pages.
                "field_notes": [{"note_number": i, **note} for i, note in enumerate(packet.get("field_notes", []), 1)] if "Field Notes" in printed else [],
                "has_difficulty": bool(re.search(r"^Difficulty\s", printed, re.MULTILINE)),
                "newly_tracked_slots": packet["newly_tracked_slots"],
                "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        if sorted(seen, key=int) != sorted((str(r["row"]) for r in packet["rows"]), key=int):
            raise ValueError(f"Incomplete printed main-row coverage for {plot}")
    if sorted(contexts) != list(range(1, audit["pages"] + 1)):
        raise ValueError("Incomplete scan page map")
    return contexts


def validate_packet_page(page: Any, context: dict[str, Any]) -> None:
    """Reject omissions/alignment errors; preserve ambiguous handwriting as flags."""
    if page.plot.strip().upper() != context["plot"]:
        raise ValueError(f"Expected plot {context['plot']}, model returned {page.plot}")
    title_plot = re.search(r"\b[RHML]\d\b", page.page_title.upper())
    if title_plot and title_plot.group() != context["plot"]:
        raise ValueError(f"Page heading disagrees with expected plot {context['plot']}")
    expected = [str(r["row"]) for r in context["main_rows"]]
    actual = [r.row_label.strip() for r in page.main_rows]
    if sorted(actual) != sorted(expected):
        raise ValueError(f"Main row coverage mismatch: expected {expected}, got {actual}")
    labels = [r.row_label.strip().upper() for r in page.newly_tracked_rows]
    if len(labels) != len(set(labels)) or not set(labels) <= set(context["newly_tracked_labels"]):
        raise ValueError(f"Invalid Newly Tracked slot labels: {labels}")
    numbers = [q.question_number for q in page.recheck_answers]
    if sorted(numbers) != sorted(q["number"] for q in context["rechecks"]):
        raise ValueError("Recheck question coverage mismatch")
    notes = [n.note_number for n in page.field_note_feedback]
    if sorted(notes) != sorted(n["note_number"] for n in context["field_notes"]):
        raise ValueError("Field note identity mismatch")
    if page.difficulty is not None and not context["has_difficulty"]:
        raise ValueError("Current difficulty returned on a page with only historical difficulty")
