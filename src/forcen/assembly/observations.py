"""Observation assembly helpers."""

from __future__ import annotations

import hashlib
from typing import List

from ..config import ConfigBundle
from ..transactions.models import MeasurementRow
from .survey import SurveyCatalog


def assemble_observations(
    measurements: List[MeasurementRow],
    config: ConfigBundle,
    tx_id: str,
) -> List[dict]:
    """Transform transaction measurements into normalized observation rows."""

    catalog = SurveyCatalog.from_config(config)
    observations: List[dict] = []
    for row in measurements:
        survey_id = catalog.survey_for_date(row.date)
        if survey_id is None:
            # Should not happen due to earlier validation, but fail closed.
            raise ValueError(f"no survey covers date {row.date.isoformat()}")
        obs_id = _observation_id(tx_id, row)
        observations.append(
            {
                "obs_id": obs_id,
                "survey_id": survey_id,
                "date": row.date.isoformat(),
                "site": row.site,
                "plot": row.plot,
                "tag": row.tag,
                "dbh_mm": row.dbh_mm,
                "health": row.health,
                "standing": row.standing,
                "notes": row.notes,
                "origin": row.origin,
                "source_tx": tx_id,
                "tree_uid": row.tree_uid,
                "genus": row.genus,
                "species": row.species,
                "code": row.code,
            }
        )
    return observations


def _observation_id(tx_id: str, row: MeasurementRow) -> str:
    seed = f"{tx_id}:{row.row_number}:{row.site}:{row.plot}:{row.tag}:{row.date.isoformat()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()
