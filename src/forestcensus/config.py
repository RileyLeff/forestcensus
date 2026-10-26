"""Configuration loading for the forest census pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import tomllib

from .errors import ConfigError


@dataclass(frozen=True)
class Survey:
    id: str
    start: date
    end: date


@dataclass(frozen=True)
class RowCorrection:
    note: str
    match: dict[str, object]
    set: dict[str, object]


@dataclass(frozen=True)
class RowExclusion:
    note: str
    match: dict[str, object]


@dataclass(frozen=True)
class TaxonOverride:
    note: str
    match: dict[str, object]
    genus: str
    species: str
    scope: str = "tree"


@dataclass(frozen=True)
class IdentityAlias:
    site: str
    plot: str
    tag: str
    identity_tag: str
    effective_from: date
    effective_to: date | None
    note: str


@dataclass(frozen=True)
class RowReassignment:
    note: str
    match: dict[str, object]
    public_tag: str | None
    identity_tag: str | None
    tree_number: str | None


@dataclass(frozen=True)
class SplitOperation:
    note: str
    source: dict[str, object]
    target_identity_tag: str
    target_identity_label: str | None
    target_public_tag: str | None
    target_tree_number: str | None
    selector: dict[str, object]


@dataclass(frozen=True)
class TreeResolution:
    note: str
    tree: dict[str, object]
    codes: tuple[str, ...]
    kind: str


@dataclass(frozen=True)
class SourceInput:
    id: str
    path: Path
    adapter: str
    base: str
    required: bool
    origin: str


@dataclass(frozen=True)
class Config:
    config_dir: Path
    surveys: tuple[Survey, ...]
    plots: frozenset[str]
    genus_aliases: dict[str, str]
    species_aliases: dict[str, str]
    species_aliases_by_genus: dict[str, dict[str, str]]
    unknown_genus: str
    unknown_species: str
    not_found_threshold_surveys: int
    output_parquet: Path
    output_manifest: Path
    row_corrections: tuple[RowCorrection, ...]
    row_exclusions: tuple[RowExclusion, ...]
    taxon_overrides: tuple[TaxonOverride, ...]
    identity_aliases: tuple[IdentityAlias, ...]
    row_reassignments: tuple[RowReassignment, ...]
    split_operations: tuple[SplitOperation, ...]
    tree_resolutions: tuple[TreeResolution, ...]
    source_inputs: tuple[SourceInput, ...]

    def survey_for_date(self, value: date) -> str:
        for survey in self.surveys:
            if survey.start <= value <= survey.end:
                return survey.id
        raise ConfigError(f"No configured survey contains date {value.isoformat()}")

    def survey_index(self, survey_id: str) -> int:
        for index, survey in enumerate(self.surveys):
            if survey.id == survey_id:
                return index
        raise ConfigError(f"Unknown survey id {survey_id}")


def load_config(config_dir: str | Path = "config") -> Config:
    config_dir = Path(config_dir)
    surveys_data = _read_toml(config_dir / "surveys.toml")
    sites_data = _read_toml(config_dir / "sites.toml")
    taxonomy_data = _read_toml(config_dir / "taxonomy.toml")
    pipeline_data = _read_toml(config_dir / "pipeline.toml")
    corrections_data = _read_toml(config_dir / "corrections.toml", optional=True)
    identity_data = _read_toml(config_dir / "identity.toml", optional=True)
    resolutions_data = _read_toml(config_dir / "resolutions.toml", optional=True)
    sources_data = _read_toml(config_dir / "sources.toml", optional=True)

    surveys = tuple(
        Survey(
            id=item["id"],
            start=date.fromisoformat(item["start"]),
            end=date.fromisoformat(item["end"]),
        )
        for item in surveys_data["surveys"]
    )
    if tuple(sorted(surveys, key=lambda item: item.start)) != surveys:
        raise ConfigError("Surveys must be ordered by start date")

    plots: set[str] = set()
    for site in sites_data["sites"].values():
        plots.update(site["plots"])

    missingness = pipeline_data.get("missingness", {})
    output = pipeline_data.get("output", {})
    threshold = int(missingness.get("not_found_threshold_surveys", 2))
    if threshold < 1:
        raise ConfigError("not_found_threshold_surveys must be at least 1")

    return Config(
        config_dir=config_dir,
        surveys=surveys,
        plots=frozenset(plots),
        genus_aliases={k.lower(): v for k, v in taxonomy_data["genus_aliases"].items()},
        species_aliases={k.lower(): v for k, v in taxonomy_data["species_aliases"].items()},
        species_aliases_by_genus={
            genus.lower(): {k.lower(): v for k, v in aliases.items()}
            for genus, aliases in taxonomy_data.get("species_aliases_by_genus", {}).items()
        },
        unknown_genus=taxonomy_data["canonical"]["unknown_genus"],
        unknown_species=taxonomy_data["canonical"]["unknown_species"],
        not_found_threshold_surveys=threshold,
        output_parquet=Path(output.get("parquet", "output/forest_census.parquet")),
        output_manifest=Path(output.get("manifest", "output/manifest.json")),
        row_corrections=_load_row_corrections(corrections_data),
        row_exclusions=_load_row_exclusions(corrections_data),
        taxon_overrides=_load_taxon_overrides(corrections_data),
        identity_aliases=_load_identity_aliases(identity_data),
        row_reassignments=_load_row_reassignments(identity_data),
        split_operations=_load_split_operations(identity_data),
        tree_resolutions=_load_tree_resolutions(resolutions_data),
        source_inputs=_load_source_inputs(sources_data),
    )


def _load_row_corrections(data: dict) -> tuple[RowCorrection, ...]:
    return tuple(
        RowCorrection(
            note=str(item.get("note", "")),
            match=dict(item.get("match", {})),
            set=dict(item.get("set", {})),
        )
        for item in data.get("row_corrections", [])
    )


def _load_row_exclusions(data: dict) -> tuple[RowExclusion, ...]:
    return tuple(
        RowExclusion(
            note=str(item.get("note", "")),
            match=dict(item.get("match", {})),
        )
        for item in data.get("row_exclusions", [])
    )


def _load_taxon_overrides(data: dict) -> tuple[TaxonOverride, ...]:
    return tuple(
        TaxonOverride(
            note=str(item.get("note", "")),
            match=dict(item.get("match", {})),
            genus=str(item["genus"]),
            species=str(item["species"]),
            scope=str(item.get("scope", "tree")),
        )
        for item in data.get("taxon_overrides", [])
    )


def _load_identity_aliases(data: dict) -> tuple[IdentityAlias, ...]:
    aliases = []
    for item in data.get("aliases", []):
        effective_to = item.get("effective_to")
        aliases.append(
            IdentityAlias(
                site=str(item["site"]),
                plot=str(item["plot"]),
                tag=str(item["tag"]),
                identity_tag=str(item["identity_tag"]),
                effective_from=date.fromisoformat(item["effective_from"]),
                effective_to=date.fromisoformat(effective_to) if effective_to else None,
                note=str(item.get("note", "")),
            )
        )
    return tuple(aliases)


def _load_row_reassignments(data: dict) -> tuple[RowReassignment, ...]:
    reassignments = []
    for item in data.get("row_reassignments", []):
        reassignments.append(
            RowReassignment(
                note=str(item.get("note", "")),
                match=dict(item.get("match", {})),
                public_tag=_optional_string(item.get("public_tag")),
                identity_tag=_optional_string(item.get("identity_tag")),
                tree_number=_optional_string(item.get("tree_number")),
            )
        )
    return tuple(reassignments)


def _load_split_operations(data: dict) -> tuple[SplitOperation, ...]:
    splits = []
    for item in data.get("splits", []):
        splits.append(
            SplitOperation(
                note=str(item.get("note", "")),
                source=dict(item["source"]),
                target_identity_tag=str(item["target_identity_tag"]),
                target_identity_label=_optional_string(item.get("target_identity_label")),
                target_public_tag=_optional_string(item.get("target_public_tag")),
                target_tree_number=_optional_string(item.get("target_tree_number")),
                selector=dict(item.get("selector", {"kind": "all"})),
            )
        )
    return tuple(splits)


def _load_tree_resolutions(data: dict) -> tuple[TreeResolution, ...]:
    resolutions = []
    for item in data.get("tree_resolutions", []):
        codes = item.get("codes", [])
        if isinstance(codes, str):
            codes = [codes]
        resolutions.append(
            TreeResolution(
                note=str(item.get("note", "")),
                tree=dict(item["tree"]),
                codes=tuple(str(code) for code in codes),
                kind=str(item.get("kind", "reviewed")),
            )
        )
    return tuple(resolutions)


def _load_source_inputs(data: dict) -> tuple[SourceInput, ...]:
    inputs = []
    for item in data.get("inputs", []):
        inputs.append(
            SourceInput(
                id=str(item["id"]),
                path=Path(str(item["path"])),
                adapter=str(item["adapter"]),
                base=str(item.get("base", "raw_dir")),
                required=bool(item.get("required", True)),
                origin=str(item.get("origin", "historical")),
            )
        )
    return tuple(inputs)


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _read_toml(path: Path, optional: bool = False) -> dict:
    if optional and not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)
