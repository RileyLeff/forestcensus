"""SPLIT selector evaluation and historical reassignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from ..dsl.types import Selector, SelectorDateFilter, SelectorStrategy, SplitCommand, TagRef
from ..transactions.models import MeasurementRow
from .survey import SurveyCatalog
from .treebuilder import AliasResolver


@dataclass
class MeasurementView:
    row: MeasurementRow
    survey_id: str


def apply_splits(
    measurements: List[MeasurementRow],
    commands: Iterable[SplitCommand],
    resolver: AliasResolver,
    catalog: SurveyCatalog,
) -> None:
    commands_sorted = sorted(commands, key=lambda cmd: cmd.effective_date)
    for command in commands_sorted:
        if command.selector is None:
            continue
        _apply_selector_split(measurements, command, resolver, catalog)


def _apply_selector_split(
    measurements: List[MeasurementRow],
    command: SplitCommand,
    resolver: AliasResolver,
    catalog: SurveyCatalog,
) -> None:
    assert command.effective_date is not None
    selector = command.selector
    if selector is None:
        return

    target_uid = resolver.resolve(command.target, command.effective_date)
    source_uid = _resolve_source_uid(resolver, command)

    views = _collect_views(measurements, source_uid, catalog)
    selected = _select_views(views, selector)

    for view in selected:
        if view.row.date >= command.effective_date:
            continue
        view.row.tree_uid = target_uid


def _resolve_source_uid(resolver: AliasResolver, command: SplitCommand) -> str:
    if command.source.tree_uid is not None:
        return command.source.tree_uid
    assert command.source.tag is not None
    when = command.source.tag.at or command.effective_date
    return resolver.resolve(command.source.tag, when)


def _collect_views(
    measurements: List[MeasurementRow], tree_uid: str, catalog: SurveyCatalog
) -> List[MeasurementView]:
    views: List[MeasurementView] = []
    for row in measurements:
        if row.tree_uid != tree_uid:
            continue
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        views.append(MeasurementView(row=row, survey_id=survey_id))
    return views


def _select_views(
    views: List[MeasurementView], selector: Selector
) -> List[MeasurementView]:
    filtered = _filter_by_date(views, selector.date_filter)

    if selector.strategy == SelectorStrategy.ALL:
        return filtered
    if selector.strategy == SelectorStrategy.LARGEST:
        return [_max_dbh(filtered)] if filtered else []
    if selector.strategy == SelectorStrategy.SMALLEST:
        return [_min_dbh(filtered)] if filtered else []
    if selector.strategy == SelectorStrategy.RANKS:
        return _select_ranks(filtered, selector.ranks)
    return []


def _filter_by_date(
    views: List[MeasurementView], date_filter: Optional[SelectorDateFilter]
) -> List[MeasurementView]:
    if date_filter is None:
        return views
    if date_filter.kind == "before":
        return [view for view in views if view.row.date < date_filter.first]
    if date_filter.kind == "after":
        return [view for view in views if view.row.date > date_filter.first]
    if date_filter.kind == "between":
        end = date_filter.second or date_filter.first
        return [view for view in views if date_filter.first <= view.row.date <= end]
    return views


def _dbh_key(view: MeasurementView) -> tuple:
    dbh = view.row.dbh_mm or 0
    health = view.row.health or 0
    return (-dbh, -health, view.row.row_number)


def _max_dbh(views: List[MeasurementView]) -> MeasurementView:
    return min(views, key=_dbh_key)


def _min_dbh(views: List[MeasurementView]) -> MeasurementView:
    return max(views, key=_dbh_key)


def _select_ranks(
    views: List[MeasurementView], ranks: tuple[int, ...]
) -> List[MeasurementView]:
    per_survey: Dict[str, List[MeasurementView]] = {}
    for view in views:
        per_survey.setdefault(view.survey_id, []).append(view)

    result: List[MeasurementView] = []
    for survey_views in per_survey.values():
        ordered = sorted(survey_views, key=_dbh_key)
        for rank in ranks:
            idx = rank - 1
            if 0 <= idx < len(ordered):
                result.append(ordered[idx])
    return result
