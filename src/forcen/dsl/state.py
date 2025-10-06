"""In-memory application of DSL commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Set, Tuple

from .exceptions import AliasOverlapError, PrimaryConflictError
from .types import AliasCommand, Command, SplitCommand, TagRef, TreeRef, UpdateCommand


@dataclass
class AliasBinding:
    tag: TagRef
    tree_ref: TreeRef
    effective_date: Optional[date]
    primary: bool
    note: Optional[str]


@dataclass
class PrimaryBinding:
    tree_key: str
    tag: TagRef
    effective_date: Optional[date]


class DSLState:
    """Mutable state used to apply DSL commands."""

    def __init__(self) -> None:
        self.aliases: Dict[Tuple[str, str, str], List[AliasBinding]] = {}
        self._alias_signatures: Set[Tuple] = set()
        self.primary_assignments: Dict[str, List[PrimaryBinding]] = {}
        self._primary_signatures: Set[Tuple] = set()
        self.updates: Dict[str, List[UpdateCommand]] = {}
        self._update_signatures: Set[Tuple] = set()
        self.splits: List[SplitCommand] = []
        self._split_signatures: Set[Tuple] = set()

    def apply(self, command: Command) -> None:
        if isinstance(command, AliasCommand):
            self._apply_alias(command)
        elif isinstance(command, UpdateCommand):
            self._apply_update(command)
        elif isinstance(command, SplitCommand):
            self._apply_split(command)
        else:  # pragma: no cover - defensive
            raise TypeError(f"Unsupported command type: {type(command)!r}")

    def apply_many(self, commands: List[Command]) -> None:
        for command in commands:
            self.apply(command)

    # ------------------------------------------------------------------
    def _apply_alias(self, command: AliasCommand) -> None:
        signature = command.signature()
        if signature in self._alias_signatures:
            return

        key = command.target.key()
        bindings = self.aliases.setdefault(key, [])
        new_effective = _effective_sort_key(command.effective_date)
        for existing in bindings:
            if existing.tree_ref.key() == command.tree_ref.key() and existing.effective_date == command.effective_date:
                # Identical logical binding, nothing else to do.
                break
            if existing.effective_date == command.effective_date and existing.tree_ref.key() != command.tree_ref.key():
                raise AliasOverlapError(
                    command.line_no,
                    (
                        f"alias for {command.target.display()} conflicts with existing binding "
                        f"at {_display_date(command.effective_date)}"
                    ),
                )
        else:
            bindings.append(
                AliasBinding(
                    tag=command.target,
                    tree_ref=command.tree_ref,
                    effective_date=command.effective_date,
                    primary=command.primary,
                    note=command.note,
                )
            )
            bindings.sort(key=lambda bind: _effective_sort_key(bind.effective_date))

        self._alias_signatures.add(signature)

        if command.primary:
            self._register_primary(command)

    def _register_primary(self, command: AliasCommand) -> None:
        tree_key = command.tree_ref.key()
        signature = (
            tree_key,
            command.target.key(),
            command.effective_date,
        )
        if signature in self._primary_signatures:
            return

        assignments = self.primary_assignments.setdefault(tree_key, [])
        for existing in assignments:
            if existing.effective_date == command.effective_date and existing.tag.key() != command.target.key():
                raise PrimaryConflictError(
                    command.line_no,
                    (
                        "PRIMARY for tree {} conflicts with tag {} already primary at {}".format(
                            command.tree_ref.display(), existing.tag.display(), _display_date(existing.effective_date)
                        )
                    ),
                )
        assignments.append(
            PrimaryBinding(
                tree_key=tree_key,
                tag=command.target,
                effective_date=command.effective_date,
            )
        )
        assignments.sort(key=lambda bind: _effective_sort_key(bind.effective_date))
        self._primary_signatures.add(signature)

    def _apply_update(self, command: UpdateCommand) -> None:
        signature = command.signature()
        if signature in self._update_signatures:
            return
        tree_key = command.tree_ref.key()
        entries = self.updates.setdefault(tree_key, [])
        entries.append(command)
        entries.sort(key=lambda cmd: _effective_sort_key(cmd.effective_date))
        self._update_signatures.add(signature)

    def _apply_split(self, command: SplitCommand) -> None:
        signature = command.signature()
        if signature in self._split_signatures:
            return
        self.splits.append(command)
        self._split_signatures.add(signature)


def _effective_sort_key(value: Optional[date]) -> Tuple[int, date]:
    if value is None:
        return (0, date.min)
    return (1, value)


def _display_date(value: Optional[date]) -> str:
    return value.isoformat() if value is not None else "unspecified"
