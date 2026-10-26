from __future__ import annotations

from dataclasses import replace
from datetime import date
import json
from pathlib import Path

import pandas as pd

from forestcensus.assembly import assemble_events
from forestcensus.config import load_config
from forestcensus.decisions import apply_decisions, build_configured_decision_ledger
from forestcensus.identity import apply_identity_operations


def _copy_base_config(config_dir: Path) -> None:
    config_dir.mkdir()
    for name in ["pipeline.toml", "sites.toml", "surveys.toml", "taxonomy.toml"]:
        (config_dir / name).write_text(Path("config", name).read_text(encoding="utf-8"), encoding="utf-8")
    (config_dir / "corrections.toml").write_text("", encoding="utf-8")


def _event(**overrides) -> dict:
    base = {
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
    return {**base, **overrides}


def test_alias_is_effective_date_aware(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
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
            _event(survey_id="June_2021", date=date(2021, 6, 15)),
            _event(survey_id="June_2022", date=date(2022, 6, 16)),
        ]
    )
    resolved = apply_identity_operations(events, config)
    assert resolved.loc[0, "identity_tag"] == "508"
    assert resolved.loc[1, "identity_tag"] == "112"


def test_approved_r4_alias_preserves_three_stems_and_source_tags() -> None:
    config = load_config()
    aliases = tuple(
        alias for alias in config.identity_aliases
        if (alias.site, alias.plot, alias.tag) == ("BRNV", "R4", "5243")
    )
    assert len(aliases) == 1
    config = replace(
        config,
        identity_aliases=aliases,
        row_corrections=(),
        row_exclusions=(),
        row_reassignments=(),
        split_operations=(),
        taxon_overrides=(),
    )
    rows = []
    for survey_id, observed_date, dbhs, healths in [
        ("October_2025", date(2025, 10, 9), [314, 134, 70], [8, 8, 0]),
        ("May_2026", date(2026, 5, 12), [None, None, None], [9, 8, 0]),
    ]:
        for tag, slot, dbh, health in zip(
            ["5163", "5243", "5243"], ["1", "1", "2"], dbhs, healths
        ):
            rows.append(_event(
                source_row=len(rows) + 2,
                survey_id=survey_id,
                date=observed_date,
                zone="R",
                plot="R4",
                public_tag=tag,
                identity_tag=tag,
                tree_number=tag,
                datasheet_slot=slot,
                genus="Acer",
                species="rubrum",
                taxon_code="ACERUB",
                dbh_mm=dbh,
                health_observed=health,
                alive_observed=health > 0,
                field_status="observed_alive" if health > 0 else "observed_dead",
            ))
    rows.extend([
        _event(plot="R4", public_tag="5238", identity_tag="5238"),
        _event(plot="R3", public_tag="5243", identity_tag="5243"),
        _event(plot="R4", public_tag="5243", identity_tag="5243"),
    ])
    events = pd.DataFrame(rows)
    original = events.copy(deep=True)
    resolved = apply_decisions(events, config)

    pd.testing.assert_frame_equal(events, original)
    pd.testing.assert_frame_equal(
        resolved.drop(columns=["identity_tag", "identity_label", "correction_notes"]),
        original.drop(columns=["identity_tag", "correction_notes"]),
    )
    assert resolved.iloc[:6]["identity_tag"].tolist() == ["5163"] * 6
    assert resolved.iloc[6:]["identity_tag"].tolist() == ["5238", "5243", "5243"]
    assert resolved.iloc[:6]["identity_label"].tolist() == ["R4/5163"] * 6

    assembled = assemble_events(resolved, config)
    merged = assembled.loc[assembled["identity_tag"].eq("5163")]
    assert set(merged["tree_uid"]) == {"b1559c5076c63b50"}
    for _, survey in merged.groupby("survey_id"):
        assert len(survey) == 3
        assert sorted(survey["stem_rank"]) == [1, 2, 3]
        assert survey["public_tag"].value_counts().to_dict() == {"5243": 2, "5163": 1}
        assert survey["field_status"].eq("observed_dead").sum() == 1
    assert len(assembled) == len(events)

    ledger = build_configured_decision_ledger(config)
    assert len(ledger) == 1
    assert ledger.iloc[0]["operation"] == "alias_identity_window"
    assert json.loads(ledger.iloc[0]["parameters"]) == {"identity_tag": "5163"}


def test_approved_red_maple_history_resolves_to_5163_with_original_tags():
    config = load_config()
    config = replace(
        config,
        identity_aliases=tuple(alias for alias in config.identity_aliases if alias.plot == "R4"),
        row_corrections=(), row_exclusions=(), row_reassignments=(),
        split_operations=(), taxon_overrides=(),
    )
    events = pd.DataFrame([
        _event(
            plot="R4", zone="R", public_tag=tag, identity_tag=tag, tree_number=tag,
            genus="Acer", species="rubrum", taxon_code="ACERUB",
            survey_id="June_2023", date=date(2023, 6, 15), source_row=index + 2,
            dbh_mm=dbh, health_observed=health,
            field_status="observed_alive" if health else "observed_dead",
        )
        for index, (tag, dbh, health) in enumerate([
            ("5238", 316, 6), ("5243", 133, 8), ("5243", None, 0),
        ])
    ])
    census = assemble_events(apply_decisions(events, config), config)
    assert len(census) == 3
    assert set(census["tree_uid"]) == {"b1559c5076c63b50"}
    assert census["public_tag"].tolist() == ["5238", "5243", "5243"]
    assert census["stem_rank"].tolist() == [1, 2, 3]
    assert census.iloc[0]["dbh_mm"] == 316
    assert census.iloc[0]["health_observed"] == 6


