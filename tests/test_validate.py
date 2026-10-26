from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pandas as pd
import pytest

from forestcensus.config import load_config
from forestcensus.validate import IssueCode, validate_census, write_diagnostics, write_issue_context


def test_validate_reports_health_and_dbh_jump_issues() -> None:
    config = load_config(Path("config"))
    rows = []
    base = {
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "stem_rank": 1,
        "datasheet_slot": "1",
        "genus": "Pinus",
        "species": "taeda",
        "taxon_code": "PINTAE",
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "notes": "",
        "correction_notes": "",
    }
    rows.append({**base, "survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 2, "dbh_mm": 100, "health_observed": 8})
    rows.append({**base, "survey_id": "June_2022", "date": date(2022, 6, 16), "source_row": 3, "dbh_mm": 200, "health_observed": 11})

    issues = validate_census(pd.DataFrame(rows), config)
    codes = {issue.code for issue in issues}
    assert "E_HEALTH_RANGE" in codes
    assert "W_DBH_JUMP" in codes
    assert "W_TREE_RANKED_DBH_JUMP" in codes


def test_issue_context_writes_surrounding_tree_history(tmp_path: Path) -> None:
    config = load_config(Path("config"))
    base = {
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "stem_rank": 1,
        "datasheet_slot": "1",
        "genus": "Pinus",
        "species": "taeda",
        "taxon_code": "PINTAE",
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "notes": "",
        "correction_notes": "",
    }
    census = pd.DataFrame(
        [
            {**base, "survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 2, "dbh_mm": 100, "health_observed": 8},
            {**base, "survey_id": "June_2022", "date": date(2022, 6, 16), "source_row": 3, "dbh_mm": 101, "health_observed": 0},
        ]
    )
    issues = validate_census(census, config)
    output = tmp_path / "context.csv"
    context = write_issue_context(census, issues, "W_ALIVE_HEALTH_CONFLICT", output)
    assert output.exists()
    assert len(context) == 2
    assert context["is_issue_row"].sum() == 1
    assert context.loc[context["is_issue_row"], "taxon_code"].iloc[0] == "PINTAE"
    assert {"genus", "species", "taxon_code"}.issubset(context.columns)


def test_validate_reports_tree_taxon_conflicts() -> None:
    config = load_config(Path("config"))
    base = {
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "stem_rank": 1,
        "datasheet_slot": "1",
        "dbh_mm": 100,
        "health_observed": 8,
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "notes": "",
        "correction_notes": "",
    }
    census = pd.DataFrame(
        [
            {
                **base,
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "source_row": 2,
                "genus": "Nyssa",
                "species": "sylvatica",
                "taxon_code": "NYSSYL",
            },
            {
                **base,
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "source_row": 3,
                "genus": "Ilex",
                "species": "opaca",
                "taxon_code": "ILEOPA",
            },
        ]
    )

    issues = validate_census(census, config)
    issue = next(issue for issue in issues if issue.code == IssueCode.W_TAXON_CONFLICT)
    assert issue.details["taxa"][0]["taxon_code"] == "NYSSYL"
    assert issue.details["taxa"][1]["taxon_code"] == "ILEOPA"


def test_write_diagnostics_serializes_structured_details(tmp_path: Path) -> None:
    config = load_config(Path("config"))
    base = {
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "stem_rank": 1,
        "datasheet_slot": "1",
        "genus": "Pinus",
        "species": "taeda",
        "taxon_code": "PINTAE",
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "notes": "",
        "correction_notes": "",
    }
    census = pd.DataFrame(
        [
            {**base, "survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 2, "dbh_mm": 100, "health_observed": 8},
            {**base, "survey_id": "June_2022", "date": date(2022, 6, 16), "source_row": 3, "dbh_mm": 200, "health_observed": 8},
        ]
    )
    issues = validate_census(census, config)
    write_diagnostics(issues, tmp_path)

    diagnostics = pd.read_csv(tmp_path / "issues.csv")
    dbh_jump = diagnostics.loc[diagnostics["code"].eq("W_DBH_JUMP")].iloc[0]
    details = json.loads(dbh_jump["details"])
    assert details["previous_survey"] == "June_2021"
    assert details["current_dbh"] == 200


def test_validate_reports_stem_profile_issues() -> None:
    config = load_config(Path("config"))
    base = {
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "datasheet_slot": "1",
        "genus": "Pinus",
        "species": "taeda",
        "taxon_code": "PINTAE",
        "health_observed": 8,
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "notes": "",
        "correction_notes": "",
    }
    census = pd.DataFrame(
        [
            {
                **base,
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "source_row": 2,
                "stem_rank": 1,
                "dbh_mm": 100,
            },
            {
                **base,
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "source_row": 3,
                "stem_rank": 2,
                "dbh_mm": 80,
            },
            {
                **base,
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "source_row": 4,
                "stem_rank": 1,
                "dbh_mm": 150,
            },
            {
                **base,
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "source_row": 5,
                "stem_rank": 2,
                "dbh_mm": 82,
            },
            {
                **base,
                "survey_id": "June_2022",
                "date": date(2022, 6, 16),
                "source_row": 6,
                "stem_rank": 3,
                "dbh_mm": 60,
            },
        ]
    )

    issues = validate_census(census, config)
    codes = [issue.code for issue in issues]
    assert IssueCode.W_TREE_RANKED_DBH_JUMP in codes
    assert IssueCode.W_TREE_STEM_COUNT_CHANGE in codes
    assert IssueCode.W_TREE_LARGE_STEM_APPEARANCE in codes

    ranked = next(issue for issue in issues if issue.code == IssueCode.W_TREE_RANKED_DBH_JUMP)
    assert ranked.details["rank"] == 1
    assert ranked.details["previous_dbh_profile"] == [100.0, 80.0]
    assert ranked.details["current_dbh_profile"] == [150.0, 82.0, 60.0]


@pytest.mark.parametrize("genus,species,code,dbh,minimum,expected", [
    ("Pinus", "taeda", "PINTAE", 19, 20, True),
    ("Pinus", "taeda", "PINTAE", 20, 20, False),
    ("Ilex", "opaca", "ILEOPA", 47, 20, False),
    ("Vaccinium", "spp.", "VACSPP", 23, 20, False),
    ("Morella", "cerifera", "MORCER", 49, 50, True),
    ("Morella", "cerifera", "MORCER", 50, 50, False),
])
def test_validate_reports_below_threshold_dbh(genus, species, code, dbh, minimum, expected) -> None:
    config = load_config(Path("config"))
    base = {
        "survey_id": "June_2021",
        "date": date(2021, 6, 15),
        "site": "BRNV",
        "zone": "H",
        "plot": "H4",
        "tree_uid": "tree-1",
        "public_tag": "112",
        "identity_tag": "112",
        "tree_number": "112",
        "stem_rank": 1,
        "datasheet_slot": "1",
        "genus": genus,
        "species": species,
        "taxon_code": code,
        "dbh_mm": dbh,
        "health_observed": 8,
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "interpreted_status": "alive",
        "alive_interpreted": True,
        "zombie_ever": False,
        "origin": "test",
        "source_file": "test.csv",
        "source_row": 2,
        "notes": "",
        "correction_notes": "",
    }

    issues = validate_census(pd.DataFrame([base]), config)
    small = [issue for issue in issues if issue.code == IssueCode.W_BELOW_THRESHOLD_DBH]
    assert bool(small) == expected
    if expected:
        assert small[0].details["dbh_mm"] == dbh
        assert small[0].details["minimum_measured_dbh_mm"] == minimum
