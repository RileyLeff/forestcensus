from __future__ import annotations

from datetime import date

import pandas as pd

from forestcensus.tree_ir import TreeDataset


def test_tree_dataset_groups_rows_by_tree_and_survey() -> None:
    events = pd.DataFrame(
        [
            {
                "_survey_index": 1,
                "tree_uid": "tree-1",
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "site": "BRNV",
                "plot": "H4",
                "public_tag": "112",
                "identity_tag": "112",
                "identity_label": "H4/112",
                "datasheet_slot": "1",
                "dbh_mm": 80,
                "health_observed": 8,
                "field_status": "observed_alive",
                "source_file": "test.csv",
                "source_row": 2,
            },
            {
                "_survey_index": 1,
                "tree_uid": "tree-1",
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "site": "BRNV",
                "plot": "H4",
                "public_tag": "112",
                "identity_tag": "112",
                "identity_label": "H4/112",
                "datasheet_slot": "2",
                "dbh_mm": 120,
                "health_observed": 8,
                "field_status": "observed_alive",
                "source_file": "test.csv",
                "source_row": 3,
            },
        ]
    )

    dataset = TreeDataset.from_events(events)
    tree = dataset.trees["tree-1"]
    survey = tree.surveys[0]

    assert tree.identity_tag == "112"
    assert survey.field_status == "observed_alive"
    assert survey.dbh_profile() == (120.0, 80.0)


def test_tree_dataset_assigns_stem_ranks_without_using_datasheet_slot() -> None:
    events = pd.DataFrame(
        [
            {
                "_survey_index": 1,
                "tree_uid": "tree-1",
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "site": "BRNV",
                "plot": "H4",
                "public_tag": "112",
                "identity_tag": "112",
                "identity_label": "H4/112",
                "datasheet_slot": "1",
                "dbh_mm": 80,
                "health_observed": 8,
                "field_status": "observed_alive",
                "source_file": "test.csv",
                "source_row": 2,
            },
            {
                "_survey_index": 1,
                "tree_uid": "tree-1",
                "survey_id": "June_2021",
                "date": date(2021, 6, 15),
                "site": "BRNV",
                "plot": "H4",
                "public_tag": "112",
                "identity_tag": "112",
                "identity_label": "H4/112",
                "datasheet_slot": "2",
                "dbh_mm": 120,
                "health_observed": 8,
                "field_status": "observed_alive",
                "source_file": "test.csv",
                "source_row": 3,
            },
        ]
    )
    events["stem_rank"] = pd.NA

    TreeDataset.from_events(events).assign_stem_ranks(events)

    by_slot = events.set_index("datasheet_slot")["stem_rank"].to_dict()
    assert by_slot["2"] == 1
    assert by_slot["1"] == 2
