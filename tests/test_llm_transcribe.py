from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from forestcensus.llm_transcribe import (
    DEFAULT_MODEL,
    PageTranscription,
    PortraitMainRowTranscription,
    PortraitPageTranscription,
    PortraitRecruitRowTranscription,
    RowTranscription,
    _column_name,
    _contains_forbidden_key,
    _load_datasheet_manifest_rows,
    _load_handwriting_contexts,
    _notes_with_species_update,
    _page_to_records,
    _parse_page_selection,
    _plot_from_title,
    _resolve_datasheet_format,
    _review_flags,
    _uses_latest_gemini_config,
    _transcribe_page,
    _write_csvs,
    materialize_llm_review,
    parse_tree_id,
    rematerialize_portrait_run,
)


def test_parse_tree_id_splits_printed_identifier() -> None:
    assert parse_tree_id("Ace.rub.929.1") == {
        "genus": "Ace",
        "spp": "rub",
        "tree_number": "929",
        "trunk_number": "1",
    }


def test_plot_from_title_extracts_brownsville_plot_suffix() -> None:
    assert _plot_from_title("BRNV.R1") == "R1"
    assert _plot_from_title("(BRNV.R2)") == "R2"
    assert _plot_from_title("BRNV R3") == "R3"


def test_may_2026_auto_selects_portrait_datasheet() -> None:
    assert _resolve_datasheet_format("auto", "May_2026") == "portrait_2026"
    assert _resolve_datasheet_format("auto", "October_2025") == "legacy"


def test_latest_gemini_models_do_not_use_deprecated_sampling_config() -> None:
    assert DEFAULT_MODEL == "gemini-3.8-flash"
    assert _uses_latest_gemini_config("gemini-3.8-flash")
    assert _uses_latest_gemini_config("gemini-3.7-flash")
    assert _uses_latest_gemini_config("gemini-3.6-flash")
    assert not _uses_latest_gemini_config("gemini-3.1-pro-preview")


def test_gemini38_request_preserves_usage_without_changing_transcription(tmp_path):
    from google.genai import types
    from PIL import Image

    image = tmp_path / "page.png"
    Image.new("RGB", (10, 10), "white").save(image)
    page = PortraitPageTranscription(page_title="BRNV R4", plot="R4")
    requests = []

    def generate(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(text=page.model_dump_json(), model_version="gemini-3.8-flash",
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=2000, candidates_token_count=1000, thoughts_token_count=500,
                total_token_count=3500))

    usage_path = tmp_path / "usage" / "page_011.json"
    result = _transcribe_page(SimpleNamespace(models=SimpleNamespace(generate_content=generate)), image,
        model=DEFAULT_MODEL, media_resolution="MEDIA_RESOLUTION_HIGH", handwriting_contexts=[],
        datasheet_format="portrait_2026", usage_path=usage_path)
    assert result == page
    request = requests[0]
    assert request["model"] == "gemini-3.8-flash"
    assert request["config"].thinking_config.thinking_level == types.ThinkingLevel.HIGH
    assert request["config"].temperature is None
    assert json.loads(usage_path.read_text())["usage"]["thoughts_token_count"] == 500


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


