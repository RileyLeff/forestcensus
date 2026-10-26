from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pytest

from forestcensus.datasheets import build_plot_datasheets
from forestcensus.field_packet import (
    _attach_poison_ivy_context,
    _historical_difficulty,
    build_field_roster,
    write_field_packet,
)
from forestcensus.publish import promote_candidate


def row(tag="1", survey="May_2026", *, rank=1, uid=None, **kwargs):
    return dict(tree_uid=uid or f"uid-{tag}", plot="L0", identity_tag=tag, public_tag=tag,
                stem_rank=rank, date={"June_2023": "2023-06-01", "October_2024": "2024-10-01", "April_2025": "2025-04-01", "October_2025": "2025-10-01", "May_2026": "2026-05-01", "October_2026": "2026-10-01"}[survey],
                survey_id=survey, genus="Juniperus", species="virginiana", taxon_code="JUNVIR",
                dbh_mm=None, health_observed=None, standing_observed=None,
                source_file="test.csv", source_row=rank) | kwargs


def policy(**kwargs):
    return dict(recent_surveys=["October_2025", "May_2026"], missing_surveys_to_omit=2, omit_dead_fallen=True,
                evergreen_genera=["Juniperus", "Pinus", "Ilex", "Morella"], expected_plots=["L0"],
                decision_reference="approved test decisions") | kwargs


def roster(rows, **kwargs):
    return build_field_roster(pd.DataFrame(rows), policy(**kwargs))


@pytest.mark.parametrize("genus", ["Juniperus", "Nyssa", "Unidentifiable"])
def test_missing_two_surveys_omitted_without_erasing_history(genus):
    frames = roster([row(survey="June_2023", dbh_mm=55, genus=genus),
                     row(survey="October_2025", genus=genus), row(genus=genus)])
    assert frames["roster"].empty
    assert frames["coverage"].disposition.tolist() == ["omitted_absent_two_surveys"]
    assert frames["rechecks"]["L0"] == []


def test_fall_zero_and_missing_spring_does_not_retire_deciduous_tree():
    frames = roster([row(survey="October_2025", health_observed=0, genus="Nyssa"), row(genus="Nyssa")])
    r = frames["roster"].iloc[0]
    assert r.phenology == "deciduous"
    assert r.roster_section == "main"
    assert r.dhs_1 == ""
    assert r.dhs_2 == "NA/0/NA"


def test_aliases_do_not_fragment_uuid_or_add_a_stem():
    rows = [row(survey="October_2025", dbh_mm=55, health_observed=8),
            row(public_tag="99", health_observed=7),
            row(rank=2, public_tag="99", health_observed=0, standing_observed=True)]
    with pytest.raises(ValueError, match="primary recording tag"):
        roster(rows)
    result = roster(rows, primary_tags={"L0/1": "1"})["roster"]
    assert len(result) == 2
    assert result.tag.tolist() == ["1", "1"]
    assert result.dhs_1.tolist() == ["NA/7/NA", "NA/0/1"]
    assert result.dhs_2.tolist() == ["55/8/NA", ""]
    assert result.field_note_numbers.tolist() == ["1|2", "1|2"]


def test_field_note_markers_use_explicit_plot_tag_references_not_prose_numbers():
    rows = [row(survey="October_2025", dbh_mm=70), row(health_observed=7),
            row(rank=2, dbh_mm=65, health_observed=7),
            row("70", dbh_mm=70, health_observed=7),
            row(plot="L1", uid="other-plot", dbh_mm=70, health_observed=7)]
    frames = roster(rows, expected_plots=["L0", "L1"], field_notes=[
        dict(plot="L0", tags=["1"], text="Tag 1 measured 70 mm in 2025.", reference="test"),
        dict(plot="L0", tags=["1"], text="Tag 1 has two stems.", reference="test"),
    ])
    marked = frames["roster"]
    assert marked.loc[marked.tree_uid.eq("uid-1"), "field_note_numbers"].tolist() == ["1|2", "1|2"]
    assert marked.loc[marked.tree_uid.ne("uid-1"), "field_note_numbers"].tolist() == ["", ""]
    payload = build_plot_datasheets(marked, field_notes=frames["field_notes"])
    assert payload["L0"]["rows"][0]["field_note_numbers"] == ["1", "2"]
    assert payload["L1"]["rows"][0]["field_note_numbers"] == []


