from dataclasses import replace
from datetime import date

import pandas as pd
import pytest

from forestcensus.assembly import assemble_events
from forestcensus.config import load_config
from forestcensus.decisions import apply_decisions, build_configured_decision_ledger
from forestcensus.errors import CorrectionMatchError


def _cleanup_config():
    config = load_config()
    targets = {("L5", "913"), ("L6", "88"), ("L6", "991"), ("L6", "57"), ("R2", "933"), ("M5", "1201")}
    return replace(
        config,
        row_corrections=tuple(
            item for item in config.row_corrections
            if item.match.get("survey_id") == "May_2026"
            and (item.match.get("plot"), item.match.get("public_tag")) in targets
        ),
        row_exclusions=tuple(
            item for item in config.row_exclusions
            if item.match.get("survey_id") == "May_2026"
            and (item.match.get("plot"), item.match.get("public_tag")) in targets
        ),
        identity_aliases=tuple(
            item for item in config.identity_aliases
            if (item.plot, item.tag) == ("L6", "991")
        ),
        row_reassignments=(),
        split_operations=(),
        taxon_overrides=(),
    )


def _events():
    base = {
        "source_file": "import_recent_format_reviewed.csv",
        "survey_id": "May_2026",
        "date": date(2026, 5, 12),
        "site": "BRNV",
        "datasheet_slot": "1",
        "dbh_mm": None,
        "health_observed": 0,
        "standing_observed": True,
        "alive_observed": None,
        "field_status": "observed_dead",
        "notes": "",
        "correction_notes": "",
        "origin": "llm_reviewed",
    }
    rows = []
    for plot, tag, genus, species, changes in [
        ("L5", "913", "Juniperus", "virginiana", {
            "health_observed": 7, "field_status": "observed_alive",
        }),
        ("L5", "913", "Juniperus", "spp.", {
            "health_observed": 7, "field_status": "observed_alive",
            "notes": "previously tagged",
        }),
        ("L6", "88", "Juniperus", "virginiana", {}),
        ("L6", "991", "Juniperus", "virginiana", {}),
        ("L6", "88", "Juniperus", "spp.", {"notes": "previously tagged"}),
        ("L6", "57", "Juniperus", "spp.", {"notes": "previously tagged"}),
        ("R2", "933", "Vaccinium", "spp.", {
            "dbh_mm": 23, "health_observed": 4, "field_status": "observed_alive",
        }),
        ("R2", "933", "Vaccinium", "spp.", {
            "datasheet_slot": "", "health_observed": None,
            "standing_observed": None, "field_status": "unknown",
        }),
        ("M5", "1201", "Morella", "cerifera", {
            "dbh_mm": 62, "health_observed": 3, "field_status": "observed_alive",
        }),
        ("M5", "1201", "Morella", "cerifera", {
            "datasheet_slot": "2", "dbh_mm": 58, "health_observed": 8,
            "field_status": "observed_alive",
        }),
        ("M5", "1201", "Morella", "spp.", {
            "datasheet_slot": "", "health_observed": None,
            "standing_observed": None, "field_status": "unknown",
        }),
    ]:
        rows.append({
            **base, "source_row": len(rows) + 2, "zone": plot[0], "plot": plot,
            "public_tag": tag, "identity_tag": tag, "tree_number": tag,
            "genus": genus, "species": species,
            "taxon_code": (genus[:3] + species[:3]).upper(), **changes,
        })
    return pd.DataFrame(rows)


