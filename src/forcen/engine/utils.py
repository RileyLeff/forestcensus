"""Shared helpers for engine workflows."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Iterable, List

from ..assembly import SurveyCatalog
from ..config import ConfigBundle
from ..dsl.types import AliasCommand, Command, SplitCommand, UpdateCommand
from ..exceptions import ForcenError
from ..transactions.models import TransactionData


def determine_default_effective_date(
    config: ConfigBundle, transaction: TransactionData
) -> date:
    """Determine the default EFFECTIVE date for DSL commands in a transaction."""

    catalog = SurveyCatalog.from_config(config)

    meta = transaction.survey_meta.data if transaction.survey_meta else None
    if meta:
        survey_id = meta.get("survey_id")
        if isinstance(survey_id, str):
            try:
                record = catalog.get(survey_id)
                return record.start
            except KeyError:
                start_value = meta.get("start")
                if isinstance(start_value, str):
                    return date.fromisoformat(start_value)
                raise ForcenError(
                    f"survey_id {survey_id} not found in config and no start provided"
                ) from None

    survey_ids: set[str] = set()
    for row in transaction.measurements:
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            raise ForcenError(
                f"measurement date {row.date.isoformat()} does not map to a known survey"
            )
        survey_ids.add(survey_id)

    if not survey_ids:
        raise ForcenError("cannot infer default EFFECTIVE date without measurements")
    if len(survey_ids) > 1:
        raise ForcenError(
            "transaction spans multiple surveys; specify EFFECTIVE dates explicitly"
        )

    survey_id = next(iter(survey_ids))
    record = catalog.get(survey_id)
    return record.start


def with_default_effective(
    commands: Iterable[Command], default_date: date
) -> List[Command]:
    updated: List[Command] = []
    for command in commands:
        if isinstance(command, AliasCommand) and command.effective_date is None:
            updated.append(replace(command, effective_date=default_date))
        elif isinstance(command, UpdateCommand) and command.effective_date is None:
            updated.append(replace(command, effective_date=default_date))
        elif isinstance(command, SplitCommand) and command.effective_date is None:
            updated.append(replace(command, effective_date=default_date))
        else:
            updated.append(command)
    return updated