def test_no_invented_missing_stem_health_and_blanks_are_fixed_slots():
    result = roster([row(survey="October_2025", dbh_mm=27, health_observed=4),
                     row(survey="October_2025", rank=2, dbh_mm=24, health_observed=0),
                     row(health_observed=5)])["roster"]
    assert result.dhs_1.tolist() == ["NA/5/NA", ""]
    assert result.dhs_2.tolist() == ["27/4/NA", "24/0/NA"]


def test_notes_only_extra_rank_does_not_manufacture_a_stem():
    frames = roster([row(survey="October_2025", dbh_mm=80),
                     row(survey="October_2025", rank=2, notes="wrong species"),
                     row(health_observed=8)])
    assert frames["roster"].stem.tolist() == ["1"]
    assert frames["exclusions"].reason.tolist() == ["extra rank has no direct observation in any survey"]


def test_never_observed_tree_is_not_a_search_entry():
    frames = roster([row(survey="October_2025"), row(), row(rank=2)])
    assert frames["roster"].empty


def test_thresholds_inclusive_with_unknown_recent_rank_kept():
    rows = []
    for tag, size, genus in [("1", 20, "Juniperus"), ("2", 50, "Morella"), ("3", 19, "Juniperus"), ("4", 49, "Morella")]:
        for survey in ["October_2025", "May_2026"]:
            rows.append(row(tag, survey, dbh_mm=size, genus=genus,
                            species="cerifera" if genus == "Morella" else "virginiana"))
    rows.extend([row("5", "October_2025", dbh_mm=19), row("5", health_observed=5)])
    frames = roster(rows)
    assert set(frames["roster"].tag) == {"1", "2", "5"}
    assert set(frames["exclusions"].tag) == {"3", "4"}
    assert frames["coverage"].tree_uid.nunique() == 5


def test_pure_history_split_is_guidance_not_duplicate_recording_tag():
    frames = roster([row(survey="October_2025", dbh_mm=70), row(health_observed=4),
                     row("old", "June_2023", public_tag="1", health_observed=0, dbh_mm=300)],
                    historical_identity_checks={"L0/old": "Separate old tree; verify identity."})
    assert len(frames["roster"]) == 1
    assert set(frames["coverage"].disposition) == {"main", "historical_identity_guidance"}
    assert any(n.get("tree_uid") == "uid-old" for n in frames["field_notes"]["L0"])
    assert frames["roster"].iloc[0].field_note_numbers == "1"


def test_stale_or_duplicate_roster_context_is_rejected():
    rows = [row(survey="October_2025"), row(), row()]
    with pytest.raises(ValueError, match="unique"):
        roster(rows)
    with pytest.raises(ValueError, match="latest two"):
        roster(rows[:2], recent_surveys=["May_2026", "October_2025"])
    with pytest.raises(ValueError, match="two-survey"):
        roster(rows[:2], missing_surveys_to_omit=3)


def test_payload_has_blank_notes_and_uuid_stem_identity():
    frames = roster([row(survey="October_2025", dbh_mm=80), row(health_observed=7)])
    data = build_plot_datasheets(frames["roster"], field_notes=frames["field_notes"],
                                recent_surveys=policy()["recent_surveys"], packet_id="test")["L0"]
    assert data["context_surveys"] == ["May_2026", "October_2025"]
    assert data["writing_row_height_pt"] == 20
    assert data["newly_tracked_slots"] == 12
    assert data["date_fields"] == 1
    assert data["crew_roles"] == ["Observer", "Recorder", "Bonus person"]
    assert data["field_note_feedback_fields"] == ["helpful", "confusing", "incorrect"]
    assert data["field_note_feedback_independent"] is True
    assert data["rows"][0]["note_hint"] == ""
    assert data["rows"][0]["tree_uid"] == "uid-1"
    assert data["field_notes"] == []
    assert data["historical_difficulty"] == {"mean": None, "count": 0}