def test_approved_may_cleanup_preserves_measurements_notes_and_stem_counts():
    config = _cleanup_config()
    events = _events()
    original = events.copy(deep=True)
    resolved = apply_decisions(events, config)
    pd.testing.assert_frame_equal(events, original)
    assert len(resolved) == len(events) - 5
    census = assemble_events(resolved, config)
    counts = census.groupby(["plot", "identity_tag"]).size().to_dict()
    assert counts == {
        ("L5", "913"): 1, ("L6", "88"): 1, ("L6", "57"): 1,
        ("R2", "933"): 1, ("M5", "1201"): 2,
    }
    l5 = census.loc[census["plot"].eq("L5")].iloc[0]
    assert l5["health_observed"] == 7
    assert l5["standing_observed"]
    assert pd.isna(l5["dbh_mm"])
    assert l5["notes"] == "previously tagged"
    assert "52:15:443|JUN|1" in l5["correction_notes"]
    l6 = census.loc[census["plot"].eq("L6")]
    assert set(l6["public_tag"]) == {"88", "991"}
    assert l6["notes"].eq("previously tagged").all()
    assert l6["correction_notes"].str.contains("Supporting review key").all()
    assert census.loc[census["plot"].eq("M5"), "dbh_mm"].tolist() == [62, 58]
    assert census.loc[census["plot"].eq("M5"), "health_observed"].tolist() == [3, 8]
    assert len(build_configured_decision_ledger(config)) == 9


@pytest.mark.parametrize("plot,tag", [("R2", "933"), ("M5", "1201")])
@pytest.mark.parametrize("field,value", [
    ("dbh_mm", 50), ("health_observed", 0), ("standing_observed", False),
])
def test_cancelled_row_decision_fails_if_new_observation_is_supplied(plot, tag, field, value):
    events = _events()
    mask = events["plot"].eq(plot) & events["public_tag"].eq(tag) & events["datasheet_slot"].eq("")
    events.loc[mask, field] = value
    with pytest.raises(CorrectionMatchError, match="matched no rows"):
        apply_decisions(events, _cleanup_config())


def test_cleanup_is_survey_scoped_and_independent_of_row_numbers():
    events = _events()
    historical = events.copy()
    historical["survey_id"] = "October_2025"
    historical["date"] = date(2025, 10, 9)
    events["source_row"] += 5000
    combined = pd.concat([events, historical], ignore_index=True)
    resolved = apply_decisions(combined, _cleanup_config())
    assert len(resolved.loc[resolved["survey_id"].eq("October_2025")]) == len(historical)
    assert len(resolved.loc[resolved["survey_id"].eq("May_2026")]) == len(events) - 5


@pytest.mark.parametrize("species", ["virginiana", "spp."])
@pytest.mark.parametrize("field,value", [
    ("dbh_mm", 235), ("health_observed", 8), ("standing_observed", False),
    ("datasheet_slot", "2"),
])
def test_l5_duplicate_decision_requires_approved_values_on_both_rows(species, field, value):
    events = _events()
    mask = events["plot"].eq("L5") & events["species"].eq(species)
    events.loc[mask, field] = value
    with pytest.raises(CorrectionMatchError, match="matched no rows"):
        apply_decisions(events, _cleanup_config())


def test_l5_merge_does_not_reassign_the_old_pine_or_other_surveys():
    events = _events()
    pine = events.loc[events["plot"].eq("L5")].iloc[[0]].copy()
    pine["survey_id"] = "October_2024"
    pine["date"] = date(2024, 10, 1)
    pine[["public_tag", "identity_tag", "tree_number"]] = "443"
    pine["genus"] = "Pinus"
    pine["species"] = "taeda"
    pine["taxon_code"] = "PINTAE"
    pine["dbh_mm"] = 420
    pine["health_observed"] = 0
    pine["field_status"] = "observed_dead"
    pine["identity_label"] = "L5/443"
    combined = pd.concat([events, pine], ignore_index=True)
    resolved = apply_decisions(combined, _cleanup_config())
    preserved = resolved.loc[resolved["public_tag"].eq("443")]
    pd.testing.assert_frame_equal(
        preserved[pine.columns].reset_index(drop=True), pine.reset_index(drop=True),
        check_dtype=False,
    )
    assert not resolved["public_tag"].eq("943").any()
