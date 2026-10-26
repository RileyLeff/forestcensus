from __future__ import annotations

from datetime import date

import pandas as pd

from forestcensus.assembly import _tree_uid
from forestcensus.canonical_review import build_canonical_review
from forestcensus.config import load_config


def test_canonical_review_links_october_new_tree_to_missing_prior_candidate() -> None:
    config = load_config("config")
    old_uid = _tree_uid("BRNV", "L0", "1")
    new_uid = _tree_uid("BRNV", "L0", "900")
    census = pd.DataFrame(
        [
            {
                "survey_id": "June_2023",
                "date": date(2023, 6, 15),
                "site": "BRNV",
                "zone": "L",
                "plot": "L0",
                "tree_uid": old_uid,
                "public_tag": "1",
                "identity_tag": "1",
                "identity_label": "L0/1",
                "tree_number": "1",
                "stem_rank": 1,
                "datasheet_slot": "1",
                "genus": "Pinus",
                "species": "taeda",
                "taxon_code": "PINTAE",
                "dbh_mm": 200.0,
                "health_observed": 8.0,
                "alive_observed": True,
                "standing_observed": True,
                "field_status": "observed_alive",
                "interpreted_status": "alive",
                "alive_interpreted": True,
                "zombie_ever": False,
                "origin": "historical",
                "source_file": "old.csv",
                "source_row": 2,
                "notes": "",
                "correction_notes": "",
            },
            {
                "survey_id": "October_2025",
                "date": date(2025, 10, 9),
                "site": "BRNV",
                "zone": "L",
                "plot": "L0",
                "tree_uid": new_uid,
                "public_tag": "900",
                "identity_tag": "900",
                "identity_label": "L0/900",
                "tree_number": "900",
                "stem_rank": 1,
                "datasheet_slot": "1",
                "genus": "Pinus",
                "species": "taeda",
                "taxon_code": "PINTAE",
                "dbh_mm": 205.0,
                "health_observed": 8.0,
                "alive_observed": None,
                "standing_observed": True,
                "field_status": "observed_alive",
                "interpreted_status": "alive",
                "alive_interpreted": True,
                "zombie_ever": False,
                "origin": "llm_reviewed",
                "source_file": "oct.csv",
                "source_row": 2,
                "notes": "",
                "correction_notes": "",
            },
        ]
    )
    evidence = pd.DataFrame(
        [
            {"plot": "L0", "public_tag_raw": "1", "evidence_rank": "primary", "note_flags": ""},
            {"plot": "L0", "public_tag_raw": "900", "evidence_rank": "accepted_input", "note_flags": "tag"},
        ]
    )
    tag_changes = pd.DataFrame(
        columns=[
            "source_path",
            "source_sheet",
            "source_row",
            "old_tree_code",
            "new_tree_code",
            "old_plot",
            "old_tag",
            "old_taxon_hint",
            "new_plot",
            "new_tag",
            "new_taxon_hint",
            "change_type",
            "year_changed",
        ]
    )

    frames = build_canonical_review(census, evidence, tag_changes, pd.DataFrame(), pd.DataFrame(), config)

    assert "october_new_matches_missing_prior_candidate" in set(frames.candidate_links["link_type"])
    cases = frames.tree_cases.set_index("tree_uid")
    assert cases.loc[new_uid, "review_bucket"] == "candidate_identity_link"
    assert cases.loc[old_uid, "review_bucket"] == "candidate_identity_link"