@pytest.mark.parametrize("ivy,suffix", [(True, "/p"), (False, ""), (None, ""), (pd.NA, "")])
def test_hsp_shows_poison_ivy_only_when_present(ivy, suffix):
    frames = roster([row(survey="October_2025"),
                     row(health_observed=7, standing_observed=False, poison_ivy_observed=ivy)])
    r = frames["roster"].iloc[0]
    assert r.hsp_1 == "7/0" + suffix
    assert r.hsp_2 == ""
    data = build_plot_datasheets(frames["roster"])["L0"]
    assert data["rows"][0]["hsp_1"] == "7/0" + suffix


def test_rediscovery_restarts_window_and_omission_is_not_canonical_deletion():
    history = [row(survey="June_2023", dbh_mm=55), row(survey="October_2024"), row(survey="April_2025")]
    a = roster(history, recent_surveys=["October_2024", "April_2025"])
    assert a["roster"].empty
    history += [row(survey="October_2025", health_observed=6), row()]
    before = pd.DataFrame(history)
    b = build_field_roster(before, policy())
    assert len(b["roster"]) == 1
    assert b["roster"].iloc[0].hsp_1 == ""
    assert b["roster"].iloc[0].hsp_2 == "6/NA"
    pd.testing.assert_frame_equal(before, pd.DataFrame(history))
    history += [row(survey="October_2026")]
    assert roster(history, recent_surveys=["May_2026", "October_2026"])["roster"].empty


@pytest.mark.parametrize("health,standing,omit", [(0, False, True), (0, True, False), (0, None, False), (5, False, False), (None, False, False)])
def test_only_dead_and_fallen_is_omitted(health, standing, omit):
    frames = roster([row(survey="October_2025"), row(health_observed=health, standing_observed=standing)])
    assert frames["roster"].empty == omit


def test_dead_then_fallen_context_does_not_invent_current_health():
    history = [row(survey="October_2025", health_observed=0, standing_observed=True), row(standing_observed=False)]
    frames = roster(history)
    assert frames["roster"].empty
    assert frames["coverage"].disposition.tolist() == ["omitted_dead_fallen"]
    assert history[-1]["health_observed"] is None


def test_multistem_dead_fallen_row_does_not_retire_live_siblings():
    frames = roster([row(survey="October_2025", dbh_mm=100), row(survey="October_2025", rank=2, dbh_mm=60),
                     row(health_observed=0, standing_observed=False), row(rank=2, health_observed=6, standing_observed=True)])
    assert frames["roster"].source_rank.tolist() == ["2"]
    assert frames["roster"].stem.tolist() == ["1"]
    assert frames["roster"].iloc[0].hsp_1 == "6/1"


def test_old_dead_fallen_later_standing_gets_question_but_live_return_resets_it():
    history = [row(survey="June_2023", health_observed=0, standing_observed=False),
               row(survey="October_2025"), row(health_observed=0, standing_observed=True)]
    frames = roster(history)
    assert len(frames["roster"]) == 1
    assert len(frames["rechecks"]["L0"]) == 1
    assert frames["rechecks"]["L0"][0]["tree_uids"] == ["uid-1"]
    assert frames["roster"].iloc[0].recheck_ids == "standing-conflict-uid-1"
    history[-1]["health_observed"] = 5
    assert roster(history)["rechecks"]["L0"] == []


def test_targeted_questions_scope_to_uuid_and_need_explicit_retirement_exception():
    history = [row(survey="June_2023", dbh_mm=55), row(survey="October_2025"), row()]
    question = dict(id="verify-tag", plot="L0", tree_uids=["uid-1"], context="Tag unclear.", question="What number is on the tag?", reference="test")
    with pytest.raises(ValueError, match="off roster"):
        roster(history, rechecks=[question])
    frames = roster(history, rechecks=[{**question, "retain_on_roster": True}])
    assert len(frames["roster"]) == 1
    assert frames["roster"].iloc[0].reason == "explicit field-question exception"
    with pytest.raises(ValueError, match="Unknown recheck UUID"):
        roster(history, rechecks=[{**question, "tree_uids": ["not-a-tree"]}])


