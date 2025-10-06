"""Full dataset reassembly from raw measurements and DSL commands."""

from __future__ import annotations

from typing import List, Sequence

from ..config import ConfigBundle
from ..dsl.types import AliasCommand, Command, SplitCommand, UpdateCommand
from ..transactions.models import MeasurementRow
from .properties import apply_properties, build_property_timelines
from .primary import apply_primary_tags, build_primary_timelines
from .split import apply_splits
from .survey import SurveyCatalog
from .treebuilder import assign_tree_uids, build_alias_resolver
from .trees import generate_implied_rows


def clone_raw_measurement(row: MeasurementRow) -> MeasurementRow:
    return MeasurementRow(
        row_number=row.row_number,
        site=row.site,
        plot=row.plot,
        tag=row.tag,
        date=row.date,
        dbh_mm=row.dbh_mm,
        health=row.health,
        standing=row.standing,
        notes=row.notes,
        genus=row.genus,
        species=row.species,
        code=row.code,
        origin=row.origin,
        normalization_flags=list(row.normalization_flags),
        raw=dict(row.raw),
        tree_uid=None,
        public_tag=None,
        source_tx=row.source_tx,
    )


def assemble_dataset(
    raw_rows: Sequence[MeasurementRow], commands: Sequence[Command], config: ConfigBundle
) -> List[MeasurementRow]:
    measurements = [clone_raw_measurement(row) for row in raw_rows]
    catalog = SurveyCatalog.from_config(config)

    resolver_commands = list(commands)
    resolver = build_alias_resolver(measurements, resolver_commands)
    assign_tree_uids(measurements, resolver)
    apply_splits(
        measurements,
        [cmd for cmd in resolver_commands if isinstance(cmd, SplitCommand)],
        resolver,
        catalog,
    )

    property_timelines = build_property_timelines(
        [cmd for cmd in resolver_commands if isinstance(cmd, UpdateCommand)],
        resolver,
    )
    apply_properties(measurements, property_timelines)

    primary_timelines = build_primary_timelines(
        [cmd for cmd in resolver_commands if isinstance(cmd, AliasCommand)],
        resolver,
    )
    apply_primary_tags(measurements, primary_timelines, catalog)

    implied_rows = generate_implied_rows(measurements, config)
    dataset = measurements + implied_rows

    dataset.sort(key=lambda row: (row.date, row.site, row.plot, row.tag, row.row_number))
    return dataset
