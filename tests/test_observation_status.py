from datetime import date

import pandas as pd
import pytest

from forestcensus.adapters import _classify_status
from forestcensus.assembly import assemble_events
from forestcensus.config import load_config
from forestcensus.domain import has_direct_observation, note_mentions_tree_absence
from forestcensus.invariants import _validation_issue_findings
from forestcensus.tree_ir import TreeDataset
from forestcensus.validate import IssueCode, Severity, validate_census


@pytest.mark.parametrize("inputs,expected", [
    ({}, "not_found"),
    ({"alive_observed": True}, "not_found"),
    ({"alive_observed": False}, "not_found"),
    ({"standing_observed": pd.NA}, "not_found"),
    ({"standing_observed": float("nan")}, "not_found"),
    ({"standing_observed": False}, "observed_unknown"),
    ({"standing_observed": True}, "observed_unknown"),
    ({"dbh_mm": 0}, "observed_unknown"),
    ({"dbh_mm": 90}, "observed_unknown"),
    ({"health_observed": 0}, "observed_dead"),
    ({"health_observed": 7}, "observed_alive"),
    ({"standing_observed": True, "notes": "not found"}, "observed_unknown"),
    ({"standing_observed": False, "notes": "missing"}, "observed_unknown"),
    ({"health_observed": 0, "notes": "missing"}, "observed_dead"),
    ({"health_observed": 7, "notes": "DNF"}, "observed_alive"),
    ({"dbh_mm": 90, "alive_observed": False}, "observed_dead"),
    ({"dbh_mm": 90, "alive_observed": True}, "observed_alive"),
])
def test_direct_inputs_determine_found_status(inputs, expected):
    row = pd.Series({
        "dbh_mm": None, "health_observed": None, "standing_observed": None,
        "alive_observed": None, "notes": "", **inputs,
    })
    assert _classify_status(row) == expected
    assert has_direct_observation(
        row.dbh_mm, row.health_observed, row.standing_observed
    ) == (expected != "not_found")


def _events(rows):
    base = {
        "source_file": "test.csv", "source_row": 2, "site": "BRNV", "zone": "H",
        "plot": "H4", "public_tag": "112", "identity_tag": "112",
        "tree_number": "112", "datasheet_slot": "1", "genus": "Pinus",
        "species": "taeda", "taxon_code": "PINTAE", "dbh_mm": None,
        "health_observed": None, "standing_observed": None, "alive_observed": None,
        "notes": "", "correction_notes": "", "origin": "test",
    }
    events = pd.DataFrame([{**base, **row} for row in rows])
    events["field_status"] = events.apply(_classify_status, axis=1)
    return events


def test_found_unknown_health_breaks_absence_run_without_inventing_health():
    events = _events([
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "dbh_mm": 100, "health_observed": 8},
        {"survey_id": "June_2022", "date": date(2022, 6, 15)},
        {"survey_id": "June_2023", "date": date(2023, 6, 15), "standing_observed": False},
        {"survey_id": "May_2024", "date": date(2024, 5, 21)},
    ])
    census = assemble_events(events, load_config()).set_index("survey_id")
    assert census.loc["June_2023", "interpreted_status"] == "observed_unknown"
    assert pd.isna(census.loc["June_2023", "health_observed"])
    assert pd.isna(census.loc["June_2023", "alive_interpreted"])
    assert census.loc[["June_2022", "May_2024"], "interpreted_status"].eq("missing_pending").all()
    assert census.loc[["June_2022", "May_2024"], "alive_interpreted"].isna().all()
    assert not census["zombie_ever"].any()


def test_unknown_stem_does_not_assert_whole_tree_death_or_create_zombie():
    events = _events([
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "health_observed": 0},
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "source_row": 3, "standing_observed": True},
        {"survey_id": "June_2022", "date": date(2022, 6, 15), "dbh_mm": 100, "health_observed": 8},
    ])
    config = load_config()
    census = assemble_events(events, config)
    assert not census["zombie_ever"].any()
    census["_survey_index"] = census["survey_id"].map(config.survey_index)
    tree = next(iter(TreeDataset.from_events(census).trees.values()))
    assert tree.ordered_surveys()[0].field_status == "observed_unknown"


def test_unknown_health_is_not_alive_evidence_after_observed_death():
    events = _events([
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "health_observed": 0},
        {"survey_id": "June_2022", "date": date(2022, 6, 15), "standing_observed": True},
    ])
    census = assemble_events(events, load_config())
    assert not census["zombie_ever"].any()
    assert census["alive_interpreted"].isna().tolist() == [False, True]
    assert not census.iloc[0]["alive_interpreted"]


def test_found_note_conflict_reaches_review_without_overriding_data():
    events = _events([
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "standing_observed": False, "notes": "missing"},
    ])
    config = load_config()
    census = assemble_events(events, config)
    issues = validate_census(census, config)
    assert not any(issue.severity == Severity.ERROR for issue in issues)
    conflicts = [issue for issue in issues if issue.code == IssueCode.W_FOUND_NOTE_CONFLICT]
    assert len(conflicts) == 1
    assert conflicts[0].details["standing_observed"] is False
    assert census.iloc[0]["notes"] == "missing"
    assert census.iloc[0]["field_status"] == "observed_unknown"
    census["_survey_index"] = census["survey_id"].map(config.survey_index)
    findings = _validation_issue_findings(census, TreeDataset.from_events(census), issues)
    assert [finding.code for finding in findings] == ["found_note_conflict"]


def test_not_found_note_without_inputs_is_not_a_conflict():
    events = _events([
        {"survey_id": "June_2021", "date": date(2021, 6, 15), "notes": "not found"},
    ])
    config = load_config()
    census = assemble_events(events, config)
    assert not any(issue.code == IssueCode.W_FOUND_NOTE_CONFLICT for issue in validate_census(census, config))


@pytest.mark.parametrize("note,expected", [
    ("dead/tag missing", False),
    ("Potential missing tag", False),
    ("top missing/broken", False),
    ("missing tag; tree not found", True),
    ("tree is missing", True),
])
def test_missing_tag_or_top_is_not_confused_with_tree_absence(note, expected):
    assert note_mentions_tree_absence(note) == expected
