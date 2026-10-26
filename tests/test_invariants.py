from __future__ import annotations

from pathlib import Path

import pandas as pd

from forestcensus.config import load_config
from forestcensus.invariants import build_invariant_report, invariant_summary, write_invariant_report


def test_invariant_report_includes_auto_excluded_nonqualifying_trees(tmp_path: Path) -> None:
    config = load_config(Path("config"))

    report = build_invariant_report("data/raw/forest_census", config)

    nonqualifying = report.loc[report["code"].eq("nonqualifying_tree_excluded")]
    assert not nonqualifying.empty
    assert set(nonqualifying["suggested_action"]) == {"auto_excluded"}
    assert nonqualifying["tree_uid"].nunique() >= 2

    output = write_invariant_report(report, tmp_path / "invariants.csv")
    assert output.exists()
    written = pd.read_csv(output)
    assert len(written) == len(report)


def test_invariant_summary_counts_unresolved_trees() -> None:
    config = load_config(Path("config"))
    report = build_invariant_report("data/raw/forest_census", config)

    summary = invariant_summary(report)

    assert summary["total"] == len(report)
    assert summary["trees"] == report["tree_uid"].nunique()
    unresolved = report.loc[report["resolution_kind"].fillna("").eq("")]
    assert summary["unresolved"] == len(unresolved)
    assert summary["unresolved_trees"] == unresolved["tree_uid"].nunique()
    assert "nonqualifying_tree_excluded" in summary["by_code"]
