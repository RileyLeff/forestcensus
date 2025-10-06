"""Functions for reading and validating configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Type

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from pydantic import BaseModel, ValidationError

from ..exceptions import ConfigError
from .models import (
    ConfigBundle,
    DatasheetsConfig,
    SitesConfig,
    SurveysConfig,
    TaxonomyConfig,
    ValidationConfig,
)


class ConfigFiles:
    """Canonical configuration filenames."""

    TAXONOMY = "taxonomy.toml"
    SITES = "sites.toml"
    SURVEYS = "surveys.toml"
    VALIDATION = "validation.toml"
    DATASHEETS = "datasheets.toml"


def load_config_bundle(root: Path) -> ConfigBundle:
    """Load all configuration files from *root* directory."""

    root = Path(root)
    taxonomy = _load_toml(root / ConfigFiles.TAXONOMY, TaxonomyConfig)
    sites = _load_toml(root / ConfigFiles.SITES, SitesConfig)
    surveys = _load_toml(root / ConfigFiles.SURVEYS, SurveysConfig)
    validation = _load_toml(root / ConfigFiles.VALIDATION, ValidationConfig)
    datasheets = _load_toml(root / ConfigFiles.DATASHEETS, DatasheetsConfig)
    return ConfigBundle(
        taxonomy=taxonomy,
        sites=sites,
        surveys=surveys,
        validation=validation,
        datasheets=datasheets,
    )


def _load_toml(path: Path, model: Type[BaseModel]) -> Any:
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError as exc:
        raise ConfigError(path, "file not found") from exc
    except (tomllib.TOMLDecodeError, OSError) as exc:
        raise ConfigError(path, f"failed to read TOML: {exc}") from exc

    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(path, _format_validation_errors(exc)) from exc


def _format_validation_errors(error: ValidationError) -> str:
    messages = []
    for err in error.errors(include_context=False):
        loc = _format_location(err.get("loc", ()))
        msg = err.get("msg", "invalid value")
        if loc:
            messages.append(f"{loc}: {msg}")
        else:
            messages.append(msg)
    return "; ".join(messages)


def _format_location(loc: tuple[Any, ...]) -> str:
    if not loc:
        return ""

    parts: list[str] = []
    for entry in loc:
        if isinstance(entry, int):
            if not parts:
                parts.append(f"[{entry}]")
            else:
                parts[-1] = parts[-1] + f"[{entry}]"
        else:
            parts.append(str(entry))
    return ".".join(parts)
