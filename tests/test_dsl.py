"""Tests for DSL parsing and application."""

from __future__ import annotations

import pytest

from forcen.dsl import (
    AliasOverlapError,
    DSLParser,
    DSLState,
    PrimaryConflictError,
)


def test_parse_alias_update_split() -> None:
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO BRNV/H4/112 PRIMARY EFFECTIVE 2020-06-15 NOTE \"Retag\"",
                "UPDATE BRNV/H4/112@2020-01-01 SET genus=Pinus,species=taeda,code=PINTAE",
                "SPLIT BRNV/H4/112 INTO BRNV/H4/900 PRIMARY EFFECTIVE 2020-06-15 "
                "SELECT LARGEST BEFORE 2020-01-01 NOTE \"Largest stem was separate\"",
            ]
        )
    )

    assert len(commands) == 3
    alias = commands[0]
    assert alias.primary is True
    assert alias.effective_date.isoformat() == "2020-06-15"
    assert alias.note == "Retag"

    update = commands[1]
    assert update.assignments["genus"] == "Pinus"
    assert update.assignments["code"] == "PINTAE"

    split = commands[2]
    assert split.selector is not None
    assert split.selector.strategy.value == "LARGEST"
    assert split.selector.date_filter is not None
    assert split.selector.date_filter.kind == "before"


def test_dsl_state_idempotency() -> None:
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY EFFECTIVE 2020-06-15",
                "SPLIT 123e4567-e89b-12d3-a456-426614174000 INTO BRNV/H4/900 PRIMARY",
            ]
        )
    )
    state = DSLState()
    state.apply_many(commands)
    state.apply_many(commands)

    assert len(state.aliases["BRNV", "H4", "508"]) == 1
    assert len(state.splits) == 1


def test_alias_overlap_error() -> None:
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY EFFECTIVE 2020-06-15",
                "ALIAS BRNV/H4/508 TO 923e4567-e89b-12d3-a456-426614174000 EFFECTIVE 2020-06-15",
            ]
        )
    )
    state = DSLState()
    state.apply(commands[0])
    with pytest.raises(AliasOverlapError):
        state.apply(commands[1])


def test_primary_conflict_error() -> None:
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY EFFECTIVE 2020-06-15",
                "ALIAS BRNV/H4/509 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY EFFECTIVE 2020-06-15",
            ]
        )
    )
    state = DSLState()
    state.apply(commands[0])
    with pytest.raises(PrimaryConflictError):
        state.apply(commands[1])
