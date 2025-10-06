"""Tests for engine utility helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from forcen.config import load_config_bundle
from forcen.dsl import DSLParser
from forcen.engine.utils import determine_default_effective_date, with_default_effective
from forcen.transactions import NormalizationConfig, load_transaction


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")


def test_determine_default_effective_date_from_measurements() -> None:
    config = load_config_bundle(CONFIG_DIR)
    tx = load_transaction(TX1_DIR, normalization=NormalizationConfig())
    default_effective = determine_default_effective_date(config, tx)
    assert default_effective == date(2019, 6, 15)


def test_with_default_effective_applies_to_commands() -> None:
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY",
                "UPDATE 123e4567-e89b-12d3-a456-426614174000 SET genus=Pinus",
            ]
        )
    )
    default_date = date(2020, 6, 15)
    updated = with_default_effective(commands, default_date)
    assert all(getattr(cmd, "effective_date", default_date) == default_date for cmd in updated)
