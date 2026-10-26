"""Adapters from archived census files to canonical observation events."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from typing import Callable

import pandas as pd

from .config import Config, SourceInput
from .decisions import apply_decisions
from .domain import has_direct_observation
from .schema import EVENT_COLUMNS


def load_raw_historical_events(raw_dir: str | Path, config: Config) -> pd.DataFrame:
    raw_dir = Path(raw_dir)
    frames = []
    if config.source_inputs:
        for source in config.source_inputs:
            path = _resolve_source_path(source, raw_dir, config)
            if not path.exists():
                if source.required:
                    raise FileNotFoundError(path)
                continue
            frames.append(_adapt_configured_source(path, config, source))
    else:
        adapters: dict[str, Callable[[Path, Config], pd.DataFrame]] = {
            "2023_and_prior.csv": adapt_2023_and_prior,
            "2024_spring.csv": adapt_2024_spring,
            "2024_fall.csv": adapt_2024_fall,
            "2025_spring.csv": adapt_2025_spring,
        }
        for filename, adapter in adapters.items():
            path = raw_dir / filename
            if not path.exists():
                raise FileNotFoundError(path)
            frames.append(adapter(path, config))
    events = pd.concat(frames, ignore_index=True)
    events["identity_tag"] = events["public_tag"]
    events["identity_label"] = ""
    events["correction_notes"] = ""
    return events[EVENT_COLUMNS]


def load_historical_events(
    raw_dir: str | Path,
    config: Config,
    *,
    apply_configured_decisions: bool = True,
) -> pd.DataFrame:
    events = load_raw_historical_events(raw_dir, config)
    if apply_configured_decisions:
        events = apply_decisions(events, config)
    return events[EVENT_COLUMNS]


def _resolve_source_path(source: SourceInput, raw_dir: Path, config: Config) -> Path:
    if source.path.is_absolute():
        return source.path
    if source.base == "raw_dir":
        return raw_dir / source.path
    if source.base == "config":
        return config.config_dir / source.path
    if source.base == "project":
        return config.config_dir.parent / source.path
    raise ValueError(f"Unknown source base {source.base!r} for {source.id}")


def _adapt_configured_source(path: Path, config: Config, source: SourceInput) -> pd.DataFrame:
    if source.adapter == "2023_and_prior":
        frame = adapt_2023_and_prior(path, config)
    elif source.adapter == "2024_spring":
        frame = adapt_2024_spring(path, config)
    elif source.adapter == "2024_fall":
        frame = adapt_2024_fall(path, config)
    elif source.adapter == "recent_import":
        frame = adapt_recent_import(path, config, origin=source.origin)
    else:
        raise ValueError(f"Unknown source adapter {source.adapter!r} for {source.id}")
    return frame


def adapt_2023_and_prior(path: Path, config: Config) -> pd.DataFrame:
    df = _read_csv(path)
    out = pd.DataFrame()
    out["source_row"] = df.index + 2
    out["source_file"] = path.name
    out["site"] = "BRNV"
    out["zone"] = df["level"].map(_clean_text).str.upper()
    out["plot"] = df["plot"].map(_clean_plot)
    out["tree_number"] = df["tree_number"].map(_clean_int_string)
    out["public_tag"] = out["tree_number"]
    out["datasheet_slot"] = df["trunk_number"].map(_clean_int_string)

    parsed_dates = []
    for _, row in df.iterrows():
        year = int(float(_coalesce(row.get("year"), "0")))
        month = _to_number(row.get("month"))
        day = _to_number(row.get("day"))
        parsed_dates.append(date(year, int(month or 6), int(day or 15)))
    out["date"] = parsed_dates
    out["survey_id"] = out["date"].map(config.survey_for_date)

    genus_species = df["spp"].map(lambda value: _split_legacy_taxon(value, config))
    out["genus"] = genus_species.map(lambda item: item[0])
    out["species"] = genus_species.map(lambda item: item[1])
    out["taxon_code"] = [_taxon_code(g, s) for g, s in zip(out["genus"], out["species"])]

    out["dbh_mm"] = df["dbh_mm"].map(_to_number)
    out["health_observed"] = df["health"].map(_to_number)
    out["alive_observed"] = df["alive"].map(_to_bool)
    out["standing_observed"] = df["standing"].map(_to_bool)
    out["notes"] = df.get("notes", "").map(_clean_text)
    out["field_status"] = out.apply(_classify_status, axis=1)
    out["origin"] = "historical"
    return _drop_bad_tree_numbers(out)


def adapt_2024_spring(path: Path, config: Config) -> pd.DataFrame:
    df = _read_csv(path)
    out = _base_recent_frame(df, path, config, survey_id="May_2024")
    out["date"] = _parse_mixed_dates(df["date"])
    out["survey_id"] = df["survey_id"].map(_clean_text)
    return _finish_recent_frame(df, out, config)


def adapt_2024_fall(path: Path, config: Config) -> pd.DataFrame:
    df = _read_csv(path)
    out = _base_recent_frame(df, path, config, survey_id="October_2024")
    survey = next(item for item in config.surveys if item.id == "October_2024")
    out["date"] = survey.start
    out["survey_id"] = "October_2024"

    genus = df.apply(lambda row: _prefer(row.get("new_genus"), row.get("genus")), axis=1)
    species = df.apply(lambda row: _prefer(row.get("new_species"), row.get("spp")), axis=1)
    out["genus"] = genus.map(lambda value: _canonical_genus(value, config))
    out["species"] = [
        _canonical_species(species_value, config, genus_value)
        for species_value, genus_value in zip(species, out["genus"])
    ]
    out["dbh_mm"] = df["dbh"].map(_to_number)
    out["datasheet_slot"] = df["stem_number"].map(_clean_int_string)
    out["notes"] = df.get("notes", "").map(_clean_text)
    out["health_observed"] = df["health"].map(_to_number)
    out["alive_observed"] = df["alive"].map(_to_bool)
    out["standing_observed"] = df["standing"].map(_to_bool)
    out["taxon_code"] = [_taxon_code(g, s) for g, s in zip(out["genus"], out["species"])]
    out["field_status"] = out.apply(_classify_status, axis=1)
    out["origin"] = "historical"
    return _drop_bad_tree_numbers(out)


def adapt_2025_spring(path: Path, config: Config) -> pd.DataFrame:
    return adapt_recent_import(path, config, origin="historical")


def adapt_recent_import(path: Path, config: Config, *, origin: str) -> pd.DataFrame:
    df = _read_csv(path)
    out = pd.DataFrame()
    out["source_row"] = df.index + 2
    out["source_file"] = path.name
    out["survey_id"] = df["survey_id"].map(_clean_text)
    out["date"] = _parse_mixed_dates(df["date"])
    out["site"] = df["site"].map(_clean_text).replace("", "BRNV")
    out["zone"] = df["zone"].map(_clean_text).str.upper()
    out["plot"] = [_recent_plot(zone, plot) for zone, plot in zip(out["zone"], df["plot"])]
    out["tree_number"] = df["tree_number"].map(_clean_int_string)
    out["public_tag"] = out["tree_number"]
    out["datasheet_slot"] = df["trunk_number"].map(_clean_int_string)
    out["genus"] = df["genus"].map(lambda value: _canonical_genus(value, config))
    out["species"] = [
        _canonical_species(species_value, config, genus_value)
        for species_value, genus_value in zip(df["spp"], out["genus"])
    ]
    out["taxon_code"] = [_taxon_code(g, s) for g, s in zip(out["genus"], out["species"])]
    out["dbh_mm"] = df["dbh_mm"].map(_to_number)
    out["health_observed"] = df["health"].map(_to_number)
    out["alive_observed"] = df["alive"].map(_to_bool)
    out["standing_observed"] = df["standing"].map(_to_bool)
    out["notes"] = df.get("notes", "").map(_clean_text)
    out["field_status"] = out.apply(_classify_status, axis=1)
    out["origin"] = origin
    return _drop_bad_tree_numbers(out)


def _base_recent_frame(
    df: pd.DataFrame, path: Path, config: Config, survey_id: str
) -> pd.DataFrame:
    out = pd.DataFrame()
    out["source_row"] = df.index + 2
    out["source_file"] = path.name
    out["site"] = df.get("site", "BRNV")
    out["site"] = out["site"].map(_clean_text).replace("", "BRNV")
    out["zone"] = df["zone"].map(_clean_text).str.upper()
    out["plot"] = [
        _plot_from_zone_number(zone, plot)
        for zone, plot in zip(out["zone"], df["plot"])
    ]
    out["tree_number"] = df["tree_number"].map(_clean_int_string)
    out["public_tag"] = out["tree_number"]
    out["datasheet_slot"] = df.get("trunk_number", df.get("stem_number")).map(_clean_int_string)
    out["survey_id"] = survey_id
    return out


def _finish_recent_frame(
    df: pd.DataFrame, out: pd.DataFrame, config: Config
) -> pd.DataFrame:
    out["genus"] = df["genus"].map(lambda value: _canonical_genus(value, config))
    out["species"] = [
        _canonical_species(species_value, config, genus_value)
        for species_value, genus_value in zip(df["spp"], out["genus"])
    ]
    out["taxon_code"] = [_taxon_code(g, s) for g, s in zip(out["genus"], out["species"])]
    out["dbh_mm"] = df["dbh_mm"].map(_to_number)
    out["health_observed"] = df["health"].map(_to_number)
    out["alive_observed"] = df["alive"].map(_to_bool)
    out["standing_observed"] = df["standing"].map(_to_bool)
    out["notes"] = df.get("notes", "").map(_clean_text)
    out["field_status"] = out.apply(_classify_status, axis=1)
    out["origin"] = "historical"
    return _drop_bad_tree_numbers(out)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype="string", keep_default_na=False)


def _parse_mixed_dates(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, errors="coerce", format="mixed").dt.date


def _clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"na", "nan", "none"}:
        return ""
    return text


def _clean_plot(value: object) -> str:
    text = _clean_text(value).upper()
    if len(text) >= 2 and text[0] in {"L", "M", "H", "R"}:
        return text
    return text


def _plot_from_zone_number(zone: object, plot: object) -> str:
    zone_text = _clean_text(zone).upper()
    plot_text = _clean_int_string(plot)
    if not zone_text or not plot_text:
        return ""
    return f"{zone_text}{plot_text}"


def _recent_plot(zone: object, plot: object) -> str:
    plot_text = _clean_plot(plot)
    if len(plot_text) >= 2 and plot_text[0] in {"L", "M", "H", "R"}:
        return plot_text
    return _plot_from_zone_number(zone, plot)


def _clean_int_string(value: object) -> str:
    number = _to_number(value)
    if pd.isna(number):
        return ""
    if float(number).is_integer():
        return str(int(number))
    return str(number)


def _to_number(value: object) -> float | None:
    text = _clean_text(value)
    if text == "":
        return None
    number = pd.to_numeric(text, errors="coerce")
    if pd.isna(number):
        return None
    return float(number)


def _to_bool(value: object) -> bool | None:
    text = _clean_text(value).lower()
    if text == "":
        return None
    if text in {"true", "t", "1", "yes", "y"}:
        return True
    if text in {"false", "f", "0", "no", "n"}:
        return False
    return None


def _split_legacy_taxon(value: object, config: Config) -> tuple[str, str]:
    text = _clean_text(value)
    if text == "Unidentifiable":
        text = "Unidentifiable spp."
    parts = text.split()
    if len(parts) >= 2:
        genus = _canonical_genus(parts[0], config)
        return genus, _canonical_species(parts[1], config, genus)
    genus = _canonical_genus(parts[0] if parts else "", config)
    return genus, config.unknown_species


def _canonical_genus(value: object, config: Config) -> str:
    text = _clean_text(value)
    if not text:
        return config.unknown_genus
    return config.genus_aliases.get(text.lower(), text)


def _canonical_species(value: object, config: Config, genus: str = "") -> str:
    text = _clean_text(value)
    if not text:
        return config.unknown_species
    genus_aliases = config.species_aliases_by_genus.get(genus.lower(), {})
    if text.lower() in genus_aliases:
        return genus_aliases[text.lower()]
    return config.species_aliases.get(text.lower(), text)


def _taxon_code(genus: str, species: str) -> str:
    return f"{genus[:3]}{species[:3]}".upper().replace(".", "")


def _classify_status(row: pd.Series) -> str:
    dbh = row.get("dbh_mm")
    health = row.get("health_observed")
    alive = row.get("alive_observed")
    standing = row.get("standing_observed")

    # Presence is independent of health; conflicting prose is diagnostic evidence.
    if not has_direct_observation(dbh, health, standing):
        return "not_found"
    if pd.notna(health) and health > 0:
        return "observed_alive"
    if alive is True:
        return "observed_alive"
    if pd.notna(health) and health == 0:
        return "observed_dead"
    if alive is False:
        return "observed_dead"
    return "observed_unknown"


def _drop_bad_tree_numbers(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df["tree_number"].map(bool)].copy()


def _coalesce(value: object, fallback: object) -> object:
    text = _clean_text(value)
    return text if text else fallback


def _prefer(primary: object, fallback: object) -> object:
    return primary if _clean_text(primary) else fallback
