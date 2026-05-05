from __future__ import annotations

from pathlib import Path

import json

from forestcensus.publish import build_census


def test_historical_build_writes_parquet(tmp_path: Path) -> None:
    output = tmp_path / "forest_census.parquet"
    census = build_census(output_path=output)
    assert output.exists()
    assert len(census) > 9000
    assert set(census["survey_id"]) >= {"June_2019", "June_2023", "April_2025"}
    assert "tree_uid" in census.columns
    assert "identity_label" in census.columns
    assert "interpreted_status" in census.columns

    l6_74_old = census.loc[census["identity_tag"].eq("74_old_juniper")]
    assert set(l6_74_old["public_tag"]) == {"74"}
    assert set(l6_74_old["identity_label"]) == {"L6/74 old Juniperus"}
    assert set(l6_74_old["survey_id"]) == {"June_2019", "June_2020", "June_2021", "June_2022"}

    l6_75_old = census.loc[census["identity_tag"].eq("75_old_dead_pinus")]
    assert set(l6_75_old["public_tag"]) == {"75"}
    assert set(l6_75_old["identity_label"]) == {"L6/75 old dead Pinus"}
    assert set(l6_75_old["dbh_mm"].dropna()) == {420.0}

    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "diagnostics" / "issues.csv").exists()
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert "diagnostics" in manifest
