from __future__ import annotations

import pandas as pd

from forestcensus.datasheets import build_datasheet_prep, build_plot_datasheets


def test_datasheet_prep_uses_direct_found_signal_rule() -> None:
    census = pd.DataFrame(
        [
            _row("April_2025", "1", stem_rank=1),
            _row("October_2025", "2", stem_rank=1, standing_observed=True),
            _row("October_2025", "3", stem_rank=1, health_observed=0),
            _row("October_2025", "4", stem_rank=1, dbh_mm=55),
        ]
    )

    frames = build_datasheet_prep(census)
    active = frames["active_stems_found_last2"]

    assert set(active["tag"]) == {"2", "3", "4"}
    assert frames["summary"]["found_recent_rows"] == 3


def test_datasheet_prep_excludes_active_stems_that_never_qualified() -> None:
    census = pd.DataFrame(
        [
            _row("June_2023", "5", stem_rank=1, dbh_mm=55, health_observed=5),
            _row("October_2025", "5", stem_rank=1, dbh_mm=45, health_observed=0),
            _row("October_2025", "6", stem_rank=1, dbh_mm=19, health_observed=0),
            _row(
                "October_2025",
                "7",
                stem_rank=1,
                dbh_mm=49,
                health_observed=0,
                genus="Morella",
                species="cerifera",
                taxon_code="MORCER",
            ),
            _row(
                "October_2025",
                "8",
                stem_rank=1,
                dbh_mm=50,
                health_observed=0,
                genus="Morella",
                species="cerifera",
                taxon_code="MORCER",
            ),
        ]
    )

    frames = build_datasheet_prep(census)
    active = frames["active_stems_found_last2"]
    excluded = frames["excluded_nonqualifying_stems"]

    assert set(active["tag"]) == {"5", "8"}
    assert excluded["tag"].tolist() == ["6", "7"]
    assert frames["summary"]["active_stems_before_threshold_filter"] == 4
    assert frames["summary"]["excluded_nonqualifying_stems"] == 2


def test_datasheet_prep_filters_duplicate_dbh_report_after_threshold_scrub() -> None:
    census = pd.DataFrame(
        [
            _row("October_2025", "7", stem_rank=1, dbh_mm=55, health_observed=5),
            _row("October_2025", "7", stem_rank=2, dbh_mm=19, health_observed=0),
            _row("October_2025", "7", stem_rank=3, dbh_mm=19, health_observed=0),
        ]
    )

    frames = build_datasheet_prep(census)

    assert frames["active_stems_found_last2"]["stem"].tolist() == ["1"]
    assert frames["excluded_nonqualifying_stems"]["stem"].tolist() == ["2", "3"]
    assert frames["same_survey_same_tag_duplicate_dbh"].empty


def test_datasheet_prep_uses_fixed_recent_survey_hsp_slots() -> None:
    census = pd.DataFrame(
        [
            _row("April_2025", "8", stem_rank=1, dbh_mm=55, health_observed=5, standing_observed=True),
            _row("October_2025", "8", stem_rank=1),
            _row("April_2025", "9", stem_rank=1),
            _row("October_2025", "9", stem_rank=1, health_observed=6, standing_observed=True),
        ]
    )

    frames = build_datasheet_prep(census)
    active = frames["active_stems_found_last2"].set_index("tag")

    assert active.loc["8", "dhs_1"] == ""
    assert active.loc["8", "dhs_2"] == "55/5/1"
    assert active.loc["9", "dhs_1"] == "NA/6/1"
    assert active.loc["9", "dhs_2"] == ""


def test_build_plot_datasheets_uses_unknown_difficulty_and_plot_counts() -> None:
    active = pd.DataFrame(
        [
            {
                "plot": "L0",
                "tree_uid": "uid-10",
                "tag": "10",
                "identity_tag": "10",
                "stem": "1",
                "spp_latest": "JUNVIR",
                "dhs_1": "NA/4/1",
                "dhs_2": "55/5/1",
                "latest_health": 4,
                "latest_notes": "poison ivy",
            },
            {
                "plot": "L0",
                "tree_uid": "uid-10",
                "tag": "10",
                "identity_tag": "10",
                "stem": "2",
                "spp_latest": "JUNVIR",
                "dhs_1": "NA/0/1",
                "dhs_2": "65/0/1",
                "latest_health": 0,
                "latest_notes": "",
            },
        ]
    )

    payloads = build_plot_datasheets(active)
    payload = payloads["L0"]

    assert payload["difficulty"] == "NA/unknown"
    assert payload["tree_count"] == 1
    assert payload["living_count"] == 1
    assert payload["species_count"] == 1
    assert payload["existing_tags"] == ["10"]
    assert payload["rows"][0]["note_hint"] == ""
    assert payload["row_pages"] == [payload["rows"]]
    assert payload["supplement_on_last_main_page"] is True
    assert payload["total_pages"] == 1


def _row(
    survey_id: str,
    tag: str,
    *,
    stem_rank: int,
    dbh_mm: float | None = None,
    health_observed: float | None = None,
    standing_observed: bool | None = None,
    genus: str = "Juniperus",
    species: str = "virginiana",
    taxon_code: str = "JUNVIR",
) -> dict[str, object]:
    return {
        "survey_id": survey_id,
        "date": "2025-10-09",
        "site": "BRNV",
        "zone": "L",
        "plot": "L0",
        "tree_uid": f"uid-{tag}",
        "public_tag": tag,
        "identity_tag": tag,
        "identity_label": f"L0/{tag}",
        "tree_number": tag,
        "stem_rank": stem_rank,
        "datasheet_slot": str(stem_rank),
        "genus": genus,
        "species": species,
        "taxon_code": taxon_code,
        "dbh_mm": dbh_mm,
        "health_observed": health_observed,
        "alive_observed": None,
        "standing_observed": standing_observed,
        "field_status": "unknown",
        "interpreted_status": "missing_pending",
        "alive_interpreted": None,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "source_row": int(tag),
        "notes": "",
        "correction_notes": "",
    }
