"""Datasheets scaffold generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from ..assembly.reassemble import assemble_dataset
from ..assembly.survey import SurveyCatalog
from ..config import ConfigBundle, load_config_bundle
from ..exceptions import ForcenError
from ..ledger.storage import Ledger
from ..transactions.models import MeasurementRow


class DatasheetsError(ForcenError):
    """Raised for datasheet generation failures."""


@dataclass
class DatasheetOptions:
    survey_id: str
    site: str
    plot: str
    output_dir: Path


def generate_datasheet(
    config_dir: Path,
    workspace: Path,
    options: DatasheetOptions,
) -> Path:
    """Generate datasheet context JSON and return the output path."""

    config = load_config_bundle(config_dir)
    ledger = Ledger(workspace)

    raw_rows = ledger.load_raw_measurements()
    if not raw_rows:
        raise DatasheetsError("No observations found; submit transactions before generating datasheets")

    commands = ledger.load_commands()
    assembled_rows = assemble_dataset(raw_rows, commands, config)
    context = _build_context(
        assembled_rows,
        config,
        options.survey_id,
        options.site,
        options.plot,
    )

    options.output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"context_{options.site}_{options.plot}_{options.survey_id}.json"
    output_path = options.output_dir / filename
    output_path.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _build_context(
    rows: Sequence[MeasurementRow],
    config: ConfigBundle,
    survey_id: str,
    site: str,
    plot: str,
) -> Dict[str, object]:
    catalog = SurveyCatalog.from_config(config)
    ordered_surveys = catalog.ordered_surveys()
    if survey_id not in ordered_surveys:
        raise DatasheetsError(f"Unknown survey id {survey_id}")

    try:
        survey_index = ordered_surveys.index(survey_id)
    except ValueError:  # pragma: no cover - guarded above
        raise DatasheetsError(f"Unknown survey id {survey_id}") from None

    previous_ids = [
        ordered_surveys[idx]
        for idx in (survey_index - 1, survey_index - 2)
        if idx >= 0
    ]

    if not previous_ids:
        raise DatasheetsError(f"Survey {survey_id} has no prior surveys; nothing to generate")

    target_record = catalog.get(survey_id)

    filtered_rows: List[MeasurementRow] = []
    for row in rows:
        if row.tree_uid is None:
            continue
        if row.site != site or row.plot != plot:
            continue
        if catalog.survey_for_date(row.date) is None:
            continue
        filtered_rows.append(row)

    if not filtered_rows:
        raise DatasheetsError(f"No observations found for site={site}, plot={plot}")

    tags_used = sorted(
        {
            (row.public_tag or row.tag)
            for row in filtered_rows
            if row.origin != "implied"
        },
        key=_tag_sort_key,
    )

    trees = _prepare_trees(filtered_rows, catalog, previous_ids, target_record.end)
    if not trees:
        raise DatasheetsError("No eligible trees found for datasheet (check prior surveys)")

    trees.sort(key=lambda entry: _tag_sort_key(entry["public_tag"]))

    return {
        "survey_id": survey_id,
        "site": site,
        "plot": plot,
        "tags_used": tags_used,
        "trees": trees,
        "previous_surveys": previous_ids,
    }


def _prepare_trees(
    rows: Iterable[MeasurementRow],
    catalog: SurveyCatalog,
    previous_ids: Sequence[str],
    target_end,
) -> List[Dict[str, object]]:
    from collections import defaultdict

    per_tree: Dict[str, Dict[str, List[MeasurementRow]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        per_tree[row.tree_uid][survey_id].append(row)

    ordered_surveys = catalog.ordered_surveys()

    entries: List[Dict[str, object]] = []

    for tree_uid, survey_map in per_tree.items():
        if not _has_real_rows(survey_map, previous_ids):
            continue

        public_tag = _public_tag_as_of(survey_map, target_end)
        zombie_ever = _compute_zombie_flag(survey_map, ordered_surveys)

        prev1_id = previous_ids[0] if previous_ids else None
        prev2_id = previous_ids[1] if len(previous_ids) > 1 else None

        prev1_rows = _load_rows_for_survey(survey_map, prev1_id)
        prev2_rows = _load_rows_for_survey(survey_map, prev2_id)

        stems_source = prev1_rows if prev1_rows else prev2_rows

        entry = {
            "tree_uid": tree_uid,
            "public_tag": public_tag,
            "zombie_ever": zombie_ever,
            "stems_next": _format_stems_with_notes(stems_source),
            "dhs1": _format_stems(prev1_rows),
            "dhs1_marked": bool(prev1_rows),
            "dhs2": _format_stems(prev2_rows),
            "dhs2_marked": bool(prev2_rows),
        }
        entries.append(entry)

    return entries


def _has_real_rows(
    survey_map: Dict[str, List[MeasurementRow]], survey_ids: Sequence[str]
) -> bool:
    for survey_id in survey_ids:
        for row in survey_map.get(survey_id, []):
            if row.origin != "implied":
                return True
    return False


def _public_tag_as_of(
    survey_map: Dict[str, List[MeasurementRow]],
    target_end,
) -> str:
    candidates: List[MeasurementRow] = []
    for rows in survey_map.values():
        for row in rows:
            if row.date <= target_end:
                candidates.append(row)

    if not candidates:
        for rows in survey_map.values():
            candidates.extend(rows)

    if not candidates:
        return ""

    candidates.sort(key=lambda row: (row.date, row.origin != "implied"), reverse=True)
    chosen = candidates[0]
    return chosen.public_tag or chosen.tag


def _compute_zombie_flag(
    survey_map: Dict[str, List[MeasurementRow]],
    ordered_surveys: Sequence[str],
) -> bool:
    seen_dead = False
    for survey_id in ordered_surveys:
        rows = [
            row
            for row in survey_map.get(survey_id, [])
            if row.origin != "implied"
        ]
        if not rows:
            continue
        alive = any((row.health or 0) > 0 for row in rows)
        if not alive:
            seen_dead = True
        elif seen_dead:
            return True
    return False


def _load_rows_for_survey(
    survey_map: Dict[str, List[MeasurementRow]],
    survey_id: Optional[str],
) -> List[MeasurementRow]:
    if survey_id is None:
        return []
    rows = [
        row
        for row in survey_map.get(survey_id, [])
        if row.origin != "implied"
    ]
    rows.sort(key=_stem_sort_key)
    return rows


def _stem_sort_key(row: MeasurementRow) -> tuple:
    dbh = row.dbh_mm if row.dbh_mm is not None else -1
    health = row.health if row.health is not None else -1
    return (-dbh, -health, row.row_number)


def _format_stems(rows: List[MeasurementRow]) -> List[Dict[str, object]]:
    payload: List[Dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        payload.append(
            {
                "rank": idx,
                "dbh_mm": row.dbh_mm,
                "health": row.health,
                "standing": row.standing,
            }
        )
    return payload


def _format_stems_with_notes(rows: List[MeasurementRow]) -> List[Dict[str, object]]:
    payload: List[Dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        payload.append(
            {
                "rank": idx,
                "dbh_mm": row.dbh_mm,
                "health": row.health,
                "standing": row.standing,
                "notes": row.notes,
            }
        )
    return payload


def _tag_sort_key(tag: str) -> tuple:
    if tag is None:
        return (1, "")
    try:
        return (0, int(tag))
    except (TypeError, ValueError):
        return (1, str(tag))
