"""Tests for transaction id computation."""

from __future__ import annotations

from pathlib import Path

from forcen.transactions.txid import compute_tx_id


def test_compute_tx_id_tx1_fixture() -> None:
    tx_dir = Path("planning/fixtures/transactions/tx-1-initial")
    assert (
        compute_tx_id(tx_dir)
        == "37ad4d5e9c2aa86e3cd1410bcdda94dfd32c6cb8dac05c95fcb3d9b64d003c27"
    )


def test_compute_tx_id_tx2_fixture() -> None:
    tx_dir = Path("planning/fixtures/transactions/tx-2-ops")
    assert (
        compute_tx_id(tx_dir)
        == "1f72b6a152199429cef65d054564c9ee7734703bc41d9914fa2d64e01be84737"
    )
