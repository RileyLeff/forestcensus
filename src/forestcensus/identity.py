"""Time-aware identity operations for retags and row reassignments."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .config import Config, IdentityAlias, RowReassignment, SplitOperation
from .corrections import _match_mask
from .errors import IdentityOperationError


def apply_identity_operations(events: pd.DataFrame, config: Config) -> pd.DataFrame:
    resolved = events.copy()
    if "identity_tag" not in resolved.columns:
        resolved["identity_tag"] = resolved["public_tag"]
    if "identity_label" not in resolved.columns:
        resolved["identity_label"] = ""
    if "correction_notes" not in resolved.columns:
        resolved["correction_notes"] = ""

    for reassignment in config.row_reassignments:
        _apply_row_reassignment(resolved, reassignment)
    for alias in config.identity_aliases:
        _apply_alias(resolved, alias)
    for split in config.split_operations:
        _apply_split(resolved, split)

    _fill_identity_labels(resolved)
    return resolved


def _apply_row_reassignment(df: pd.DataFrame, reassignment: RowReassignment) -> None:
    mask = _match_mask(df, reassignment.match)
    if not mask.any():
        raise IdentityOperationError(f"Row reassignment matched no rows: {reassignment.note}")
    if reassignment.public_tag is not None:
        df.loc[mask, "public_tag"] = reassignment.public_tag
    if reassignment.identity_tag is not None:
        df.loc[mask, "identity_tag"] = reassignment.identity_tag
    elif reassignment.public_tag is not None:
        df.loc[mask, "identity_tag"] = reassignment.public_tag
    if reassignment.tree_number is not None:
        df.loc[mask, "tree_number"] = reassignment.tree_number
    _append_note(df, mask, reassignment.note)


def _apply_alias(df: pd.DataFrame, alias: IdentityAlias) -> None:
    dates = pd.to_datetime(df["date"]).dt.date
    mask = (
        df["site"].astype("string").eq(alias.site)
        & df["plot"].astype("string").eq(alias.plot)
        & df["public_tag"].astype("string").eq(alias.tag)
        & (dates >= alias.effective_from)
    )
    if alias.effective_to is not None:
        mask &= dates <= alias.effective_to
    if not mask.any():
        raise IdentityOperationError(
            "Identity alias matched no rows: "
            f"{alias.site}/{alias.plot}/{alias.tag} -> {alias.identity_tag}"
        )
    df.loc[mask, "identity_tag"] = alias.identity_tag
    _append_note(df, mask, alias.note)


def _apply_split(df: pd.DataFrame, split: SplitOperation) -> None:
    source_mask = _source_mask(df, split.source)
    selector_mask = _selector_mask(df.loc[source_mask], split.selector)
    mask = pd.Series(False, index=df.index)
    mask.loc[selector_mask.index] = selector_mask
    if not mask.any():
        raise IdentityOperationError(f"Split operation matched no rows: {split.note}")

    df.loc[mask, "identity_tag"] = split.target_identity_tag
    if split.target_identity_label is not None:
        df.loc[mask, "identity_label"] = split.target_identity_label
    if split.target_public_tag is not None:
        df.loc[mask, "public_tag"] = split.target_public_tag
    if split.target_tree_number is not None:
        df.loc[mask, "tree_number"] = split.target_tree_number
    _append_note(df, mask, split.note)


def _source_mask(df: pd.DataFrame, source: dict[str, object]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, expected in source.items():
        if column not in df.columns:
            raise IdentityOperationError(f"Split source refers to unknown column {column!r}")
        if column == "date":
            actual = pd.to_datetime(df[column]).dt.date
            mask &= actual.eq(date.fromisoformat(str(expected)))
        else:
            actual = df[column].astype("string").fillna("")
            mask &= actual.eq(str(expected))
    return mask


def _selector_mask(source_rows: pd.DataFrame, selector: dict[str, object]) -> pd.Series:
    mask = pd.Series(False, index=source_rows.index)
    if source_rows.empty:
        return mask

    filtered = _filter_selector_window(source_rows, selector)
    if filtered.empty:
        return mask

    kind = str(selector.get("kind", "all")).lower()
    if kind == "all":
        mask.loc[filtered.index] = True
        return mask

    for _, group in filtered.groupby("survey_id", sort=False):
        ranked = _rank_for_selector(group)
        if kind == "largest":
            mask.loc[ranked.index[0]] = True
        elif kind == "smallest":
            mask.loc[ranked.index[-1]] = True
        elif kind == "rank":
            rank = int(selector["rank"])
            selected = ranked.loc[ranked["_selector_rank"].eq(rank)]
            mask.loc[selected.index] = True
        else:
            raise IdentityOperationError(f"Unknown split selector kind {kind!r}")
    return mask


def _filter_selector_window(rows: pd.DataFrame, selector: dict[str, object]) -> pd.DataFrame:
    filtered = rows.copy()
    if "match" in selector:
        filtered = filtered.loc[_selector_match_mask(filtered, dict(selector["match"]))]
    if "survey_id" in selector:
        filtered = filtered.loc[filtered["survey_id"].astype("string").eq(str(selector["survey_id"]))]
    dates = pd.to_datetime(filtered["date"]).dt.date
    if "before" in selector:
        filtered = filtered.loc[dates < date.fromisoformat(str(selector["before"]))]
        dates = pd.to_datetime(filtered["date"]).dt.date
    if "after" in selector:
        filtered = filtered.loc[dates > date.fromisoformat(str(selector["after"]))]
        dates = pd.to_datetime(filtered["date"]).dt.date
    if "on_or_after" in selector:
        filtered = filtered.loc[dates >= date.fromisoformat(str(selector["on_or_after"]))]
        dates = pd.to_datetime(filtered["date"]).dt.date
    if "on_or_before" in selector:
        filtered = filtered.loc[dates <= date.fromisoformat(str(selector["on_or_before"]))]
    return filtered


def _selector_match_mask(df: pd.DataFrame, match: dict[str, object]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, expected in match.items():
        if column not in df.columns:
            raise IdentityOperationError(f"Split selector match refers to unknown column {column!r}")
        if column in {"dbh_mm", "health_observed", "source_row"}:
            actual = pd.to_numeric(df[column], errors="coerce")
            mask &= actual.eq(float(expected))
        elif column == "date":
            actual = pd.to_datetime(df[column]).dt.date
            mask &= actual.eq(date.fromisoformat(str(expected)))
        else:
            actual = df[column].astype("string").fillna("")
            mask &= actual.eq(str(expected))
    return mask


def _rank_for_selector(group: pd.DataFrame) -> pd.DataFrame:
    ranked = group.assign(
        _dbh=group["dbh_mm"].fillna(-1),
        _health=group["health_observed"].fillna(-1),
    ).sort_values(
        ["_dbh", "_health", "source_file", "source_row"],
        ascending=[False, False, True, True],
        kind="mergesort",
    )
    ranked["_selector_rank"] = range(1, len(ranked) + 1)
    return ranked


def _append_note(df: pd.DataFrame, mask: pd.Series, note: str) -> None:
    note = note.strip()
    if not note:
        return
    current = df.loc[mask, "correction_notes"].fillna("").astype(str)
    df.loc[mask, "correction_notes"] = current.map(
        lambda existing: note if not existing else f"{existing}; {note}"
    )


def _fill_identity_labels(df: pd.DataFrame) -> None:
    empty = df["identity_label"].fillna("").astype(str).str.strip().eq("")
    df.loc[empty, "identity_label"] = [
        f"{plot}/{identity_tag}"
        for plot, identity_tag in zip(df.loc[empty, "plot"], df.loc[empty, "identity_tag"])
    ]
