"""Pydantic models describing configuration files."""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Literal

from pydantic import BaseModel, Field, model_validator


class SpeciesEntry(BaseModel):
    genus: str
    species: str
    code: str

    @model_validator(mode="after")
    def ensure_code_matches(self) -> "SpeciesEntry":
        expected = (self.genus[:3] + self.species[:3]).upper()
        if self.code != expected:
            raise ValueError("code must equal upper(genus[0:3]+species[0:3])")
        return self


class TaxonomyConfig(BaseModel):
    species: List[SpeciesEntry]
    enforce_no_synonyms: bool = True

    @model_validator(mode="after")
    def ensure_unique_triplets(self) -> "TaxonomyConfig":
        seen_codes: Dict[str, SpeciesEntry] = {}
        seen_pairs: Dict[tuple[str, str], SpeciesEntry] = {}
        for entry in self.species:
            if entry.code in seen_codes:
                raise ValueError(f"duplicate code {entry.code}")
            pair = (entry.genus.lower(), entry.species.lower())
            if pair in seen_pairs and self.enforce_no_synonyms:
                raise ValueError(
                    f"duplicate genus/species pair {entry.genus} {entry.species}"
                )
            seen_codes[entry.code] = entry
            seen_pairs[pair] = entry
        return self


class SiteConfig(BaseModel):
    zone_order: List[str]
    plots: List[str]
    girdling: Dict[str, date] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_fields(self) -> "SiteConfig":
        if not self.zone_order:
            raise ValueError("zone_order must not be empty")
        if not self.plots:
            raise ValueError("plots must not be empty")
        if len(set(self.plots)) != len(self.plots):
            raise ValueError("plots must be unique per site")
        return self


class SitesConfig(BaseModel):
    sites: Dict[str, SiteConfig]

    @model_validator(mode="after")
    def ensure_non_empty(self) -> "SitesConfig":
        if not self.sites:
            raise ValueError("at least one site must be defined")
        return self


class SurveyWindow(BaseModel):
    id: str
    start: date
    end: date

    @model_validator(mode="after")
    def ensure_order(self) -> "SurveyWindow":
        if self.end < self.start:
            raise ValueError("end must not be before start")
        return self


class SurveysConfig(BaseModel):
    surveys: List[SurveyWindow]

    @model_validator(mode="after")
    def check_ordering(self) -> "SurveysConfig":
        seen_ids: Dict[str, SurveyWindow] = {}
        for idx, window in enumerate(self.surveys):
            if window.id in seen_ids:
                raise ValueError(f"surveys[{idx}].id duplicates survey id {window.id}")
            if idx > 0:
                prev = self.surveys[idx - 1]
                if window.start <= prev.end:
                    raise ValueError(
                        "surveys[{}].start overlaps surveys[{}].end ({} <= {})".format(
                            idx,
                            idx - 1,
                            window.start,
                            prev.end,
                        )
                    )
            seen_ids[window.id] = window
        return self


class ValidationConfig(BaseModel):
    rounding: Literal["half_up"]
    dbh_pct_warn: float
    dbh_pct_error: float
    dbh_abs_floor_warn_mm: int
    dbh_abs_floor_error_mm: int
    retag_delta_pct: float
    new_tree_flag_min_dbh_mm: int
    drop_after_absent_surveys: int

    @model_validator(mode="after")
    def check_thresholds(self) -> "ValidationConfig":
        if self.dbh_pct_warn <= 0 or self.dbh_pct_error <= 0:
            raise ValueError("dbh_pct thresholds must be positive")
        if self.dbh_pct_warn >= self.dbh_pct_error:
            raise ValueError("dbh_pct_warn must be less than dbh_pct_error")
        if self.dbh_abs_floor_warn_mm < 0 or self.dbh_abs_floor_error_mm < 0:
            raise ValueError("dbh_abs_floor thresholds must be >= 0")
        if self.dbh_abs_floor_warn_mm >= self.dbh_abs_floor_error_mm:
            raise ValueError("dbh_abs_floor_warn_mm must be < dbh_abs_floor_error_mm")
        if self.retag_delta_pct <= 0:
            raise ValueError("retag_delta_pct must be positive")
        if self.new_tree_flag_min_dbh_mm <= 0:
            raise ValueError("new_tree_flag_min_dbh_mm must be positive")
        if self.drop_after_absent_surveys < 2:
            raise ValueError("drop_after_absent_surveys must be >= 2")
        return self


class DatasheetsConfig(BaseModel):
    show_previous_surveys: int
    sort: Literal["public_tag_numeric_asc"]
    show_zombie_asterisk: bool

    @model_validator(mode="after")
    def ensure_previous_surveys(self) -> "DatasheetsConfig":
        if self.show_previous_surveys < 0:
            raise ValueError("show_previous_surveys must be >= 0")
        return self


class ConfigBundle(BaseModel):
    taxonomy: TaxonomyConfig
    sites: SitesConfig
    surveys: SurveysConfig
    validation: ValidationConfig
    datasheets: DatasheetsConfig