def test_row_reassignment_can_change_visible_and_identity_tags(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
    (config_dir / "identity.toml").write_text(
        """
[[row_reassignments]]
note = "Row was entered under wrong tag"
match = { source_file = "test.csv", source_row = 2 }
public_tag = "900"
identity_tag = "900"
tree_number = "900"
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    resolved = apply_identity_operations(pd.DataFrame([_event()]), config)
    assert resolved.iloc[0]["public_tag"] == "900"
    assert resolved.iloc[0]["identity_tag"] == "900"
    assert resolved.iloc[0]["tree_number"] == "900"
    assert "wrong tag" in resolved.iloc[0]["correction_notes"]


def test_split_largest_moves_one_measurement_per_survey(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
    (config_dir / "identity.toml").write_text(
        """
[[splits]]
note = "Largest stem belongs to another tree"
source = { site = "BRNV", plot = "H4", identity_tag = "508" }
target_identity_tag = "900"
target_public_tag = "900"
target_tree_number = "900"
selector = { kind = "largest" }
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    events = pd.DataFrame(
        [
            _event(source_row=2, survey_id="June_2021", date=date(2021, 6, 15), dbh_mm=80),
            _event(source_row=3, survey_id="June_2021", date=date(2021, 6, 15), dbh_mm=120),
            _event(source_row=4, survey_id="June_2022", date=date(2022, 6, 16), dbh_mm=82),
            _event(source_row=5, survey_id="June_2022", date=date(2022, 6, 16), dbh_mm=121),
        ]
    )
    resolved = apply_identity_operations(events, config).sort_values("source_row")
    assert resolved.loc[resolved["source_row"].isin([3, 5]), "identity_tag"].tolist() == ["900", "900"]
    assert resolved.loc[resolved["source_row"].isin([2, 4]), "identity_tag"].tolist() == ["508", "508"]
    assert set(resolved.loc[resolved["identity_tag"].eq("900"), "public_tag"]) == {"900"}


def test_split_rank_respects_survey_filter(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
    (config_dir / "identity.toml").write_text(
        """
[[splits]]
note = "Rank two in one survey belongs elsewhere"
source = { site = "BRNV", plot = "H4", identity_tag = "508" }
target_identity_tag = "901"
selector = { kind = "rank", rank = 2, survey_id = "June_2021" }
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    events = pd.DataFrame(
        [
            _event(source_row=2, survey_id="June_2021", date=date(2021, 6, 15), dbh_mm=120),
            _event(source_row=3, survey_id="June_2021", date=date(2021, 6, 15), dbh_mm=80),
            _event(source_row=4, survey_id="June_2022", date=date(2022, 6, 16), dbh_mm=80),
        ]
    )
    resolved = apply_identity_operations(events, config).sort_values("source_row")
    assert resolved.loc[resolved["source_row"].eq(3), "identity_tag"].iloc[0] == "901"
    assert resolved.loc[resolved["source_row"].eq(4), "identity_tag"].iloc[0] == "508"


def test_split_can_create_labeled_synthetic_identity_without_changing_public_tag(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
    (config_dir / "identity.toml").write_text(
        """
[[splits]]
note = "Old dead tree under same visible tag gets its own identity"
source = { site = "BRNV", plot = "H4", identity_tag = "508" }
target_identity_tag = "508_old_dead"
target_identity_label = "H4/508 old dead"
selector = { kind = "all", before = "2022-01-01", match = { field_status = "observed_dead", genus = "Pinus" } }
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    events = pd.DataFrame(
        [
            _event(
                source_row=2,
                survey_id="June_2021",
                date=date(2021, 6, 15),
                genus="Pinus",
                field_status="observed_dead",
            ),
            _event(
                source_row=3,
                survey_id="June_2022",
                date=date(2022, 6, 16),
                genus="Pinus",
                field_status="observed_dead",
            ),
            _event(
                source_row=4,
                survey_id="June_2021",
                date=date(2021, 6, 15),
                genus="Acer",
                field_status="observed_dead",
            ),
        ]
    )

    resolved = apply_identity_operations(events, config).sort_values("source_row")

    moved = resolved.loc[resolved["source_row"].eq(2)].iloc[0]
    assert moved["public_tag"] == "508"
    assert moved["tree_number"] == "508"
    assert moved["identity_tag"] == "508_old_dead"
    assert moved["identity_label"] == "H4/508 old dead"

    unchanged = resolved.loc[resolved["source_row"].isin([3, 4])]
    assert unchanged["identity_tag"].tolist() == ["508", "508"]
    assert unchanged["identity_label"].tolist() == ["H4/508", "H4/508"]
