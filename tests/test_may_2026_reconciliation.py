from dataclasses import replace
from datetime import date

import pandas as pd
import pytest

from forestcensus.adapters import _classify_status
from forestcensus.assembly import assemble_events
from forestcensus.config import load_config
from forestcensus.decisions import apply_decisions
from forestcensus.errors import CorrectionMatchError
from forestcensus.validate import IssueCode, validate_census


def _events():
    records = [
        ("M1", "5952", "", "Unidentifiable", None, None, "(fallen)"),
        ("M6", "5154", "1", "Unidentifiable", 0, None, "dead standing, previously tagged"),
        ("L2", "616", "1", "Morella", 0, True, "previously tagged"),
        ("L2", "816", "1", "Morella", None, None, "missing"),
        ("L2", "733", "2", "Morella", 3, None, "double stem, same as 5038"),
        ("L2", "5380", "1", "Morella", 3, True, ""),
        ("L5", "509", "1", "Morella", None, True, "0 - previously tagged"),
        ("H1", "96", "1", "Pinus", 0, True, "missing"),
        ("H4", "130", "1", "Unidentifiable", 0, True, ""),
        ("H4", "130", "2", "Unidentifiable", 0, None, "fallen/missing"),
        ("M0", "585", "1", "Juniperus", 0, True, "not found"),
        ("M0", "586", "1", "Juniperus", 0, None, "not found fallen"),
        ("M4", "2444", "1", "Pinus", 0, True, "NOT Found"),
        ("M7", "319", "1", "Juniperus", None, True, "missing"),
        ("M7", "329", "1", "Nyssa", None, True, "missing"),
        ("L1", "891", "1", "Morella", 0, True, "Previously tagged"),
        ("L5", "786", "1", "Juniperus", 0, True, "previously tagged"),
        ("L6", "574", "1", "Morella", 8, True, "previously tagged"),
        ("L0", "172", "1", "Nyssa", 0, None, "fallen"),
        ("R4", "5211", "1", "Unidentifiable", 0, None, "upright but leaning on another tree"),
        ("H2", "102", "1", "Pinus", None, None, "fallen / dead"),
        ("L1", "148", "1", "Pinus", None, None, "fallen most likely"),
        ("L6", "50", "1", "Juniperus", None, None, "lots of fallen junipers"),
        ("L2", "228", "1", "Nyssa", 0, None, "fallen above girdle"),
        ("H1", "199", "1", "Pinus", 0, None, ""),
        ("M5", "2479", "1", "Nyssa", 0, True, "Fallen"),
    ]
    species = {"Unidentifiable": "spp.", "Morella": "cerifera", "Pinus": "taeda", "Juniperus": "virginiana", "Nyssa": "sylvatica"}
    rows = []
    for plot, tag, slot, genus, health, standing, notes in records:
        rows.append({
            "source_file": "import_recent_format_reviewed.csv", "source_row": len(rows) + 2,
            "survey_id": "May_2026", "date": date(2026, 5, 12), "site": "BRNV",
            "plot": plot, "zone": plot[0], "public_tag": tag, "identity_tag": tag,
            "tree_number": tag, "datasheet_slot": slot, "genus": genus,
            "species": species[genus], "taxon_code": (genus[:3] + species[genus][:3]).upper(),
            "dbh_mm": None, "health_observed": health, "standing_observed": standing,
            "alive_observed": None, "notes": notes, "correction_notes": "", "origin": "test",
        })
    for plot, tag, genus, dbh, health, standing in [
        ("M6", "5145", "Juniperus", 40, 0, True),
        ("L2", "816", "Morella", 59, 2, True),
        ("L2", "5380", "Morella", 51, 6, True),
        ("M7", "329", "Nyssa", None, 0, False),
    ]:
        rows.append({
            **rows[0], "source_row": len(rows) + 2, "plot": plot, "zone": plot[0],
            "public_tag": tag, "identity_tag": tag, "tree_number": tag,
            "survey_id": "October_2025", "date": date(2025, 10, 9), "genus": genus,
            "species": species[genus], "taxon_code": (genus[:3] + species[genus][:3]).upper(),
            "datasheet_slot": "1", "dbh_mm": dbh, "health_observed": health,
            "standing_observed": standing, "notes": "",
        })
    result = pd.DataFrame(rows)
    result["field_status"] = result.apply(_classify_status, axis=1)
    return result


def _config(events):
    config = load_config()
    keys = set(zip(events["plot"], events.public_tag))
    selected = lambda item: item.match.get("survey_id") == "May_2026" and (item.match.get("plot"), item.match.get("public_tag")) in keys
    return replace(
        config, row_corrections=tuple(filter(selected, config.row_corrections)),
        row_exclusions=tuple(filter(selected, config.row_exclusions)),
        row_reassignments=tuple(filter(selected, config.row_reassignments)),
        identity_aliases=(), split_operations=(),
        taxon_overrides=tuple(item for item in config.taxon_overrides if item.match.get("identity_tag") == "5145"),
    )


