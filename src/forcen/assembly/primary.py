"""Primary tag timelines derived from ALIAS commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional

from ..dsl.types import AliasCommand
from ..transactions.models import MeasurementRow
from .survey import SurveyCatalog
from .treebuilder import AliasResolver


@dataclass
class PrimaryRecord:
    effective_date: date
    tag: str


class PrimaryTimeline:
    def __init__(self) -> None:
        self._records: List[PrimaryRecord] = []

    def add(self, effective_date: date, tag: str) -> None:
        self._records.append(PrimaryRecord(effective_date, tag))
        self._records.sort(key=lambda record: record.effective_date)

    def resolve(self, when: date) -> Optional[str]:
        current: Optional[str] = None
        for record in self._records:
            if record.effective_date <= when:
                current = record.tag
            else:
                break
        return current


def build_primary_timelines(
    commands: Iterable[AliasCommand], resolver: AliasResolver
) -> Dict[str, PrimaryTimeline]:
    timelines: Dict[str, PrimaryTimeline] = {}
    for command in commands:
        if not command.primary or command.effective_date is None:
            continue
        tree_uid = resolver.resolve(command.target, command.effective_date)
        timeline = timelines.setdefault(tree_uid, PrimaryTimeline())
        timeline.add(command.effective_date, command.target.tag)
    return timelines


def apply_primary_tags(
    measurements: Iterable[MeasurementRow],
    timelines: Dict[str, PrimaryTimeline],
    catalog: SurveyCatalog,
) -> None:
    for row in measurements:
        if row.tree_uid is None:
            row.public_tag = row.public_tag or row.tag
            continue
        timeline = timelines.get(row.tree_uid)
        if timeline is None:
            row.public_tag = row.public_tag or row.tag
            continue
        tag = timeline.resolve(row.date)
        row.public_tag = tag or row.public_tag or row.tag
