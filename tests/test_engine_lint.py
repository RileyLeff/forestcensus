"""Tests for the lint transaction pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from forcen.engine import lint_transaction
from forcen.transactions import NormalizationConfig

CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")


def test_lint_transaction_fixture_clean(tmp_path: Path) -> None:
    report = lint_transaction(TX1_DIR, CONFIG_DIR)
    assert report.error_count == 0
    assert report.warning_count == 0
    assert len(report.measurement_rows) == 2
    assert report.tx_id == "37ad4d5e9c2aa86e3cd1410bcdda94dfd32c6cb8dac05c95fcb3d9b64d003c27"


def test_lint_transaction_reports_errors(tmp_path: Path) -> None:
    tx_dir = tmp_path / "tx"
    tx_dir.mkdir()
    (tx_dir / "updates.tdl").write_text("", encoding="utf-8")
    (tx_dir / "measurements.csv").write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
UNKNOWN,H4,112,2019-06-16,171,9,TRUE,""
""",
        encoding="utf-8",
    )

    report = lint_transaction(tx_dir, CONFIG_DIR)
    assert report.has_errors
    assert any(issue.code == "E_ROW_SITE_OR_PLOT_UNKNOWN" for issue in report.issues)


def test_lint_transaction_custom_normalization(tmp_path: Path) -> None:
    tx_dir = tmp_path / "tx"
    tx_dir.mkdir()
    (tx_dir / "updates.tdl").write_text("", encoding="utf-8")
    (tx_dir / "measurements.csv").write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
BRNV,H4,112,2019-06-16,171,9,TRUE,""
""",
        encoding="utf-8",
    )

    normalization = NormalizationConfig(rounding="half_up")
    report = lint_transaction(tx_dir, CONFIG_DIR, normalization=normalization)
    assert report.error_count == 0
