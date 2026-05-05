from __future__ import annotations

from pathlib import Path

import pytest

from forestcensus.llm_transcribe import (
    PageTranscription,
    RowTranscription,
    _contains_forbidden_key,
    _parse_page_selection,
    _review_flags,
    _write_csvs,
    parse_tree_id,
)


def test_parse_tree_id_splits_printed_identifier() -> None:
    assert parse_tree_id("Ace.rub.929.1") == {
        "genus": "Ace",
        "spp": "rub",
        "tree_number": "929",
        "trunk_number": "1",
    }


def test_page_schema_rejects_unexpected_row_fields() -> None:
    with pytest.raises(ValueError):
        PageTranscription.model_validate(
            {
                "page_title": "BRNV.R1",
                "plot": "R1",
                "rows": [
                    {
                        "row_label": "2",
                        "id_text": "Ace.rub.929.1",
                        "health_observed": 8,
                        "dhas_1": "430/10/1/1",
                    }
                ],
            }
        )


def test_forbidden_key_detection_catches_dhas_variants() -> None:
    assert _contains_forbidden_key({"rows": [{"dhas.1": "430/10/1/1"}]})
    assert not _contains_forbidden_key({"rows": [{"notes": "poison ivy"}]})


def test_parse_page_selection_supports_ranges_and_all() -> None:
    assert _parse_page_selection("1,3-4", 10) == [1, 3, 4]
    assert _parse_page_selection("all", 3) == [1, 2, 3]


def test_write_csvs_handles_empty_outputs(tmp_path: Path) -> None:
    transcription = tmp_path / "transcription.csv"
    import_csv = tmp_path / "import.csv"
    review_csv = tmp_path / "review.csv"
    _write_csvs([], transcription, import_csv, review_csv)
    assert transcription.exists()
    assert import_csv.exists()
    assert review_csv.exists()


def test_row_health_range_is_strict() -> None:
    with pytest.raises(ValueError):
        RowTranscription.model_validate(
            {
                "row_label": "1",
                "id_text": "Ace.rub.929.1",
                "health_observed": 11,
            }
        )


def test_review_flags_do_not_warn_on_poison_ivy_only_row() -> None:
    row = RowTranscription.model_validate(
        {
            "row_label": "32",
            "id_text": "Uni.spp.963.1",
            "poison_ivy_observed": True,
        }
    )
    assert _review_flags(row) == []


def test_review_flags_mark_notes_and_missing_health_with_dbh() -> None:
    row = RowTranscription.model_validate(
        {
            "row_label": "31",
            "id_text": "Liq.sty.962.1",
            "dbh_mm": 325,
            "standing_observed": True,
            "notes": "nys 962 with 961",
        }
    )
    assert _review_flags(row) == [
        "dbh_without_health",
        "standing_without_measurement",
        "notes_present",
    ]


def test_review_flags_ignore_missing_dbh_when_health_is_present() -> None:
    row = RowTranscription.model_validate(
        {
            "row_label": "40",
            "id_text": "Ile.opa.998.2",
            "health_observed": 4,
            "standing_observed": True,
        }
    )
    assert _review_flags(row) == []
