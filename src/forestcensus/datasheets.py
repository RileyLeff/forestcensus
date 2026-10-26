"""Operational datasheet preparation for upcoming censuses."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import pandas as pd

from .domain import (
    MORELLA_CERIFERA_MIN_DBH_MM,
    NON_MORELLA_CERIFERA_MIN_DBH_MM,
    passes_size_filter,
)


DEFAULT_RECENT_SURVEYS = ("April_2025", "October_2025")
DEFAULT_FIELD_SURVEY_ID = "May_2026"
DEFAULT_DATASHEET_DIFFICULTY = "NA/unknown"
DEFAULT_DATASHEET_ROWS_PER_PAGE = 40
DEFAULT_SUPPLEMENT_INLINE_MAX_ROWS = 24


def build_datasheet_prep(
    census: pd.DataFrame,
    *,
    recent_surveys: Iterable[str] = DEFAULT_RECENT_SURVEYS,
) -> dict[str, pd.DataFrame | dict[str, object]]:
    """Build non-canonical operational tables for field datasheet generation.

    A row is considered found for this workflow when the field crew recorded at
    least one direct input: DBH, health, or standing. Rows with none of those
    signals are treated as not found/not reported for the purpose of upcoming
    working sheets, even if the broader canonical pipeline currently labels them
    as ``unknown``.
    """

    surveys = list(recent_surveys)
    survey_order = {survey: index for index, survey in enumerate(surveys)}
    recent = census.loc[census["survey_id"].isin(surveys)].copy()
    recent["dbh_mm"] = pd.to_numeric(recent["dbh_mm"], errors="coerce")
    recent["health_observed"] = pd.to_numeric(recent["health_observed"], errors="coerce")
    recent["_standing_present"] = recent["standing_observed"].notna()
    recent["_survey_order"] = recent["survey_id"].map(survey_order)
    recent["_found_signal"] = (
        recent["dbh_mm"].notna()
        | recent["health_observed"].notna()
        | recent["_standing_present"]
    )
    found = recent.loc[recent["_found_signal"]].copy()

    active_before_filter = _active_stems(found, recent, census, surveys)
    active, excluded_nonqualifying = _filter_nonqualifying_active_stems(active_before_filter, census)
    found_active = _found_rows_for_active_stems(found, active)
    duplicate_plot_tags = _duplicate_plot_tags(active)
    species_changes = active.loc[active["spp_values_last2"].str.contains("|", regex=False)].copy()
    species_conflicts = _species_conflicts(active)
    duplicate_dbh = _same_survey_same_tag_duplicate_dbh(found_active)
    summary = {
        "source_surveys": surveys,
        "found_definition": "dbh_mm present OR health_observed present OR standing_observed present",
        "stem_qualification_rule": (
            "exclude active stem rows with DBH history but no measurement passing the taxon-specific size filter"
        ),
        "measurement_threshold_mm": {
            "non_morella_cerifera": NON_MORELLA_CERIFERA_MIN_DBH_MM,
            "morella_cerifera": MORELLA_CERIFERA_MIN_DBH_MM,
        },
        "recent_rows": int(len(recent)),
        "found_recent_rows": int(len(found)),
        "active_stems_before_threshold_filter": int(len(active_before_filter)),
        "excluded_nonqualifying_stems": int(len(excluded_nonqualifying)),
        "active_stems": int(len(active)),
        "active_trees": int(active["tree_uid"].nunique()) if not active.empty else 0,
        "plots": int(active["plot"].nunique()) if not active.empty else 0,
        "duplicate_plot_tags": int(len(duplicate_plot_tags)),
        "species_changes_by_stem_last2": int(len(species_changes)),
        "species_conflicts_by_tree_active": int(len(species_conflicts)),
        "same_survey_same_tag_duplicate_dbh_rows": int(len(duplicate_dbh)),
    }
    return {
        "active_stems_found_last2": active,
        "duplicate_plot_tags_active": duplicate_plot_tags,
        "species_changes_by_stem_last2": species_changes,
        "species_conflicts_by_tree_active": species_conflicts,
        "same_survey_same_tag_duplicate_dbh": duplicate_dbh,
        "excluded_nonqualifying_stems": excluded_nonqualifying,
        "summary": summary,
    }


def write_datasheet_prep(frames: dict[str, pd.DataFrame | dict[str, object]], out_dir: str | Path) -> dict[str, object]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for name, frame in frames.items():
        if name == "summary":
            continue
        assert isinstance(frame, pd.DataFrame)
        path = out_path / f"{name}.csv"
        frame.to_csv(path, index=False)
        outputs[name] = str(path)
    summary = dict(frames["summary"])
    summary["outputs"] = outputs
    summary_path = out_path / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["summary"] = str(summary_path)
    return summary


def build_plot_datasheets(
    active_stems: pd.DataFrame,
    *,
    survey_id: str = DEFAULT_FIELD_SURVEY_ID,
    difficulty: str = DEFAULT_DATASHEET_DIFFICULTY,
    site: str = "BRNV",
    rows_per_page: int = DEFAULT_DATASHEET_ROWS_PER_PAGE,
    supplement_inline_max_rows: int = DEFAULT_SUPPLEMENT_INLINE_MAX_ROWS,
    field_notes: dict[str, list[dict]] | None = None,
    recent_surveys: Iterable[str] = DEFAULT_RECENT_SURVEYS,
    packet_id: str = "",
    historical_difficulty: dict[str, dict] | None = None,
    rechecks: dict[str, list[dict]] | None = None,
) -> dict[str, dict[str, object]]:
    """Build per-plot JSON payloads consumed by the Typst datasheet template."""

    if active_stems.empty:
        return {}

    frame = active_stems.copy()
    frame["tag"] = frame["tag"].map(_clean_tag)
    frame["stem"] = frame["stem"].map(_clean_stem)
    frame["_health"] = pd.to_numeric(frame["latest_health"], errors="coerce")
    rows_by_plot: dict[str, dict[str, object]] = {}

    for plot, group in frame.groupby("plot", sort=False):
        ordered = group.sort_values(
            ["tag", "stem"],
            key=lambda series: series.astype(str).map(_natural_key),
            kind="mergesort",
        )
        if "roster_section" in ordered:
            ordered = ordered.sort_values("roster_section", kind="mergesort")
        living_tree_count = int(
            ordered.loc[ordered["_health"].gt(0).fillna(False), "tree_uid"].nunique()
        )
        rows = [
            {
                "row": str(index),
                "tag": str(row["tag"]),
                "tree_uid": str(row["tree_uid"]),
                "spp": _json_text(row.get("spp_latest")),
                "stem": str(row["stem"]),
                "reference_dbh": _number_or_blank(row.get("reference_dbh_mm")),
                "dhs_1": _json_text(row.get("dhs_1")),
                "dhs_2": _json_text(row.get("dhs_2")),
                **({"hsp_1": _json_text(row.get("hsp_1")), "hsp_2": _json_text(row.get("hsp_2"))}
                   if "hsp_1" in row else {}),
                "note_hint": "",
                "roster_section": _json_text(row.get("roster_section", "main")),
                "source_rank": _json_text(row.get("source_rank", row["stem"])),
                "last_seen": _json_text(row.get("latest_survey", "")),
                "recheck_ids": _json_text(row.get("recheck_ids", "")).split("|") if _json_text(row.get("recheck_ids", "")) else [],
                "field_note_numbers": _json_text(row.get("field_note_numbers", "")).split("|") if _json_text(row.get("field_note_numbers", "")) else [],
            }
            for index, (_, row) in enumerate(ordered.iterrows(), start=1)
        ]
        row_pages = _chunks(rows, rows_per_page)
        supplement_on_last_main_page = len(row_pages[-1]) <= supplement_inline_max_rows
        rows_by_plot[str(plot)] = {
            "site": site,
            "plot": str(plot),
            "survey_id": survey_id,
            "tree_count": int(ordered["tree_uid"].nunique()),
            "living_count": living_tree_count,
            "species_count": int(ordered["spp_latest"].dropna().astype(str).nunique()),
            "difficulty": difficulty,
            "crew_slots": 12,
            "existing_tags": list(dict.fromkeys(ordered["tag"].astype(str))),
            "rows": rows,
            "row_pages": row_pages,
            "main_page_count": len(row_pages),
            "supplement_on_last_main_page": supplement_on_last_main_page,
            "total_pages": len(row_pages) if supplement_on_last_main_page else len(row_pages) + 1,
        }
        if field_notes is not None:
            payload = rows_by_plot[str(plot)]
            # Packet layout flows automatically; page count is filled from the
            # compiled PDF, never guessed from a fixed row limit.
            payload.update(
                packet_id=packet_id,
                historical_difficulty=(historical_difficulty or {}).get(str(plot), {"mean": None, "count": 0}),
                survey_title=survey_id.replace("_", " ") + " Survey",
                date_fields=1,
                crew_roles=["Observer", "Recorder", "Bonus person"],
                writing_row_height_pt=20,
                newly_tracked_slots=12,
                field_notes=field_notes.get(str(plot), []),
                rechecks=(rechecks or {}).get(str(plot), []),
                field_note_feedback_fields=["helpful", "confusing", "incorrect"],
                field_note_feedback_independent=True,
                context_surveys=list(reversed(list(recent_surveys))),
                supplement_on_last_main_page=False,
                total_pages=None,
                recent_tree_count=int(ordered.loc[ordered.roster_section.eq("main"), "tree_uid"].nunique()),
                recheck_rows=sum(bool(row["recheck_ids"]) for row in rows),
            )
            payload.pop("row_pages")
            payload.pop("main_page_count")

    return dict(sorted(rows_by_plot.items(), key=lambda item: _natural_key(item[0])))


def write_plot_datasheets(
    active_stems: pd.DataFrame,
    out_dir: str | Path,
    *,
    survey_id: str = DEFAULT_FIELD_SURVEY_ID,
    difficulty: str = DEFAULT_DATASHEET_DIFFICULTY,
    template: str | Path = "prototypes/datasheets/portrait_prototype.typ",
    compile_pdfs: bool = True,
    rows_per_page: int = DEFAULT_DATASHEET_ROWS_PER_PAGE,
    supplement_inline_max_rows: int = DEFAULT_SUPPLEMENT_INLINE_MAX_ROWS,
) -> dict[str, object]:
    out_path = Path(out_dir)
    json_dir = out_path / "json"
    typ_dir = out_path / "typ"
    pdf_dir = out_path / "pdf"
    json_dir.mkdir(parents=True, exist_ok=True)
    typ_dir.mkdir(parents=True, exist_ok=True)
    if compile_pdfs:
        pdf_dir.mkdir(parents=True, exist_ok=True)

    payloads = build_plot_datasheets(
        active_stems,
        survey_id=survey_id,
        difficulty=difficulty,
        rows_per_page=rows_per_page,
        supplement_inline_max_rows=supplement_inline_max_rows,
    )
    template_text = Path(template).read_text(encoding="utf-8")
    typst_available = shutil.which("typst") is not None
    compiled: list[str] = []
    typ_files: list[str] = []
    json_files: list[str] = []
    combined_pdf: str | None = None

    for plot, payload in payloads.items():
        stem = f"{payload['site']}_{plot}"
        json_path = json_dir / f"{stem}.json"
        typ_path = typ_dir / f"{stem}.typ"
        pdf_path = pdf_dir / f"{stem}.pdf"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        relative_json = Path("../json") / json_path.name
        typ_path.write_text(
            _typst_with_data_path(template_text, relative_json.as_posix()),
            encoding="utf-8",
        )
        json_files.append(str(json_path))
        typ_files.append(str(typ_path))
        if compile_pdfs and typst_available:
            subprocess.run(
                ["typst", "compile", "--root", str(out_path), str(typ_path), str(pdf_path)],
                check=True,
            )
            compiled.append(str(pdf_path))

    pdfunite = shutil.which("pdfunite")
    if compiled and pdfunite is not None:
        combined_path = out_path / f"BRNV_{survey_id}_datasheets.pdf"
        subprocess.run([pdfunite, *compiled, str(combined_path)], check=True)
        combined_pdf = str(combined_path)

    summary = {
        "plots": len(payloads),
        "survey_id": survey_id,
        "difficulty": difficulty,
        "rows_per_page": rows_per_page,
        "supplement_inline_max_rows": supplement_inline_max_rows,
        "json_dir": str(json_dir),
        "typ_dir": str(typ_dir),
        "pdf_dir": str(pdf_dir) if compile_pdfs else None,
        "json_files": json_files,
        "typ_files": typ_files,
        "pdf_files": compiled,
        "combined_pdf": combined_pdf,
        "typst_available": typst_available,
        "pdfunite_available": pdfunite is not None,
        "compiled": bool(compile_pdfs and typst_available),
    }
    summary_path = out_path / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["summary"] = str(summary_path)
    return summary


def _active_stems(
    found: pd.DataFrame,
    recent: pd.DataFrame,
    census: pd.DataFrame,
    surveys: list[str],
) -> pd.DataFrame:
    if found.empty:
        return pd.DataFrame(columns=_active_columns())
    rows: list[dict[str, object]] = []
    keys = ["tree_uid", "plot", "identity_tag", "public_tag", "stem_rank"]
    recent_groups = {key: group for key, group in recent.groupby(keys, dropna=False, sort=False)}
    reference_dbh = _latest_dbh_by_stem(census)
    hsp_surveys = list(reversed(surveys[-2:]))
    for key, group in found.groupby(keys, dropna=False, sort=False):
        ordered = group.sort_values(["_survey_order", "source_file", "source_row"])
        latest = ordered.iloc[-1]
        recent_group = recent_groups.get(key, group.iloc[0:0])
        rows.append(
            {
                "plot": latest["plot"],
                "tree_uid": latest["tree_uid"],
                "tag": _clean_tag(latest["public_tag"]),
                "identity_tag": _clean_tag(latest["identity_tag"]),
                "stem": _clean_stem(latest["stem_rank"]),
                "spp_latest": latest["taxon_code"],
                "spp_values_last2": "|".join(sorted(set(ordered["taxon_code"].dropna().astype(str)))),
                "latest_survey": latest["survey_id"],
                "latest_dbh_mm": latest["dbh_mm"],
                "reference_dbh_mm": reference_dbh.get((str(latest["tree_uid"]), _clean_stem(latest["stem_rank"]))),
                "latest_health": latest["health_observed"],
                "latest_standing": latest["standing_observed"],
                "dhs_1": _dhs_for_survey(recent_group, hsp_surveys[0]) if hsp_surveys else "",
                "dhs_2": _dhs_for_survey(recent_group, hsp_surveys[1]) if len(hsp_surveys) > 1 else "",
                "last2_observation_count": int(len(ordered)),
                "latest_notes": latest.get("notes", ""),
                "latest_source_file": latest["source_file"],
                "latest_source_row": latest["source_row"],
            }
        )
    frame = pd.DataFrame(rows, columns=_active_columns())
    return frame.sort_values(
        ["plot", "tag", "stem"],
        key=lambda series: series.astype(str).map(_natural_key),
        kind="mergesort",
    )


def _filter_nonqualifying_active_stems(
    active: pd.DataFrame,
    census: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if active.empty:
        return active, pd.DataFrame(columns=_excluded_nonqualifying_columns())

    history = census.copy()
    history["dbh_mm"] = pd.to_numeric(history["dbh_mm"], errors="coerce")
    history["_stem"] = history["stem_rank"].map(_clean_stem)
    history["_passes_size_filter"] = [
        passes_size_filter(row.dbh_mm, row.genus, row.species, row.taxon_code)
        for row in history.itertuples()
    ]
    grouped = (
        history.groupby(["tree_uid", "_stem"], dropna=False)
        .agg(
            dbh_observation_count=("dbh_mm", lambda values: int(values.notna().sum())),
            qualifying_dbh_observation_count=("_passes_size_filter", "sum"),
            max_dbh_all=("dbh_mm", "max"),
            min_dbh_all=("dbh_mm", "min"),
        )
        .reset_index()
    )
    annotated = active.merge(
        grouped,
        left_on=["tree_uid", "stem"],
        right_on=["tree_uid", "_stem"],
        how="left",
    )
    has_dbh_history = annotated["dbh_observation_count"].fillna(0).gt(0)
    never_qualified = annotated["qualifying_dbh_observation_count"].fillna(0).eq(0)
    exclude_mask = has_dbh_history & never_qualified

    excluded = annotated.loc[exclude_mask].copy()
    if excluded.empty:
        excluded = pd.DataFrame(columns=_excluded_nonqualifying_columns())
    else:
        excluded["exclusion_reason"] = (
            "stem has DBH history but no measurement passing the taxon-specific size filter"
        )
        excluded = excluded[_excluded_nonqualifying_columns()]

    kept = annotated.loc[~exclude_mask, _active_columns()].copy()
    return kept.reset_index(drop=True), excluded.reset_index(drop=True)


def _found_rows_for_active_stems(found: pd.DataFrame, active: pd.DataFrame) -> pd.DataFrame:
    if found.empty or active.empty:
        return found.iloc[0:0].copy()
    rows = found.copy()
    rows["_stem"] = rows["stem_rank"].map(_clean_stem)
    active_keys = set(zip(active["tree_uid"].astype(str), active["stem"].astype(str)))
    return rows.loc[
        [(str(tree_uid), str(stem)) in active_keys for tree_uid, stem in zip(rows["tree_uid"], rows["_stem"])]
    ].copy()


def _duplicate_plot_tags(active: pd.DataFrame) -> pd.DataFrame:
    if active.empty:
        return pd.DataFrame(columns=["plot", "tag", "tree_uid_count", "tree_uids", "stems", "spp_values", "row_count"])
    grouped = active.groupby(["plot", "tag"]).agg(
        tree_uid_count=("tree_uid", "nunique"),
        tree_uids=("tree_uid", lambda values: "|".join(sorted(set(map(str, values))))),
        stems=("stem", lambda values: "|".join(map(str, values))),
        spp_values=("spp_latest", lambda values: "|".join(sorted(set(map(str, values))))),
        row_count=("tree_uid", "size"),
    )
    return grouped.reset_index().loc[lambda frame: frame["tree_uid_count"] > 1].sort_values(["plot", "tag"])


def _species_conflicts(active: pd.DataFrame) -> pd.DataFrame:
    if active.empty:
        return pd.DataFrame(columns=["plot", "tree_uid", "identity_tag", "tag", "spp_count", "spp_values", "stem_count", "stems"])
    grouped = active.groupby(["plot", "tree_uid", "identity_tag", "tag"]).agg(
        spp_count=("spp_latest", "nunique"),
        spp_values=("spp_latest", lambda values: "|".join(sorted(set(map(str, values))))),
        stem_count=("stem", "nunique"),
        stems=("stem", lambda values: "|".join(map(str, values))),
    )
    return grouped.reset_index().loc[lambda frame: frame["spp_count"] > 1].sort_values(["plot", "tag"])


def _same_survey_same_tag_duplicate_dbh(found: pd.DataFrame) -> pd.DataFrame:
    if found.empty:
        return pd.DataFrame(
            columns=[
                "survey_id",
                "plot",
                "public_tag",
                "tree_uid",
                "stem_rank",
                "dbh_mm",
                "health_observed",
                "taxon_code",
                "source_file",
                "source_row",
                "notes",
            ]
        )
    rows = found.copy()
    rows["_dbh_key"] = rows["dbh_mm"].round(1).astype("string")
    duplicate_mask = (
        rows.duplicated(["survey_id", "plot", "public_tag", "_dbh_key"], keep=False)
        & rows["dbh_mm"].notna()
    )
    columns = [
        "survey_id",
        "plot",
        "public_tag",
        "tree_uid",
        "stem_rank",
        "dbh_mm",
        "health_observed",
        "taxon_code",
        "source_file",
        "source_row",
        "notes",
    ]
    return rows.loc[duplicate_mask, columns].sort_values(["survey_id", "plot", "public_tag", "dbh_mm", "stem_rank"])


def _dhs(row: pd.Series | None) -> str:
    if row is None:
        return ""
    return "/".join(
        [
            _number_or_na(row.get("dbh_mm")),
            _number_or_na(row.get("health_observed")),
            _standing_or_na(row.get("standing_observed")),
        ]
    )


def _dhs_for_survey(group: pd.DataFrame, survey_id: str) -> str:
    return _dhs(_found_for_survey(group, survey_id))


def _hsp_for_survey(group: pd.DataFrame, survey_id: str) -> str:
    row = _found_for_survey(group, survey_id)
    if row is None:
        return ""
    hs = f"{_number_or_na(row.get('health_observed'))}/{_standing_or_na(row.get('standing_observed'))}"
    return hs + ("/p" if _standing_or_na(row.get("poison_ivy_observed")) == "1" else "")


def _found_for_survey(group: pd.DataFrame, survey_id: str) -> pd.Series | None:
    rows = group.loc[group["survey_id"] == survey_id].copy()
    if rows.empty:
        return None
    rows = rows.sort_values(["source_file", "source_row"])
    found_rows = rows.loc[rows["_found_signal"]]
    if found_rows.empty:
        return None
    return found_rows.iloc[-1]


def _latest_dbh_by_stem(census: pd.DataFrame) -> dict[tuple[str, str], float]:
    history = census.copy()
    history["dbh_mm"] = pd.to_numeric(history["dbh_mm"], errors="coerce")
    history = history.loc[history["dbh_mm"].notna()].copy()
    if history.empty:
        return {}
    history["_stem"] = history["stem_rank"].map(_clean_stem)
    history["_tree_uid"] = history["tree_uid"].astype(str)
    history = history.sort_values(["date", "survey_id", "source_file", "source_row"])
    latest = history.groupby(["_tree_uid", "_stem"], dropna=False).tail(1)
    return {
        (str(row["_tree_uid"]), str(row["_stem"])): float(row["dbh_mm"])
        for _, row in latest.iterrows()
    }


def _number_or_blank(value: object) -> str:
    if pd.isna(value):
        return ""
    numeric = float(value)
    return str(int(numeric)) if numeric.is_integer() else str(round(numeric, 1))


def _number_or_na(value: object) -> str:
    if pd.isna(value):
        return "NA"
    numeric = float(value)
    return str(int(numeric)) if numeric.is_integer() else str(round(numeric, 1))


def _standing_or_na(value: object) -> str:
    if pd.isna(value):
        return "NA"
    text = str(value).strip().lower()
    if text in {"true", "1", "1.0"}:
        return "1"
    if text in {"false", "0", "0.0"}:
        return "0"
    return str(value)


def _clean_tag(value: object) -> str:
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def _clean_stem(value: object) -> str:
    return _clean_tag(value)


def _natural_key(value: str) -> tuple[str, int | str]:
    return ("", int(value)) if value.isdigit() else (value, value)


def _json_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def _typst_with_data_path(template_text: str, data_path: str) -> str:
    lines = template_text.splitlines()
    if not lines:
        raise ValueError("Typst template is empty")
    lines[0] = f'#let data = json("{data_path}")'
    return "\n".join(lines) + "\n"


def _chunks(rows: list[dict[str, object]], size: int) -> list[list[dict[str, object]]]:
    if size <= 0:
        raise ValueError("rows_per_page must be positive")
    return [rows[index : index + size] for index in range(0, len(rows), size)] or [[]]


def _active_columns() -> list[str]:
    return [
        "plot",
        "tree_uid",
        "tag",
        "identity_tag",
        "stem",
        "spp_latest",
        "spp_values_last2",
        "latest_survey",
        "latest_dbh_mm",
        "reference_dbh_mm",
        "latest_health",
        "latest_standing",
        "dhs_1",
        "dhs_2",
        "last2_observation_count",
        "latest_notes",
        "latest_source_file",
        "latest_source_row",
    ]


def _excluded_nonqualifying_columns() -> list[str]:
    return _active_columns() + [
        "dbh_observation_count",
        "qualifying_dbh_observation_count",
        "max_dbh_all",
        "min_dbh_all",
        "exclusion_reason",
    ]
