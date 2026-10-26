from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from forestcensus.assembly import assemble_events
from forestcensus.config import load_config


def _events(rows: list[dict]) -> pd.DataFrame:
    base = {
        "source_file": "test.csv",
        "source_row": 2,
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "datasheet_slot": "1",
        "genus": "Pinus",
        "species": "taeda",
        "taxon_code": "PINTAE",
        "dbh_mm": None,
        "health_observed": None,
        "alive_observed": None,
        "standing_observed": None,
        "notes": "",
        "correction_notes": "",
        "origin": "test",
    }
    return pd.DataFrame([{**base, **row} for row in rows])


def test_consecutive_not_found_becomes_inferred_dead() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "field_status": "observed_alive", "dbh_mm": 100, "health_observed": 8},
            {"survey_id": "June_2022", "date": date(2022, 6, 16), "field_status": "not_found"},
            {"survey_id": "June_2023", "date": date(2023, 6, 16), "field_status": "not_found"},
        ]
    )
    assembled = assemble_events(events, config)
    missing = assembled.loc[assembled["field_status"].eq("not_found")]
    assert set(missing["interpreted_status"]) == {"inferred_dead"}


def test_rediscovery_rolls_inferred_death_back_to_missing() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "field_status": "observed_alive", "dbh_mm": 100, "health_observed": 8},
            {"survey_id": "June_2022", "date": date(2022, 6, 16), "field_status": "not_found"},
            {"survey_id": "June_2023", "date": date(2023, 6, 16), "field_status": "not_found"},
            {"survey_id": "May_2024", "date": date(2024, 5, 21), "field_status": "observed_alive", "dbh_mm": 105, "health_observed": 8},
        ]
    )
    assembled = assemble_events(events, config)
    missing = assembled.loc[assembled["field_status"].eq("not_found")]
    assert set(missing["interpreted_status"]) == {"missing_pending"}


def test_zombie_requires_observed_dead_then_observed_alive() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "field_status": "observed_dead", "health_observed": 0},
            {"survey_id": "June_2022", "date": date(2022, 6, 16), "field_status": "observed_alive", "dbh_mm": 100, "health_observed": 8},
        ]
    )
    assembled = assemble_events(events, config)
    assert assembled["zombie_ever"].all()


def test_stem_rank_is_derived_from_dbh_not_datasheet_slot() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 2, "datasheet_slot": "1", "dbh_mm": 80, "health_observed": 8, "field_status": "observed_alive"},
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 3, "datasheet_slot": "2", "dbh_mm": 120, "health_observed": 8, "field_status": "observed_alive"},
        ]
    )
    assembled = assemble_events(events, config)
    by_slot = assembled.set_index("datasheet_slot")["stem_rank"].to_dict()
    assert by_slot["2"] == 1
    assert by_slot["1"] == 2


def test_identity_tag_not_public_tag_controls_tree_uid() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {"survey_id": "June_2021", "date": date(2021, 6, 15), "public_tag": "112", "identity_tag": "112", "dbh_mm": 100, "health_observed": 8, "field_status": "observed_alive"},
            {"survey_id": "June_2022", "date": date(2022, 6, 16), "public_tag": "508", "identity_tag": "112", "tree_number": "508", "dbh_mm": 103, "health_observed": 8, "field_status": "observed_alive"},
        ]
    )
    assembled = assemble_events(events, config)
    assert assembled["public_tag"].nunique() == 2
    assert assembled["tree_uid"].nunique() == 1


def test_non_morella_tree_qualifies_at_twenty_mm() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "field_status": "observed_alive",
                "dbh_mm": 20,
                "health_observed": 8,
            },
            {
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "field_status": "observed_alive",
                "dbh_mm": 22,
                "health_observed": 8,
            },
        ]
    )

    assembled = assemble_events(events, config)

    assert len(assembled) == 2


def test_morella_cerifera_requires_fifty_mm_to_qualify() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "field_status": "observed_alive",
                "genus": "Morella",
                "species": "cerifera",
                "taxon_code": "MORCER",
                "dbh_mm": 42,
                "health_observed": 8,
            },
            {
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "field_status": "observed_alive",
                "genus": "Morella",
                "species": "cerifera",
                "taxon_code": "MORCER",
                "dbh_mm": 49,
                "health_observed": 8,
            },
        ]
    )

    assembled = assemble_events(events, config)

    assert assembled.empty


def test_below_threshold_rows_remain_when_tree_has_qualifying_history() -> None:
    config = load_config(Path("config"))
    events = _events(
        [
            {
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "field_status": "observed_alive",
                "dbh_mm": 60,
                "health_observed": 8,
            },
            {
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "field_status": "observed_dead",
                "dbh_mm": 42,
                "health_observed": 0,
            },
        ]
    )

    assembled = assemble_events(events, config)

    assert len(assembled) == 2
    assert set(assembled["dbh_mm"]) == {42, 60}
