"""Derived tree-level outputs (trees_view, retag suggestions)."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from .survey import SurveyCatalog


def build_tree_view(
    rows: Iterable[MeasurementRow], catalog: SurveyCatalog
) -> List[dict]:
    selected: Dict[Tuple[str, str], MeasurementRow] = {}

    for row in rows:
        if row.tree_uid is None:
            continue
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        key = (row.tree_uid, survey_id)
        current = selected.get(key)
        if current is None:
            selected[key] = row
            continue
        current_priority = (current.origin != "implied", current.date)
        new_priority = (row.origin != "implied", row.date)
        if new_priority > current_priority:
            selected[key] = row

    records: List[dict] = []
    for (tree_uid, survey_id), row in selected.items():
        records.append(
            {
                "tree_uid": tree_uid,
                "survey_id": survey_id,
                "public_tag": row.tag,
                "site": row.site,
                "plot": row.plot,
                "genus": row.genus,
                "species": row.species,
                "code": row.code,
                "origin": row.origin,
            }
        )

    records.sort(key=lambda rec: (rec["survey_id"], rec["site"], rec["plot"], rec["public_tag"]))
    return records


def build_retag_suggestions(
    rows: Iterable[MeasurementRow], config: ConfigBundle
) -> List[dict]:
    catalog = SurveyCatalog.from_config(config)
    surveys = catalog.ordered_surveys()
    if len(surveys) < 2:
        return []

    threshold_dbh = config.validation.new_tree_flag_min_dbh_mm
    delta_pct = config.validation.retag_delta_pct

    by_tree: Dict[str, Dict[str, List[MeasurementRow]]] = defaultdict(lambda: defaultdict(list))
    first_seen: Dict[str, str] = {}

    for row in rows:
        if row.tree_uid is None or row.origin == "implied":
            continue
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        by_tree[row.tree_uid][survey_id].append(row)
        first_seen.setdefault(row.tree_uid, survey_id)

    suggestions: List[dict] = []

    for idx in range(1, len(surveys)):
        prev_survey = surveys[idx - 1]
        curr_survey = surveys[idx]
        prev_start = catalog.get(prev_survey).start
        curr_start = catalog.get(curr_survey).start

        lost_entries: List[tuple] = []
        new_entries: List[tuple] = []

        for tree_uid, survey_rows in by_tree.items():
            prev_rows = survey_rows.get(prev_survey)
            curr_rows = survey_rows.get(curr_survey)

            if prev_rows and not curr_rows:
                lost_row = max(prev_rows, key=lambda r: (r.dbh_mm or 0, r.health or 0))
                lost_entries.append((tree_uid, lost_row))

            if not prev_rows and curr_rows and first_seen.get(tree_uid) == curr_survey:
                new_row = max(curr_rows, key=lambda r: (r.dbh_mm or 0, r.health or 0))
                if (new_row.dbh_mm or 0) >= threshold_dbh:
                    new_entries.append((tree_uid, new_row))

        for lost_tree_uid, lost_row in lost_entries:
            for new_tree_uid, new_row in new_entries:
                if lost_row.site != new_row.site or lost_row.plot != new_row.plot:
                    continue
                lost_dbh = lost_row.dbh_mm or 0
                new_dbh = new_row.dbh_mm or 0
                if lost_dbh == 0 or new_dbh == 0:
                    continue
                delta = abs(lost_dbh - new_dbh)
                allowed = delta_pct * max(lost_dbh, new_dbh)
                if delta > allowed:
                    continue

                suggestion = {
                    "survey_id": curr_survey,
                    "plot": f"{new_row.site}/{new_row.plot}",
                    "lost_tree_uid": lost_tree_uid,
                    "lost_public_tag": lost_row.tag,
                    "lost_max_dbh_mm": lost_dbh,
                    "new_tree_uid": new_tree_uid,
                    "new_public_tag": new_row.tag,
                    "new_max_dbh_mm": new_dbh,
                    "delta_mm": delta,
                    "delta_pct": round(delta / max(lost_dbh, new_dbh), 4),
                    "suggested_alias_line": (
                        f"ALIAS {new_row.site}/{new_row.plot}/{new_row.tag} "
                        f"TO {lost_tree_uid} PRIMARY EFFECTIVE {curr_start.isoformat()}"
                    ),
                }
                suggestions.append(suggestion)

    suggestions.sort(key=lambda rec: (rec["survey_id"], rec["plot"], rec["new_public_tag"]))
    return suggestions
