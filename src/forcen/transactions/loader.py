"""Load transaction directories into structured data."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from ..dsl import Command, DSLParser
from .exceptions import TransactionFormatError
from .models import SurveyMeta, TransactionData
from .normalization import NormalizationConfig, load_measurements


UPDATES_FILENAME = "updates.tdl"
MEASUREMENTS_FILENAME = "measurements.csv"
SURVEY_META_FILENAME = "survey_meta.toml"


def load_transaction(
    path: Path, *, normalization: NormalizationConfig = NormalizationConfig()
) -> TransactionData:
    path = Path(path)
    if not path.is_dir():
        raise TransactionFormatError(path=path, message="transaction directory not found")

    measurements = load_measurements(path / MEASUREMENTS_FILENAME, normalization)
    commands = _load_updates(path / UPDATES_FILENAME)
    survey_meta = _load_survey_meta(path / SURVEY_META_FILENAME)

    return TransactionData(
        path=path,
        measurements=measurements,
        commands=commands,
        survey_meta=survey_meta,
    )


def _load_updates(path: Path) -> List[Command]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    parser = DSLParser()
    return parser.parse(text)


def _load_survey_meta(path: Path) -> Optional[SurveyMeta]:
    if not path.exists():
        return None
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise TransactionFormatError(path=path, message=f"invalid TOML ({exc})") from exc
    return SurveyMeta(data=data)
