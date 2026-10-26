from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from forestcensus.adapters import load_historical_events
from forestcensus.adapters import adapt_2024_spring
from forestcensus.adapters import adapt_2024_fall
from forestcensus.adapters import adapt_2025_spring
from forestcensus.config import load_config
from forestcensus.config import RowCorrection, RowExclusion
from forestcensus.corrections import apply_corrections
from forestcensus.errors import CorrectionMatchError, CorrectionUnsafeSelectorError


def test_historical_row_corrections_are_applied() -> None:
    config = load_config(Path("config"))
    events = load_historical_events("data/raw/forest_census", config)

    h4_swap = events.loc[
        events["survey_id"].eq("June_2021")
        & events["site"].eq("BRNV")
        & events["plot"].eq("H4")
        & events["correction_notes"].str.contains("wrong tag", regex=False)
    ]
    assert len(h4_swap) == 1
    assert h4_swap.iloc[0]["public_tag"] == "508"
    assert h4_swap.iloc[0]["identity_tag"] == "508"

    dbh_fix = events.loc[
        events["survey_id"].eq("June_2023")
        & events["plot"].eq("M5")
        & events["public_tag"].eq("2478")
        & events["correction_notes"].str.contains("450 mm", regex=False)
    ]
    assert len(dbh_fix) == 1
    assert dbh_fix.iloc[0]["dbh_mm"] == 450

    health_fix = events.loc[
        events["source_file"].eq("2024_spring.csv")
        & events["source_row"].eq(1047)
    ]
    assert len(health_fix) == 1
    assert health_fix.iloc[0]["health_observed"] == 10
    assert "R1/957 health 20" in health_fix.iloc[0]["correction_notes"]


def test_2024_spring_adapter_parses_mixed_date_formats() -> None:
    config = load_config(Path("config"))
    events = adapt_2024_spring(Path("data/raw/forest_census/2024_spring.csv"), config)

    short_year_row = events.loc[events["source_row"].eq(1152)].iloc[0]
    long_year_row = events.loc[events["source_row"].eq(1047)].iloc[0]

    assert short_year_row["date"] == date(2024, 5, 22)
    assert long_year_row["date"] == date(2024, 5, 20)


def test_species_aliases_can_depend_on_genus() -> None:
    config = load_config(Path("config"))
    fall = adapt_2024_fall(Path("data/raw/forest_census/2024_fall.csv"), config)
    spring_2025 = adapt_2025_spring(Path("data/raw/forest_census/2025_spring.csv"), config)

    liquidambar = fall.loc[fall["source_row"].eq(1231)].iloc[0]
    nyssa = spring_2025.loc[spring_2025["source_row"].eq(815)].iloc[0]
    vaccinium = fall.loc[fall["source_row"].eq(1261)].iloc[0]

    assert (liquidambar["genus"], liquidambar["species"], liquidambar["taxon_code"]) == (
        "Liquidambar",
        "styraciflua",
        "LIQSTY",
    )
    assert (nyssa["genus"], nyssa["species"], nyssa["taxon_code"]) == ("Nyssa", "sylvatica", "NYSSYL")
    assert (vaccinium["genus"], vaccinium["species"], vaccinium["taxon_code"]) == (
        "Vaccinium",
        "spp.",
        "VACSPP",
    )


