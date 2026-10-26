"""Pure assembly from canonical events to the published census table."""

from __future__ import annotations

import hashlib

import pandas as pd

from .config import Config
from .domain import passes_size_filter
from .schema import OUTPUT_COLUMNS
from .tree_ir import TreeDataset, TreeRecord


def assemble_events(events: pd.DataFrame, config: Config) -> pd.DataFrame:
    df = events.copy()
    if "identity_tag" not in df.columns:
        df["identity_tag"] = df["public_tag"]
    if "identity_label" not in df.columns:
        df["identity_label"] = [
            f"{plot}/{identity_tag}"
            for plot, identity_tag in zip(df["plot"], df["identity_tag"])
        ]
    if "correction_notes" not in df.columns:
        df["correction_notes"] = ""
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["tree_uid"] = [
        _tree_uid(site, plot, tag)
        for site, plot, tag in zip(df["site"], df["plot"], df["identity_tag"])
    ]
    df["_survey_index"] = df["survey_id"].map(config.survey_index)
    df["interpreted_status"] = _initial_interpreted_status(df)
    df["stem_rank"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    tree_dataset = TreeDataset.from_events(df)
    df = _drop_nonqualifying_below_threshold_trees(df, tree_dataset)
    tree_dataset = TreeDataset.from_events(df)
    tree_dataset.assign_stem_ranks(df)
    for tree in tree_dataset.trees.values():
        _apply_missingness(df, tree, config)

    zombie_uids = _compute_zombies(tree_dataset)
    df["zombie_ever"] = df["tree_uid"].isin(zombie_uids)
    df["alive_interpreted"] = df["interpreted_status"].map(
        {"alive": True, "observed_dead": False, "inferred_dead": False}
    ).astype("boolean")

    df = df.sort_values(
        ["_survey_index", "site", "plot", "public_tag", "stem_rank", "source_file", "source_row"],
        kind="mergesort",
    )
    df = df.drop(columns=["_survey_index"])
    return df[OUTPUT_COLUMNS].reset_index(drop=True)


def _tree_uid(site: str, plot: str, identity_tag: str) -> str:
    payload = f"{site}/{plot}/{identity_tag}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def _initial_interpreted_status(df: pd.DataFrame) -> pd.Series:
    return df["field_status"].map(
        {
            "observed_alive": "alive",
            "observed_dead": "observed_dead",
            "observed_unknown": "observed_unknown",
            "not_found": "missing_pending",
            "unknown": "missing_pending",
        }
    ).fillna("missing_pending")


def _drop_nonqualifying_below_threshold_trees(
    df: pd.DataFrame,
    tree_dataset: TreeDataset,
) -> pd.DataFrame:
    nonqualifying_tree_uids = {
        str(tree_uid)
        for tree_uid, tree_rows in df.groupby("tree_uid", sort=False)
        if _is_nonqualifying_below_threshold_tree(tree_rows)
    }
    if not nonqualifying_tree_uids:
        return df
    return df.loc[~df["tree_uid"].isin(nonqualifying_tree_uids)].copy()


def _is_nonqualifying_below_threshold_tree(tree_rows: pd.DataFrame) -> bool:
    measured = tree_rows.loc[pd.to_numeric(tree_rows["dbh_mm"], errors="coerce").notna()]
    if measured.empty:
        return False
    return not any(
        passes_size_filter(row.dbh_mm, row.genus, row.species, row.taxon_code)
        for row in measured.itertuples()
    )


def _apply_missingness(df: pd.DataFrame, tree: TreeRecord, config: Config) -> None:
    survey_status = {
        survey.survey_index: survey.field_status
        for survey in tree.ordered_surveys()
    }
    ordered = sorted(survey_status)
    run: list[int] = []
    for survey_index in ordered + [None]:
        status = survey_status.get(survey_index) if survey_index is not None else None
        if status in {"not_found", "unknown"}:
            run.append(survey_index)
            continue
        _close_missing_run(df, tree, run, survey_status, config)
        run = []


def _close_missing_run(
    df: pd.DataFrame,
    tree: TreeRecord,
    run: list[int],
    survey_status: dict[int, str],
    config: Config,
) -> None:
    if len(run) < config.not_found_threshold_surveys:
        return
    later_statuses = [
        status
        for survey_index, status in survey_status.items()
        if survey_index > max(run)
    ]
    if "observed_alive" in later_statuses:
        return
    row_indices = [
        row_index
        for survey in tree.surveys
        if survey.survey_index in run
        for row_index in survey.row_indices
    ]
    df.loc[row_indices, "interpreted_status"] = "inferred_dead"


def _compute_zombies(tree_dataset: TreeDataset) -> set[str]:
    zombies: set[str] = set()
    for tree in tree_dataset.trees.values():
        seen_observed_dead = False
        for survey in tree.ordered_surveys():
            status = survey.field_status
            if status == "observed_dead":
                seen_observed_dead = True
            elif status == "observed_alive" and seen_observed_dead:
                zombies.add(tree.tree_uid)
                break
    return zombies
