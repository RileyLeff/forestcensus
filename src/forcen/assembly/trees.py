"""Tree timeline assembly helpers."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, Iterable, List, Optional

from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from .survey import SurveyCatalog


def generate_implied_rows(
    measurements: Iterable[MeasurementRow], config: ConfigBundle
) -> List[MeasurementRow]:
    catalog = SurveyCatalog.from_config(config)
    surveys = catalog.ordered_surveys()
    if not surveys:
        return []

    drop_after = config.validation.drop_after_absent_surveys
    tree_map: Dict[str, Dict[str, List[MeasurementRow]]] = defaultdict(lambda: defaultdict(list))

    for row in measurements:
        if row.tree_uid is None:
            continue
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            continue
        tree_map[row.tree_uid][survey_id].append(row)

    implied_rows: List[MeasurementRow] = []

    for tree_uid, survey_rows in tree_map.items():
        last_real_row: Optional[MeasurementRow] = None
        last_presence_index: Optional[int] = None

        for idx, survey_id in enumerate(surveys):
            rows = survey_rows.get(survey_id)
            if rows:
                # Use the latest dated row for metadata fallback.
                last_real_row = max(rows, key=lambda row: row.date)
                last_presence_index = idx

        if last_presence_index is None or last_real_row is None:
            continue

        trailing_missing = len(surveys) - (last_presence_index + 1)
        if trailing_missing < drop_after:
            continue

        implied_index = last_presence_index + 1
        implied_survey_id = surveys[implied_index]
        survey_record = catalog.get(implied_survey_id)

        implied_rows.append(
            MeasurementRow(
                row_number=0,
                site=last_real_row.site,
                plot=last_real_row.plot,
                tag=last_real_row.tag,
                date=survey_record.start,
                dbh_mm=None,
                health=0,
                standing=False,
                notes="",
                genus=last_real_row.genus,
                species=last_real_row.species,
                code=last_real_row.code,
                origin="implied",
                normalization_flags=[],
                raw={},
                tree_uid=tree_uid,
                public_tag=last_real_row.public_tag or last_real_row.tag,
                source_tx=last_real_row.source_tx,
            )
        )

    return implied_rows