def test_materialize_llm_review_applies_latest_field_edits(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    transcription = run_dir / "transcription.csv"
    transcription.write_text(
        "\n".join(
            [
                "survey_id,date,site,zone,plot,tree_number,tree_code,trunk_number,genus,spp,dbh_mm,health,standing,poison_ivy,notes,source_page,source_row,source_row_label,source_id_text,source_page_title,source_image,source_json,transcription_flags,review_flags",
                "October_2025,2025-10-09,BRNV,R,R1,929,R1_929_Ace,1,Ace,rub,430,8,0,0,,1,1,2,Ace.rub.929.1,BRNV.R1,page.png,page.json,,",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "review_decisions.jsonl").write_text(
        "\n".join(
            [
                '{"key":"1:1:Ace.rub.929.1","action":"edit","chosen_field":"health","chosen_value":"7","decided_at":"2026-05-06T10:00:00Z"}',
                '{"key":"1:1:Ace.rub.929.1","action":"edit","chosen_field":"health","chosen_value":"9","decided_at":"2026-05-06T11:00:00Z"}',
                '{"key":"1:1:Ace.rub.929.1","action":"edit","chosen_field":"standing","chosen_value":"1","decided_at":"2026-05-06T11:05:00Z"}',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "rejected_pages.json").write_text("[]\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        f'{{"name":"test review","dirs":["{run_dir}"]}}\n',
        encoding="utf-8",
    )

    summary = materialize_llm_review(manifest, tmp_path / "reviewed")

    assert summary["decisions_loaded"] == 3
    assert summary["edits_deduped"] == 2
    assert summary["edits_applied"] == 2
    reviewed = (tmp_path / "reviewed" / "import_recent_format_reviewed.csv").read_text(
        encoding="utf-8"
    )
    assert "430,9,,," in reviewed
    assert ",1,,0" in reviewed


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


def test_review_flags_call_out_dead_health_without_standing() -> None:
    row = RowTranscription.model_validate(
        {
            "row_label": "32",
            "id_text": "Uni.spp.963.1",
            "health_observed": 0,
        }
    )
    assert _review_flags(row) == [
        "measurement_without_standing",
        "dead_health_without_standing",
    ]


def test_load_handwriting_profile_resolves_project_relative_examples(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    image = tmp_path / "assets" / "handwriting" / "juan.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"not really a png")
    (config_dir / "handwriting_profiles.toml").write_text(
        """
[profiles.juan]
description = "left is 7, right is 1"
examples = ["assets/handwriting/juan.png"]
""",
        encoding="utf-8",
    )

    contexts = _load_handwriting_contexts(config_dir, ["juan"], [])

    assert len(contexts) == 1
    assert contexts[0].name == "juan"
    assert contexts[0].examples == (image,)


def test_portrait_manifest_rows_are_authoritative_for_existing_trees(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    (manifest_dir / "BRNV_R1.json").write_text(
        """
{
  "plot": "R1",
  "row_pages": [[
    {"row": "1", "tag": "929", "spp": "ACERUB", "stem": "1", "reference_dbh": "430"},
    {"row": "2", "tag": "930", "spp": "ILEOPA", "stem": "1", "reference_dbh": "129"}
  ]]
}
""",
        encoding="utf-8",
    )
    manifest_rows = _load_datasheet_manifest_rows(manifest_dir)
    page = PortraitPageTranscription(
        page_title="BRNV R1",
        plot="R1",
        field_date="2026/05/12",
        main_rows=[
            PortraitMainRowTranscription(
                row_label="1",
                tag_text="928",
                species_text="ACERUB",
                stem_text="1/1",
                health_observed=9,
                standing_observed=True,
                species_update="ILEOPA",
            ),
            PortraitMainRowTranscription(
                row_label="2",
                tag_text="930",
                species_text="ILEOPA",
                stem_text="1",
            ),
        ],
        newly_tracked_rows=[
            PortraitRecruitRowTranscription(
                row_label="N1",
                tag_text="7001",
                species_text="PINTAE",
                stem_text="1/2",
                dbh_mm=52,
                health_observed=8,
                standing_observed=True,
            )
        ],
    )

    records = _page_to_records(
        page,
        page_number=1,
        image_path=tmp_path / "page.png",
        raw_json_path=tmp_path / "page.json",
        survey_id="May_2026",
        survey_date=date(2026, 5, 12),
        manifest_rows=manifest_rows,
    )

    assert len(records) == 3
    assert records[0]["tree_number"] == "929"
    assert records[0]["dbh_mm"] is None
    assert records[0]["identity_source"] == "datasheet_manifest"
    assert "manifest_identity_mismatch" in records[0]["review_flags"]
    assert records[0]["species_update"] == "ILEOPA"
    assert records[0]["notes"] == ""
    assert records[1]["tree_number"] == "930"
    assert records[1]["health"] is None
    assert records[1]["alive"] == "0"
    assert records[2]["section"] == "newly_tracked"
    assert records[2]["tree_number"] == "7001"
    assert records[2]["trunk_number"] == "1"
    assert records[2]["genus"] == "Pin"
    assert records[2]["spp"] == "tae"
    assert records[2]["dbh_mm"] == 52

    transcription_csv = tmp_path / "transcription.csv"
    import_csv = tmp_path / "import.csv"
    review_csv = tmp_path / "review.csv"
    _write_csvs(records, transcription_csv, import_csv, review_csv)
    import_text = import_csv.read_text(encoding="utf-8")
    assert "species update: ILEOPA" in import_text


def test_handwritten_main_extension_is_materialized_as_newly_tracked(tmp_path: Path) -> None:
    page = PortraitPageTranscription(
        page_title="BRNV H5",
        plot="H5",
        main_rows=[
            PortraitMainRowTranscription(
                row_label="26",
                tag_text="551",
                species_text="ILEOPA",
                stem_text="1",
                health_observed=9,
                standing_observed=True,
                flags=["handwritten_row_added"],
            )
        ],
    )

    records = _page_to_records(
        page,
        page_number=19,
        image_path=tmp_path / "page.png",
        raw_json_path=tmp_path / "page.json",
        survey_id="May_2026",
        survey_date=date(2026, 5, 12),
        manifest_rows={},
    )

    assert len(records) == 1
    assert records[0]["section"] == "newly_tracked"
    assert records[0]["identity_source"] == "newly_tracked_handwriting"
    assert "handwritten_main_extension" in records[0]["review_flags"]
    assert "manifest_row_not_found" not in records[0]["review_flags"]


@pytest.mark.parametrize("with_addition", [False, True])
@pytest.mark.parametrize("parent_note", [False, True])
def test_rematerialize_portrait_run_uses_saved_json_and_new_manifest(tmp_path: Path, with_addition: bool, parent_note: bool) -> None:
    source_run = tmp_path / "source"
    raw_dir = source_run / "raw_json"
    raw_dir.mkdir(parents=True)
    (source_run / "pages").mkdir()
    (source_run / "run_metadata.json").write_text(
        """{
  "datasheet_format": "portrait_2026",
  "model": "gemini-3.7-flash",
  "pages": [1],
  "pdf": "scan.pdf",
  "survey_id": "May_2026"
}
""",
        encoding="utf-8",
    )
    (source_run / "layout_manifest.json").write_text('{"pages": []}\n', encoding="utf-8")
    (source_run / "rejected_pages.json").write_text("[]\n", encoding="utf-8")
    page = PortraitPageTranscription(
        page_title="BRNV R1",
        plot="R1",
        problems_and_info="100-JUN-1-NA-0-std-previously tagged",
        main_rows=[
            PortraitMainRowTranscription(
                row_label="1",
                tag_text="929",
                species_text="ACERUB",
                stem_text="1",
                health_observed=8,
                standing_observed=True,
                notes="2nd stem dead standing" if parent_note else "",
            )
        ],
    )
    (raw_dir / "page_001.json").write_text(
        page.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    original_json = (raw_dir / "page_001.json").read_bytes()
    additions_path = tmp_path / "additions.json"
    additions = {
        "survey_id": "May_2026",
        "pages": [{
            "source_page": 1,
            "plot": "R1",
            "source_json_sha256": hashlib.sha256(original_json).hexdigest(),
            "source_text": "2nd stem dead standing" if parent_note else page.problems_and_info,
            **({"source_row_label": "1"} if parent_note else {}),
            "newly_tracked_rows": [{
                "row_label": "notes-1", "tag_text": "100", "species_text": "JUN",
                "stem_text": "1", "health_observed": 0, "standing_observed": True,
                "notes": "previously tagged",
            }],
        }],
    }
    additions_path.write_text(json.dumps(additions))
    manifest_dir = tmp_path / "manifest"
    manifest_dir.mkdir()
    (manifest_dir / "BRNV_R1.json").write_text(
        """{
  "plot": "R1",
  "row_pages": [[
    {"row": "1", "tag": "930", "spp": "ILEOPA", "stem": "1"}
  ]]
}
""",
        encoding="utf-8",
    )

    result = rematerialize_portrait_run(
        source_run,
        output_dir=tmp_path / "rematerialized",
        datasheet_manifest_dir=manifest_dir,
        page_additions_path=additions_path if with_addition else None,
    )

    output = pd.read_csv(result.transcription_csv, dtype="string", keep_default_na=False)
    assert result.rows == (2 if with_addition else 1)
    assert output.loc[0, "tree_number"] == "930"
    assert output.loc[0, "genus"] == "Ile"
    assert output.loc[0, "identity_source"] == "datasheet_manifest"
    assert "manifest_identity_mismatch" in output.loc[0, "review_flags"]
    assert result.layout_manifest.exists()
    if with_addition:
        added = output.iloc[1]
        assert added["tree_number"] == "100"
        assert added["genus"] == "Jun"
        assert added["spp"] == ""
        assert added["health"] == "0"
        assert added["standing"] == "1"
        assert added["dbh_mm"] == added["poison_ivy"] == ""
        assert added["section"] == "newly_tracked"
        assert added["source_row"] == "2"
        assert added["source_json"] == str(additions_path)
        assert added["identity_source"] == "reviewed_page_note"
        first_output = result.transcription_csv.read_bytes()
        # A normal rebuild must remember additions and never append them twice.
        rematerialize_portrait_run(source_run, output_dir=result.output_dir, datasheet_manifest_dir=manifest_dir)
        assert result.transcription_csv.read_bytes() == first_output
        assert (raw_dir / "page_001.json").read_bytes() == original_json
        if parent_note:
            additions["pages"][0]["source_row_label"] = "missing"
            additions_path.write_text(json.dumps(additions))
            with pytest.raises(ValueError, match="parent row mismatch"):
                rematerialize_portrait_run(source_run, output_dir=result.output_dir, datasheet_manifest_dir=manifest_dir)
            additions["pages"][0]["source_row_label"] = "1"
        additions["pages"][0]["source_json_sha256"] = "wrong"
        additions_path.write_text(json.dumps(additions))
        with pytest.raises(ValueError, match="source mismatch"):
            rematerialize_portrait_run(source_run, output_dir=result.output_dir, datasheet_manifest_dir=manifest_dir)
        assert result.transcription_csv.read_bytes() == first_output


def test_portrait_layout_column_names_distinguish_printed_context() -> None:
    assert _column_name(8, 12, "portrait_2026") == "printed_dbh"
    assert _column_name(11, 12, "portrait_2026") == "species_update"
    assert _column_name(5, 9, "portrait_2026") == "dbh_mm"


@pytest.mark.parametrize("update, expected", [("NA", ""), (" N/A ", ""), ("n/a", ""), ("", ""), ("ILEOPA", "ILEOPA")])
def test_portrait_species_update_na_means_no_change(tmp_path: Path, update: str, expected: str) -> None:
    row = PortraitMainRowTranscription(
        row_label="1", tag_text="5218", species_text="NYSSYL", stem_text="1",
        health_observed=0, standing_observed=True, species_update=update,
        notes="DBH NA; standing dead",
    )
    page = PortraitPageTranscription(page_title="BRNV R4", plot="R4", main_rows=[row])
    record = _page_to_records(
        page, page_number=8, image_path=tmp_path / "page.png",
        raw_json_path=tmp_path / "page.json", survey_id="May_2026",
        survey_date=date(2026, 5, 12), manifest_rows={},
    )[0]
    assert record["species_update"] == expected
    assert ("species_update_present" in record["review_flags"]) == bool(expected)
    assert record["notes"] == "DBH NA; standing dead"
    assert record["health"] == 0
    assert record["dbh_mm"] is None
    assert row.species_update == update.strip()
    expected_notes = f"{row.notes}; species update: {expected}" if expected else row.notes
    assert _notes_with_species_update(row.notes, update) == expected_notes


def test_approved_r4_note_additions_preserve_unspecified_fields(tmp_path: Path) -> None:
    config_path = Path(__file__).parents[1] / "config/may_2026_transcription_additions.json"
    addition = next(p for p in json.loads(config_path.read_text())["pages"] if p["source_page"] == 8)
    rows = [PortraitRecruitRowTranscription.model_validate(r) for r in addition["newly_tracked_rows"]]
    page = PortraitPageTranscription(page_title="BRNV R4", plot="R4", newly_tracked_rows=rows)
    records = _page_to_records(
        page, page_number=8, image_path=tmp_path / "page.png",
        raw_json_path=tmp_path / "page.json", survey_id="May_2026",
        survey_date=date(2026, 5, 12), manifest_rows={},
    )
    by_tag = {r["tree_number"]: r for r in records}
    assert len(records) == len(by_tag) == 11
    assert {tag: r["health"] for tag, r in by_tag.items()} == {
        "5218": 0, "735": 4, "5253": 6, "5250": 4, "5251": 4,
        "5264": 2, "5246": 0, "5263": 7, "5262": 5, "5260": 7, "5247": 4,
    }
    assert all(r["dbh_mm"] is None for r in records)
    assert all(r["trunk_number"] == "" for tag, r in by_tag.items() if tag != "5247")
    assert by_tag["5253"]["genus"] == by_tag["5253"]["spp"] == ""
    assert by_tag["5263"]["standing"] == ""
    assert by_tag["5262"]["standing"] == ""
    assert by_tag["5247"]["trunk_number"] == "2"
    assert by_tag["5247"]["standing"] == "1"
    assert by_tag["5247"]["poison_ivy"] == "0"
    assert "5163" not in by_tag and "5243" not in by_tag
