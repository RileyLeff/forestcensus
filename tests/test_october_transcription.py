from datetime import date
import json
import csv
from pathlib import Path

import pytest

from forestcensus.llm_transcribe import (
    PORTRAIT_FORMAT, PortraitPageTranscription, _load_datasheet_manifest_rows,
    _page_to_metadata, _page_to_records, _resolve_datasheet_format, _resolve_manifest_dir,
)
from forestcensus.transcription_packet import load_packet_context, validate_packet_page


def context():
    return {"plot": "R4", "main_rows": [{"row": "3"}], "newly_tracked_labels": [f"N{i}" for i in range(1, 13)],
            "rechecks": [{"number": 1, "id": "r4-stems", "tags": ["5262"], "question": "How many stems?"}],
            "field_notes": [{"note_number": 1, "text": "Aliases 5163 and 5243"}], "has_difficulty": False}


def page():
    return PortraitPageTranscription(page_title="BRNV R4", plot="R4", observer="Riley",
        main_rows=[{"row_label": "3", "tag_text": "5163+", "species_text": "ACERUB", "stem_text": "1/3"}],
        newly_tracked_rows=[{"row_label": "N12", "tag_text": "6000", "species_text": "VACSPP", "dbh_mm": 22}],
        recheck_answers=[{"question_number": 1, "answer": "Two, small stem fallen"}],
        field_note_feedback=[{"note_number": 1, "helpful": True, "incorrect": True, "handwritten_notes": "tag still attached"}],
        other_handwriting="Margin: tag unreadable")


def test_october_auto_requires_explicit_packet():
    assert _resolve_datasheet_format("auto", "October_2026") == PORTRAIT_FORMAT
    with pytest.raises(ValueError, match="exact printed packet"):
        _resolve_manifest_dir(None, PORTRAIT_FORMAT, "October_2026")


def test_flat_and_paginated_manifests_are_equivalent(tmp_path):
    path = tmp_path / "BRNV_R4.json"
    row = {"row": 3, "tag": "5163+", "spp": "ACERUB", "stem": "1/3"}
    path.write_text(json.dumps({"plot": "R4", "row_pages": [[row]]}))
    old = _load_datasheet_manifest_rows(tmp_path)
    path.write_text(json.dumps({"plot": "R4", "rows": [row], "row_pages": [[row]]}))
    assert _load_datasheet_manifest_rows(tmp_path) == old
    assert old[("R4", "3")]["tag"] == "5163"


def test_metadata_is_preserved_without_becoming_observations():
    kwargs = dict(page_number=11, image_path=Path("scan.png"), raw_json_path=Path("raw.json"),
                  survey_id="October_2026", survey_date=date(2026, 10, 4))
    p = page()
    validate_packet_page(p, context())
    metadata = _page_to_metadata(p, **kwargs, page_context=context())
    answer = json.loads(metadata["recheck_answers"])[0]
    assert answer["id"] == "r4-stems"
    assert answer["answer"] == "Two, small stem fallen"
    assert json.loads(metadata["field_note_feedback"])[0]["confusing"] is None
    rows = _page_to_records(p, **kwargs, manifest_rows={})
    assert len(rows) == 2
    assert rows[0]["dbh_mm"] is None
    assert rows[0]["health"] is None
    assert rows[0]["standing"] == ""
    assert rows[1]["source_row_label"] == "N12"
    assert rows[1]["dbh_mm"] == 22


def test_review_materialization_keeps_page_evidence_separate(tmp_path):
    from forestcensus.llm_transcribe import _write_csvs, _write_page_metadata, materialize_llm_review

    run = tmp_path / "run"
    run.mkdir()
    kwargs = dict(page_number=11, image_path=Path("scan.png"), raw_json_path=Path("raw.json"),
                  survey_id="October_2026", survey_date=date(2026, 10, 4))
    rows = _page_to_records(page(), **kwargs, manifest_rows={})
    metadata = _page_to_metadata(page(), **kwargs, page_context=context())
    _write_csvs(rows, run / "transcription.csv", run / "import.csv", run / "review.csv")
    _write_page_metadata([metadata], run / "page_metadata.csv")
    selection = tmp_path / "selection.json"
    selection.write_text(json.dumps({"dirs": [str(run)]}))
    summary = materialize_llm_review(selection, tmp_path / "reviewed")
    assert summary["rows_loaded"] == 2
    assert summary["page_metadata_rows"] == 1
    with Path(summary["page_metadata_csv"]).open() as source:
        result = list(csv.DictReader(source))[0]
    assert result["recheck_answers"] == metadata["recheck_answers"]
    assert result["field_note_feedback"] == metadata["field_note_feedback"]
    assert result["source_run_dir"] == str(run)


@pytest.mark.parametrize("change,match", [
    ({"plot": "H4"}, "Expected plot"), ({"main_rows": []}, "row coverage"),
    ({"recheck_answers": []}, "question coverage"), ({"difficulty": "easy"}, "historical difficulty"),
    ({"newly_tracked_rows": [{"row_label": "N13"}]}, "slot labels"),
    ({"field_note_feedback": [{"note_number": 2}]}, "note identity"),
    ({"field_note_feedback": []}, "note identity"),
    ({"page_title": "BRNV H4"}, "Page heading"),
])
def test_packet_checks_reject_wrong_or_missing_sections(change, match):
    p = PortraitPageTranscription.model_validate({**page().model_dump(), **change})
    with pytest.raises(ValueError, match=match):
        validate_packet_page(p, context())


def test_scan_map_is_content_guarded(tmp_path):
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(b"changed scan")
    pdf.with_suffix(".manifest.json").write_text(json.dumps({"sha256": "wrong"}))
    with pytest.raises(ValueError, match="audited page map"):
        load_packet_context(pdf, tmp_path, "October_2026")


def test_missing_october_scan_map_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="audited .manifest"):
        load_packet_context(tmp_path / "scan.pdf", tmp_path, "October_2026")


def test_billing_failure_stops_requests_and_persists_incomplete_run(tmp_path, monkeypatch):
    from PIL import Image
    from google import genai
    from forestcensus import llm_transcribe as module

    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(b"test")
    image = tmp_path / "page.png"
    Image.new("L", (10, 10), "white").save(image)
    monkeypatch.setattr(module, "_pdf_page_count", lambda _: 2)
    monkeypatch.setattr(module, "_render_pages", lambda *_: {1: image, 2: image})
    monkeypatch.setattr(module, "_write_review_crops", lambda *_, **__: None)
    monkeypatch.setattr(module, "_load_gemini_api_key", lambda: "test-key")
    monkeypatch.setattr(genai, "Client", lambda **_: object())
    calls = []

    class BillingError(Exception):
        code = 402

    def fail(*_, **__):
        calls.append(1)
        raise BillingError("credits depleted")

    monkeypatch.setattr(module, "_transcribe_page", fail)
    result = module.transcribe_pdf(pdf, survey_id="May_2026", datasheet_manifest_dir=tmp_path,
                                   output_dir=tmp_path / "run", pages="all")
    assert len(calls) == 1
    assert result.rejected_pages == 2
    assert json.loads(result.run_metadata.read_text())["status"] == "incomplete"
    assert "Not attempted" in json.loads(result.rejected_json.read_text())[1]["error"]
    assert len(json.loads(result.layout_manifest.read_text())["pages"]) == 2
    with pytest.raises(ValueError, match="Run already exists"):
        module.transcribe_pdf(pdf, survey_id="May_2026", datasheet_manifest_dir=tmp_path, output_dir=tmp_path / "run")