def test_accepted_may_identities_and_observation_counts():
    raw = _events()
    original = raw.copy(deep=True)
    config = _config(raw)
    resolved = apply_decisions(raw, config)
    pd.testing.assert_frame_equal(raw, original)
    may = resolved[resolved.survey_id.eq("May_2026")]
    assert len(may) == len(raw[raw.survey_id.eq("May_2026")]) - 2
    assert not may.public_tag.eq("5952").any()
    assert not may.public_tag.eq("816").any()
    for written, identity in [("5154", "5145"), ("616", "816"), ("733", "5380")]:
        row = may[may.public_tag.eq(written)].iloc[0]
        assert row.identity_tag == identity
        assert row.tree_number == written
    census = assemble_events(resolved, config)
    current = census[census.survey_id.eq("May_2026")]
    stems = current[current["plot"].eq("L2") & current.identity_tag.eq("5380")]
    assert set(stems.public_tag) == {"5380", "733"}
    assert set(stems.stem_rank) == {1, 2}
    assert stems.health_observed.eq(3).all()
    assert stems.tree_uid.nunique() == 1
    assert len(current[current.identity_tag.eq("816")]) == 1
    for tag in ["891", "786", "574", "509"]:
        assert current[current.public_tag.eq(tag)].identity_tag.eq(tag).all()
    row = current[current.public_tag.eq("509")].iloc[0]
    assert row.health_observed == 0 and row.standing_observed
    row = current[current.public_tag.eq("5154")].iloc[0]
    assert row.genus == "Juniperus" and row.standing_observed
    assert row.health_observed == 0
    fallen = current[current.public_tag.eq("2479")].iloc[0]
    assert fallen.health_observed == 0 and fallen.standing_observed == False
    assert "scan page 35" in fallen.correction_notes


def test_absence_decisions_clear_current_claims_not_historical_death():
    raw = _events()
    config = _config(raw)
    resolved = apply_decisions(raw, config)
    absent_keys = {("H1", "96"), ("H4", "130"), ("M0", "585"), ("M0", "586"), ("M4", "2444"), ("M7", "319"), ("M7", "329")}
    absent = resolved[resolved.survey_id.eq("May_2026") & resolved.apply(lambda r: (r['plot'], r.public_tag) in absent_keys and bool(r.notes), axis=1)]
    assert len(absent) == 7
    assert absent[["dbh_mm", "health_observed", "standing_observed", "alive_observed"]].isna().all().all()
    assert absent.field_status.eq("not_found").all()
    prior = resolved[resolved.survey_id.eq("October_2025") & resolved.public_tag.eq("329")].iloc[0]
    assert prior.health_observed == 0 and not prior.standing_observed
    assert resolved[resolved.survey_id.eq("May_2026") & resolved.public_tag.eq("130") & resolved.datasheet_slot.eq("1")].standing_observed.all()
    census = assemble_events(resolved, config)
    assert not any(i.code == IssueCode.W_FOUND_NOTE_CONFLICT for i in validate_census(census, config))


def test_blank_standing_requires_explicit_individual_evidence():
    raw = _events()
    resolved = apply_decisions(raw, _config(raw))
    may = resolved[resolved.survey_id.eq("May_2026")].set_index("public_tag")
    assert not may.loc["172", "standing_observed"]
    assert not may.loc["102", "standing_observed"]
    assert pd.isna(may.loc["102", "health_observed"])
    assert may.loc["102", "field_status"] == "observed_unknown"
    assert may.loc["5211", "standing_observed"]
    for tag in ["148", "50", "228", "199", "733"]:
        assert pd.isna(may.loc[tag, "standing_observed"])


@pytest.mark.parametrize("tag,field,value", [
    ("5952", "health_observed", 0), ("816", "dbh_mm", 59),
    ("509", "health_observed", 4), ("96", "health_observed", 8),
    ("172", "notes", "not found fallen"),
    ("2479", "health_observed", 8),
])
def test_decisions_fail_when_the_approved_evidence_changes(tag, field, value):
    raw = _events()
    raw.loc[raw.public_tag.eq(tag) & raw.survey_id.eq("May_2026"), field] = value
    with pytest.raises(CorrectionMatchError, match="matched no rows"):
        apply_decisions(raw, _config(raw))


def test_may_decisions_do_not_depend_on_source_row_numbers():
    raw = _events()
    config = _config(raw)
    first = apply_decisions(raw, config)
    raw.source_row += 10000
    second = apply_decisions(raw, config)
    pd.testing.assert_frame_equal(first.drop(columns="source_row"), second.drop(columns="source_row"))
