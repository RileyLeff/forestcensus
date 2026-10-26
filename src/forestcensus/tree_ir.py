"""Tree-level intermediate representation for census assembly.

The IR deliberately treats stems as survey-local ranked observations, not
persistent stem identities. Field data only tag trees, so ranked DBH profiles
are properties of a tree in one survey.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class StemObservation:
    row_index: Any
    dbh_mm: float | None
    health_observed: float | None
    datasheet_slot: str
    source_file: str
    source_row: int | None


@dataclass(frozen=True)
class TreeSurvey:
    survey_id: str
    survey_index: int
    date: date
    public_tag: str
    row_indices: tuple[Any, ...]
    stems: tuple[StemObservation, ...]
    field_status: str

    def ranked_stems(self) -> tuple[StemObservation, ...]:
        return tuple(
            sorted(
                self.stems,
                key=lambda stem: (
                    -_sort_number(stem.dbh_mm),
                    -_sort_number(stem.health_observed),
                    stem.source_file,
                    _sort_number(stem.source_row),
                ),
            )
        )

    def dbh_profile(self, minimum_dbh_mm: float | None = None) -> tuple[float, ...]:
        dbhs = [
            stem.dbh_mm
            for stem in self.ranked_stems()
            if stem.dbh_mm is not None
            and (minimum_dbh_mm is None or stem.dbh_mm >= minimum_dbh_mm)
        ]
        return tuple(float(dbh) for dbh in dbhs)


@dataclass(frozen=True)
class TreeRecord:
    tree_uid: str
    site: str
    plot: str
    identity_tag: str
    identity_label: str
    surveys: tuple[TreeSurvey, ...]

    def ordered_surveys(self) -> tuple[TreeSurvey, ...]:
        return tuple(sorted(self.surveys, key=lambda survey: survey.survey_index))


@dataclass(frozen=True)
class TreeDataset:
    trees: dict[str, TreeRecord]

    @classmethod
    def from_events(cls, events: pd.DataFrame) -> TreeDataset:
        trees = {}
        for tree_uid, tree_rows in events.groupby("tree_uid", sort=False):
            first = tree_rows.iloc[0]
            surveys = []
            for (survey_index, survey_id), survey_rows in tree_rows.groupby(
                ["_survey_index", "survey_id"],
                sort=True,
            ):
                surveys.append(
                    TreeSurvey(
                        survey_id=str(survey_id),
                        survey_index=int(survey_index),
                        date=pd.to_datetime(survey_rows["date"]).dt.date.min(),
                        public_tag=str(survey_rows["public_tag"].iloc[0]),
                        row_indices=tuple(survey_rows.index),
                        stems=tuple(_stem_from_row(row) for row in survey_rows.itertuples()),
                        field_status=_tree_survey_field_status(survey_rows["field_status"]),
                    )
                )
            trees[str(tree_uid)] = TreeRecord(
                tree_uid=str(tree_uid),
                site=str(first["site"]),
                plot=str(first["plot"]),
                identity_tag=str(first["identity_tag"]),
                identity_label=str(first["identity_label"]),
                surveys=tuple(surveys),
            )
        return cls(trees=trees)

    def assign_stem_ranks(self, events: pd.DataFrame) -> None:
        for tree in self.trees.values():
            for survey in tree.surveys:
                for rank, stem in enumerate(survey.ranked_stems(), start=1):
                    events.loc[stem.row_index, "stem_rank"] = rank

    def survey_statuses(self, tree: TreeRecord) -> dict[int, str]:
        return {
            survey.survey_index: survey.field_status
            for survey in tree.ordered_surveys()
        }


def _stem_from_row(row: object) -> StemObservation:
    return StemObservation(
        row_index=getattr(row, "Index"),
        dbh_mm=_nullable_float(getattr(row, "dbh_mm")),
        health_observed=_nullable_float(getattr(row, "health_observed")),
        datasheet_slot=str(getattr(row, "datasheet_slot", "")),
        source_file=str(getattr(row, "source_file", "")),
        source_row=_nullable_int(getattr(row, "source_row", None)),
    )


def _tree_survey_field_status(statuses: pd.Series) -> str:
    values = set(statuses.dropna())
    if "observed_alive" in values:
        return "observed_alive"
    if "observed_unknown" in values:
        return "observed_unknown"
    if "observed_dead" in values:
        return "observed_dead"
    if "not_found" in values:
        return "not_found"
    return "unknown"


def _nullable_float(value: object) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def _nullable_int(value: object) -> int | None:
    if pd.isna(value):
        return None
    return int(value)


def _sort_number(value: float | int | None) -> float:
    if value is None:
        return -1
    return float(value)
