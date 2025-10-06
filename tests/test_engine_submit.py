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


def test_submit_transaction_idempotent(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    submit_transaction(TX1_DIR, CONFIG_DIR, workspace)
    result = submit_transaction(TX1_DIR, CONFIG_DIR, workspace)

    assert result.accepted is False
    versions = list((workspace / "versions").iterdir())
    assert len(versions) == 1
