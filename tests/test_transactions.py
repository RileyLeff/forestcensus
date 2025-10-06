"""Tests for transaction normalization and loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from forcen.dsl import AliasCommand
from forcen.transactions import (
    NormalizationConfig,
    TransactionDataError,
    load_measurements,
    load_transaction,
)


FIXTURE_TX1 = Path("planning/fixtures/transactions/tx-1-initial")
FIXTURE_TX2 = Path("planning/fixtures/transactions/tx-2-ops")


def test_load_measurements_fixture() -> None:
    rows = load_measurements(FIXTURE_TX1 / "measurements.csv")
    assert len(rows) == 2
    first = rows[0]
    assert first.site == "BRNV"
    assert first.dbh_mm == 171
    assert first.health == 9
    assert first.standing is True
    assert first.normalization_flags == []


def test_health_rounding_and_alive_override(tmp_path: Path) -> None:
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes,alive
BRNV,H4,112,2020-06-16,180,8.6,TRUE,"",
BRNV,H4,113,2020-06-16,150,0,TRUE,"",TRUE
BRNV,H4,114,2020-06-16,140,12,TRUE,"",
"""
    )
    rows = load_measurements(csv_path)
    assert rows[0].health == 9
    assert "health_rounded" in rows[0].normalization_flags
    assert rows[1].health == 1
    assert "alive_override" in rows[1].normalization_flags
    assert rows[2].health == 10
    assert "health_clamped" in rows[2].normalization_flags


def test_invalid_boolean_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
BRNV,H4,112,2020-06-16,180,9,MAYBE,""
"""
    )
    with pytest.raises(TransactionDataError):
        load_measurements(csv_path)


def test_load_transaction_with_updates() -> None:
    data = load_transaction(FIXTURE_TX2)
    assert data.commands, "expected DSL commands"
    assert isinstance(data.commands[0], AliasCommand)
