"""Survey catalog helpers."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Sequence

from ..config import ConfigBundle


@dataclass(frozen=True)
class SurveyRecord:
    survey_id: str
    start: date
    end: date

    def contains(self, when: date) -> bool:
        return self.start <= when <= self.end


class SurveyCatalog:
    """Convenience catalog for mapping dates to survey ids."""

    def __init__(self, surveys: Sequence[SurveyRecord]):
        self._surveys = list(sorted(surveys, key=lambda record: record.start))
        self._starts = [record.start for record in self._surveys]
        self._index: Dict[str, SurveyRecord] = {record.survey_id: record for record in self._surveys}

    @classmethod
    def from_config(cls, config: ConfigBundle) -> "SurveyCatalog":
        records = [
            SurveyRecord(survey_id=survey.id, start=survey.start, end=survey.end)
            for survey in config.surveys.surveys
        ]
        return cls(records)

    def survey_for_date(self, when: date) -> Optional[str]:
        idx = bisect_right(self._starts, when) - 1
        if idx < 0 or idx >= len(self._surveys):
            return None
        record = self._surveys[idx]
        if record.contains(when):
            return record.survey_id
        return None

    def ordered_surveys(self) -> List[str]:
        return [record.survey_id for record in self._surveys]

    def get(self, survey_id: str) -> SurveyRecord:
        return self._index[survey_id]