def test_identity_aliases_can_decouple_public_tag_from_identity(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    for name in ["pipeline.toml", "sites.toml", "surveys.toml", "taxonomy.toml"]:
        (config_dir / name).write_text(Path("config", name).read_text(encoding="utf-8"), encoding="utf-8")
    (config_dir / "corrections.toml").write_text("", encoding="utf-8")
    (config_dir / "identity.toml").write_text(
        """
[[aliases]]
site = "BRNV"
plot = "H4"
tag = "508"
identity_tag = "112"
effective_from = "2022-01-01"
note = "Retag for test"
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    events = pd.DataFrame(
        [
            {
                "source_file": "test.csv",
                "source_row": 2,
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "site": "BRNV",
                "zone": "H",
                "plot": "H4",
                "public_tag": "508",
                "identity_tag": "508",
                "tree_number": "508",
                "datasheet_slot": "1",
                "genus": "Pinus",
                "species": "taeda",
                "taxon_code": "PINTAE",
                "dbh_mm": 100,
                "health_observed": 8,
                "alive_observed": True,
                "standing_observed": True,
                "field_status": "observed_alive",
                "notes": "",
                "correction_notes": "",
                "origin": "test",
            }
        ]
    )

    from forestcensus.identity import apply_identity_operations

    corrected = apply_identity_operations(events, config)
    assert corrected.iloc[0]["public_tag"] == "508"
    assert corrected.iloc[0]["identity_tag"] == "112"
    assert "Retag for test" in corrected.iloc[0]["correction_notes"]


def test_row_number_correction_requires_source_file_and_sanity_field() -> None:
    events = pd.DataFrame(
        [
            {
                "source_file": "test.csv",
                "source_row": 2,
                "survey_id": "June_2022",
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 8,
                "correction_notes": "",
            }
        ]
    )

    missing_file = SimpleNamespace(
        row_corrections=(
            RowCorrection(
                note="unsafe row-only correction",
                match={"source_row": 2, "plot": "H4"},
                set={"health_observed": 7},
            ),
        )
    )
    with pytest.raises(CorrectionUnsafeSelectorError, match="source_file"):
        apply_corrections(events, missing_file)

    missing_sanity = SimpleNamespace(
        row_corrections=(
            RowCorrection(
                note="unsafe provenance-only correction",
                match={"source_file": "test.csv", "source_row": 2},
                set={"health_observed": 7},
            ),
        )
    )
    with pytest.raises(CorrectionUnsafeSelectorError, match="sanity field"):
        apply_corrections(events, missing_sanity)


def test_row_correction_must_match_exactly_one_row() -> None:
    events = pd.DataFrame(
        [
            {
                "source_file": "test.csv",
                "source_row": 2,
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 8,
                "correction_notes": "",
            },
            {
                "source_file": "test.csv",
                "source_row": 3,
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 8,
                "correction_notes": "",
            },
        ]
    )
    config = SimpleNamespace(
        row_corrections=(
            RowCorrection(
                note="too broad",
                match={"plot": "H4"},
                set={"health_observed": 7},
            ),
        )
    )
    with pytest.raises(CorrectionMatchError, match="matched 2 rows"):
        apply_corrections(events, config)


def test_row_correction_cannot_change_source_provenance() -> None:
    events = pd.DataFrame(
        [
            {
                "source_file": "test.csv",
                "source_row": 2,
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 8,
                "correction_notes": "",
            }
        ]
    )
    config = SimpleNamespace(
        row_corrections=(
            RowCorrection(
                note="bad provenance mutation",
                match={"source_file": "test.csv", "source_row": 2, "plot": "H4"},
                set={"source_row": 99},
            ),
        )
    )
    with pytest.raises(CorrectionUnsafeSelectorError, match="provenance"):
        apply_corrections(events, config)


def test_row_exclusion_removes_exactly_one_matching_row() -> None:
    events = pd.DataFrame(
        [
            {
                "source_file": "test.csv",
                "source_row": 2,
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 8,
                "correction_notes": "",
            },
            {
                "source_file": "test.csv",
                "source_row": 3,
                "plot": "H4",
                "public_tag": "508",
                "health_observed": 0,
                "correction_notes": "",
            },
        ]
    )
    config = SimpleNamespace(
        row_corrections=(),
        row_exclusions=(
            RowExclusion(
                note="duplicate test row",
                match={"source_file": "test.csv", "source_row": 3, "plot": "H4"},
            ),
        ),
    )

    corrected = apply_corrections(events, config)
    assert corrected["source_row"].tolist() == [2]
