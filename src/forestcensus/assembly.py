"""Pure assembly from canonical events to the published census table."""

from __future__ import annotations

import hashlib

import pandas as pd

from .config import Config
from .schema import OUTPUT_COLUMNS


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
    df["stem_rank"] = _rank_stems(df)
    df["interpreted_status"] = _initial_interpreted_status(df)

    for tree_uid, indices in df.groupby("tree_uid", sort=False).groups.items():
        _apply_missingness(df, list(indices), config)

    zombie_uids = _compute_zombies(df)
    df["zombie_ever"] = df["tree_uid"].isin(zombie_uids)
    df["alive_interpreted"] = df["interpreted_status"].eq("alive")

    df = df.sort_values(
        ["_survey_index", "site", "plot", "public_tag", "stem_rank", "source_file", "source_row"],
        kind="mergesort",
    )
    df = df.drop(columns=["_survey_index"])
    return df[OUTPUT_COLUMNS].reset_index(drop=True)


def _tree_uid(site: str, plot: str, identity_tag: str) -> str:
    payload = f"{site}/{plot}/{identity_tag}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def _rank_stems(df: pd.DataFrame) -> pd.Series:
    ranks = pd.Series(index=df.index, dtype="Int64")
    grouped = df.groupby(["tree_uid", "survey_id"], sort=False)
    for _, group in grouped:
        sort_frame = group.assign(
            _dbh=group["dbh_mm"].fillna(-1),
            _health=group["health_observed"].fillna(-1),
        ).sort_values(
            ["_dbh", "_health", "source_file", "source_row"],
            ascending=[False, False, True, True],
            kind="mergesort",
        )
        ranks.loc[sort_frame.index] = range(1, len(sort_frame) + 1)
    return ranks


def _initial_interpreted_status(df: pd.DataFrame) -> pd.Series:
    return df["field_status"].map(
        {
            "observed_alive": "alive",
            "observed_dead": "observed_dead",
            "not_found": "missing_pending",
            "unknown": "missing_pending",
        }
    ).fillna("missing_pending")


def _apply_missingness(df: pd.DataFrame, indices: list[int], config: Config) -> None:
    tree = df.loc[indices].sort_values("_survey_index")
    survey_status = (
        tree.groupby("_survey_index", sort=True)["field_status"]
        .apply(_tree_survey_field_status)
        .to_dict()
    )
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
    tree: pd.DataFrame,
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
    mask = tree["_survey_index"].isin(run)
    df.loc[tree.loc[mask].index, "interpreted_status"] = "inferred_dead"


def _tree_survey_field_status(statuses: pd.Series) -> str:
    values = set(statuses.dropna())
    if "observed_alive" in values:
        return "observed_alive"
    if "observed_dead" in values:
        return "observed_dead"
    if "not_found" in values:
        return "not_found"
    return "unknown"


def _compute_zombies(df: pd.DataFrame) -> set[str]:
    zombies: set[str] = set()
    tree_status = (
        df.groupby(["tree_uid", "_survey_index"], sort=True)["field_status"]
        .apply(_tree_survey_field_status)
        .reset_index()
    )
    for tree_uid, group in tree_status.groupby("tree_uid", sort=False):
        seen_observed_dead = False
        for status in group.sort_values("_survey_index")["field_status"]:
            if status == "observed_dead":
                seen_observed_dead = True
            elif status == "observed_alive" and seen_observed_dead:
                zombies.add(tree_uid)
                break
    return zombies
