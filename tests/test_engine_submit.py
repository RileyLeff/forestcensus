"""Tests for transaction submission and ledger outputs."""

from __future__ import annotations

import json
from pathlib import Path

from forcen.engine import SubmitError, submit_transaction


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")


def test_submit_transaction_creates_ledger(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    result = submit_transaction(TX1_DIR, CONFIG_DIR, workspace)

    assert result.accepted is True
    assert result.version_seq == 1

    observations_csv = workspace / "observations_long.csv"
    assert observations_csv.exists()
    csv_lines = observations_csv.read_text().strip().splitlines()
    assert len(csv_lines) == 3  # header + 2 rows

    manifest_path = workspace / "versions" / "0001" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["version_seq"] == 1
    assert manifest["tx_ids"] == [result.tx_id]
    assert manifest["row_counts"]["field"] >= 2

    trees_view = workspace / "trees_view.csv"
    assert trees_view.exists()
    assert "tree_uid" in trees_view.read_text()

    retag_csv = workspace / "retag_suggestions.csv"
    assert retag_csv.exists()


def test_submit_transaction_idempotent(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    submit_transaction(TX1_DIR, CONFIG_DIR, workspace)
    result = submit_transaction(TX1_DIR, CONFIG_DIR, workspace)

    assert result.accepted is False
    versions = list((workspace / "versions").iterdir())
    assert len(versions) == 1


def test_submit_second_transaction_produces_retag(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    submit_transaction(TX1_DIR, CONFIG_DIR, workspace)
    tx2_dir = Path("planning/fixtures/transactions/tx-2-ops")
    submit_transaction(tx2_dir, CONFIG_DIR, workspace)

    retag_csv = workspace / "retag_suggestions.csv"
    content = retag_csv.read_text()
    assert "suggested_alias_line" in content