def test_difficulty_averages_once_per_survey_and_keeps_unrated_missing():
    metadata = pd.DataFrame([
        dict(plot="L0", survey_id="May_2026", difficulty="easy"),
        dict(plot="L0", survey_id="May_2026", difficulty="easy"),
        dict(plot="L0", survey_id="October_2025", difficulty="hard"),
        dict(plot="L1", survey_id="May_2026", difficulty=""),
    ])
    assert _historical_difficulty(metadata) == {"L0": {"mean": 2.0, "count": 2}}
    metadata.loc[1, "difficulty"] = "medium"
    with pytest.raises(ValueError, match="Conflicting difficulty"):
        _historical_difficulty(metadata)
    metadata.loc[1, "difficulty"] = "mystery"
    with pytest.raises(ValueError, match="known category"):
        _historical_difficulty(metadata)


def test_poison_ivy_context_uses_hashed_source_rows_not_rank_or_tag(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("survey_id,poison_ivy\nMay_2026,1\nMay_2026,0\nMay_2026,\n")
    original = pd.DataFrame([row(rank=2, source_file="input.csv", source_row=2),
                             row(rank=1, source_file="input.csv", source_row=3),
                             row(rank=3, source_file="input.csv", source_row=4)])
    manifest = {"inputs": {str(source): hashlib.sha256(source.read_bytes()).hexdigest()}}
    sources = {"May_2026": str(source)}
    result = _attach_poison_ivy_context(original, sources, manifest)
    assert result.poison_ivy_observed.iloc[0] == True
    assert result.poison_ivy_observed.iloc[1] == False
    assert pd.isna(result.poison_ivy_observed.iloc[2])
    assert "poison_ivy_observed" not in original
    wrong = original.copy()
    wrong.loc[0, "source_row"] = 999
    with pytest.raises(ValueError, match="source coordinates"):
        _attach_poison_ivy_context(wrong, sources, manifest)
    source.write_text(source.read_text().replace(",1", ",0"))
    with pytest.raises(ValueError, match="published canonical input"):
        _attach_poison_ivy_context(original, sources, manifest)


def test_packet_refuses_to_overwrite_existing_output(tmp_path):
    with pytest.raises(FileExistsError):
        write_field_packet("unused", "unused", tmp_path)


def test_candidate_promotion_preserves_previous_publication_and_checks_fingerprints(tmp_path):
    candidate = tmp_path / "candidate" / "forest_census.parquet"
    candidate.parent.mkdir()
    pd.DataFrame({"a": [1]}).to_parquet(candidate)
    dependency = tmp_path / "source.txt"
    dependency.write_text("source")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = dict(rows=1, artifact_sha256=digest(candidate), inputs={str(dependency): digest(dependency)},
                    config={}, diagnostics={"by_severity": {}})
    candidate.with_name("manifest.json").write_text(json.dumps(manifest))
    target = tmp_path / "published" / candidate.name
    target.parent.mkdir()
    target.write_bytes(b"old publication")
    old_hash = digest(target)
    promote_candidate(candidate, target)
    assert digest(target) == digest(candidate)
    assert (target.parent / "publication_history" / old_hash[:16] / target.name).read_bytes() == b"old publication"
    dependency.write_text("changed")
    with pytest.raises(ValueError, match="stale"):
        promote_candidate(candidate, target)
    manifest["inputs"] = {}
    manifest["diagnostics"]["by_severity"] = {"error": 1}
    candidate.with_name("manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="validation errors"):
        promote_candidate(candidate, target)


@pytest.mark.skipif(any(shutil.which(tool) is None for tool in ("typst", "pdfinfo", "pdftotext")), reason="PDF tools not installed")
@pytest.mark.parametrize("has_notes", [False, True])
@pytest.mark.parametrize("has_question", [False, True])
def test_real_packet_pdf_zip_and_inline_note_columns(tmp_path, has_notes, has_question):
    parquet = tmp_path / "forest_census.parquet"
    pd.DataFrame([row(survey="October_2025", dbh_mm=55, health_observed=8, standing_observed=True),
                  row(health_observed=7, standing_observed=True, poison_ivy_observed=True)]).to_parquet(parquet)
    parquet.with_name("manifest.json").write_text(json.dumps({
        "artifact_sha256": hashlib.sha256(parquet.read_bytes()).hexdigest(),
        "diagnostics": {"by_severity": {}},
    }))
    config = tmp_path / "policy.toml"
    difficulty = tmp_path / "page_metadata.csv"
    difficulty.write_text("survey_id,plot,difficulty\nMay_2026,L0,easy\nMay_2026,L0,easy\nOctober_2025,L0,hard\n")
    config.write_text('''version = "test"
survey_id = "October_2026"
recent_surveys = ["October_2025", "May_2026"]
expected_plots = ["L0"]
evergreen_genera = ["Juniperus"]
missing_surveys_to_omit = 2
omit_dead_fallen = true
decision_reference = "test"
''' + (f'difficulty_sources = ["{difficulty}"]\n' if has_notes else "") + ('''
[[field_notes]]
plot = "L0"
tags = ["1"]
reference = "test context"
text = "Tag 1 was measured at 55 mm in October 2025."
''' if has_notes else "") + ('''
[[rechecks]]
id = "test-tag"
plot = "L0"
tree_uids = ["uid-1"]
context = "The recorded number was unclear."
question = "What number is on the tag?"
reference = "test"
''' if has_question else ""))
    out = tmp_path / "packet"
    manifest = write_field_packet(parquet, config, out)
    with ZipFile(out / manifest["zip"]) as archive:
        assert archive.namelist() == ["BRNV_L0.pdf"]
        assert archive.read("BRNV_L0.pdf") == (out / "pdf/BRNV_L0.pdf").read_bytes()
    content = subprocess.check_output(["pdftotext", "-layout", str(out / "pdf/BRNV_L0.pdf"), "-"], text=True)
    assert ("Field Notes" in content) == has_notes
    assert ("Recheck Questions" in content) == has_question
    assert "Recheck - no direct input" not in content
    assert "Unhelpful" not in content
    assert "NA = unknown" not in content
    assert manifest["packet_id"] not in content
    assert "Packet " not in content
    assert "hsp = health / standing / poison ivy (only if applicable)" in content
    assert "health/standing; /p = poison ivy" not in content
    assert "* = open question below" in content
    assert "+ = appears in field note" in content
    assert "* Recheck question below" not in content
    marker = ("*" if has_question else "") + ("+" if has_notes else "")
    row_line = next(line for line in content.splitlines() if "JUNVIR" in line and "7/1/p" in line)
    assert row_line.split()[1] == "1" + marker
    assert "Previous DBH (mm) is reference only" not in content
    assert "STD: tick" not in content
    assert "Look for every Recheck tag and stem" not in content
    assert "Recheck rows are not confirmed dead" not in content
    assert "Prior guidance only" not in content
    assert "7/1/p" in content
    assert "8/1" in content and "8/1/NA" not in content
    assert ("Avg. difficulty: 2/4 (2 rated surveys)" if has_notes else "Avg. difficulty: NA") in content
    bounds = ET.fromstring(subprocess.check_output(["pdftotext", "-bbox", str(out / "pdf/BRNV_L0.pdf"), "-"], text=True))
    words = bounds.findall(".//{http://www.w3.org/1999/xhtml}word")
    assert words and all(float(word.attrib["yMin"]) >= 10 for word in words)
    if has_question:
        assert "1*" in content
        assert "What number is on the tag?" in content
        checks = json.loads((out / "rechecks.json").read_text())
        assert checks["L0"][0]["tree_uids"] == ["uid-1"]
        assert manifest["recheck_questions"] == manifest["recheck_trees"] == 1
    if has_notes:
        header = next(line for line in content.splitlines() if "Field Notes" in line)
        assert header.index("Helpful") > header.index("Field Notes")
        assert header.index("Confusing") > header.index("Helpful")
        assert header.index("Incorrect") > header.index("Confusing")
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
