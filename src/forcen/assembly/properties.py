"""Tree property timelines derived from UPDATE commands."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional

from ..dsl.types import UpdateCommand, TagRef, TreeRef
from ..transactions.models import MeasurementRow
from .treebuilder import AliasResolver


@dataclass
class PropertyRecord:
    effective_date: date
    fields: Dict[str, str]


class PropertyTimeline:
    def __init__(self) -> None:
        self._records: List[PropertyRecord] = []

    def add(self, effective_date: date, fields: Dict[str, str]) -> None:
        self._records.append(PropertyRecord(effective_date=effective_date, fields=fields))
        self._records.sort(key=lambda record: record.effective_date)

    def resolve(self, when: date) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for record in self._records:
            if record.effective_date <= when:
                result.update(record.fields)
            else:
                break
        return result


def build_property_timelines(
    commands: Iterable[UpdateCommand], resolver: AliasResolver
) -> Dict[str, PropertyTimeline]:
    timelines: Dict[str, PropertyTimeline] = defaultdict(PropertyTimeline)
    for command in commands:
        if command.effective_date is None:
            continue
        tree_uid = _resolve_tree_uid(resolver, command.tree_ref, command.effective_date)
        timeline = timelines[tree_uid]
        timeline.add(command.effective_date, command.assignments)
    return timelines


def apply_properties(
    measurements: Iterable[MeasurementRow],
    timelines: Dict[str, PropertyTimeline],
) -> None:
    for row in measurements:
        if row.tree_uid is None:
            continue
        timeline = timelines.get(row.tree_uid)
        if timeline is None:
            continue
        fields = timeline.resolve(row.date)
        if not fields:
            continue
        if "genus" in fields:
            row.genus = fields["genus"]
        if "species" in fields:
            row.species = fields["species"]
        if "code" in fields:
            row.code = fields["code"]
        if "site" in fields:
            row.site = fields["site"]
        if "plot" in fields:
            row.plot = fields["plot"]
        if "tag" in fields:
            row.tag = fields["tag"]


def _resolve_tree_uid(resolver: AliasResolver, tree_ref: TreeRef, when: date) -> str:
    if tree_ref.tree_uid is not None:
        return tree_ref.tree_uid
    assert tree_ref.tag is not None
    tag = tree_ref.tag
    resolve_date = tag.at or when
    return resolver.resolve(TagRef(site=tag.site, plot=tag.plot, tag=tag.tag), resolve_date)
