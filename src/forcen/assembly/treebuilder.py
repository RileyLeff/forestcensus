"""Tree identity resolution from DSL commands."""

from __future__ import annotations

from bisect import bisect_right
from datetime import date
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID, uuid5

from ..dsl.types import AliasCommand, Command, SplitCommand, TagRef, TreeRef
from ..transactions.models import MeasurementRow


_TAG_NAMESPACE = UUID("c4b77a82-05e2-4d83-9d9c-20f62157a5e5")


class TagTimeline:
    """Timeline of tree assignments for a single tag."""

    def __init__(self, base_tree_uid: str) -> None:
        self._dates: List[date] = [date.min]
        self._tree_uids: List[str] = [base_tree_uid]

    def bind(self, when: date, tree_uid: str) -> None:
        idx = bisect_right(self._dates, when)
        if idx > 0 and self._dates[idx - 1] == when:
            self._tree_uids[idx - 1] = tree_uid
            return
        self._dates.insert(idx, when)
        self._tree_uids.insert(idx, tree_uid)

    def resolve(self, when: date) -> str:
        idx = bisect_right(self._dates, when) - 1
        if idx < 0:
            idx = 0
        return self._tree_uids[idx]


class AliasResolver:
    """Resolves tag references to tree_uids over time."""

    def __init__(self) -> None:
        self._tags: Dict[Tuple[str, str, str], TagTimeline] = {}

    def ensure_tag(self, tag: TagRef) -> None:
        key = tag.key()
        if key not in self._tags:
            tree_uid = tree_uid_for_tag(key)
            self._tags[key] = TagTimeline(tree_uid)

    def bind(self, tag: TagRef, when: date, tree_uid: str) -> None:
        self.ensure_tag(tag)
        self._tags[tag.key()].bind(when, tree_uid)

    def resolve(self, tag: TagRef, when: date) -> str:
        self.ensure_tag(tag)
        return self._tags[tag.key()].resolve(when)

    def register_commands(self, commands: Iterable[Command]) -> None:
        for command in commands:
            if isinstance(command, AliasCommand):
                self.ensure_tag(command.target)
                if command.tree_ref.tag is not None:
                    self.ensure_tag(command.tree_ref.tag)
            elif isinstance(command, SplitCommand):
                self.ensure_tag(command.target)


def tree_uid_for_tag(tag: TagRef | Tuple[str, str, str]) -> str:
    if isinstance(tag, TagRef):
        key = tag.key()
    else:
        key = tag
    return str(uuid5(_TAG_NAMESPACE, "/".join(key)))


def build_alias_resolver(
    measurements: Iterable[MeasurementRow], commands: List[Command]
) -> AliasResolver:
    resolver = AliasResolver()
    for row in measurements:
        resolver.ensure_tag(TagRef(site=row.site, plot=row.plot, tag=row.tag))
    resolver.register_commands(commands)

    alias_commands = sorted(
        (cmd for cmd in commands if isinstance(cmd, AliasCommand)),
        key=lambda cmd: cmd.effective_date,
    )

    for command in alias_commands:
        assert command.effective_date is not None
        tree_uid = _resolve_tree_ref(
            resolver, command.tree_ref, command.effective_date
        )
        resolver.bind(command.target, command.effective_date, tree_uid)

    split_commands = sorted(
        (cmd for cmd in commands if isinstance(cmd, SplitCommand)),
        key=lambda cmd: cmd.effective_date,
    )

    for command in split_commands:
        if command.effective_date is None:
            continue
        resolver.bind(command.target, command.effective_date, tree_uid_for_tag(command.target))

    return resolver


def _resolve_tree_ref(
    resolver: AliasResolver, tree_ref: TreeRef, default_date: date
) -> str:
    if tree_ref.tree_uid is not None:
        return tree_ref.tree_uid
    assert tree_ref.tag is not None
    when = tree_ref.tag.at or default_date
    return resolver.resolve(tree_ref.tag, when)


def assign_tree_uids(
    measurements: Iterable[MeasurementRow], resolver: AliasResolver
) -> None:
    for row in measurements:
        tag = TagRef(site=row.site, plot=row.plot, tag=row.tag)
        row.tree_uid = resolver.resolve(tag, row.date)
