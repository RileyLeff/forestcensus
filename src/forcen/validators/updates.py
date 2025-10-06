"""Validation for DSL updates."""

from __future__ import annotations

from typing import Iterable, List

from ..dsl import DSLState
from ..dsl.exceptions import AliasOverlapError, PrimaryConflictError
from ..dsl.types import Command
from .issues import ValidationIssue


def validate_dsl_commands(commands: Iterable[Command]) -> List[ValidationIssue]:
    state = DSLState()
    issues: List[ValidationIssue] = []

    for command in commands:
        try:
            state.apply(command)
        except AliasOverlapError as exc:
            issues.append(
                ValidationIssue(
                    code="E_ALIAS_OVERLAP",
                    severity="error",
                    message=str(exc),
                    location=f"updates.tdl:line {exc.line_no}",
                )
            )
        except PrimaryConflictError as exc:
            issues.append(
                ValidationIssue(
                    code="E_PRIMARY_DUPLICATE_AT_DATE",
                    severity="error",
                    message=str(exc),
                    location=f"updates.tdl:line {exc.line_no}",
                )
            )

    return issues
