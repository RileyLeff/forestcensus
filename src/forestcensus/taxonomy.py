"""Accepted tree taxonomy and genus-level identification resolution."""

from __future__ import annotations

import pandas as pd

from .config import Config, TaxonOverride
from .corrections import _append_note, _match_mask
from .errors import CorrectionMatchError, CorrectionUnsafeSelectorError


REQUIRED_TREE_SELECTOR_COLUMNS = {"site", "plot", "identity_tag"}


def apply_taxon_overrides(events: pd.DataFrame, config: Config) -> pd.DataFrame:
    resolved = events.copy()
    if "correction_notes" not in resolved.columns:
        resolved["correction_notes"] = ""

    # Identification-resolution policies also cover taxa assigned by tree decisions.
    overrides = sorted(getattr(config, "taxon_overrides", ()), key=lambda item: item.scope == "genus")
    for override in overrides:
        _apply_taxon_override(resolved, override, config)

    return resolved


def _apply_taxon_override(df: pd.DataFrame, override: TaxonOverride, config: Config) -> None:
    _validate_taxon_override(override)
    mask = _match_mask(df, override.match)
    if not mask.any():
        raise CorrectionMatchError(f"Taxon override matched no rows: {override.note}")

    genus = _canonical_genus(override.genus, config)
    species = _canonical_species(override.species, genus, config)
    df.loc[mask, "genus"] = genus
    df.loc[mask, "species"] = species
    df.loc[mask, "taxon_code"] = _taxon_code(genus, species)
    _append_note(df, mask, override.note)


def _validate_taxon_override(override: TaxonOverride) -> None:
    if override.scope == "genus":
        if (
            set(override.match) != {"genus"}
            or override.match["genus"] != override.genus
            or override.species != "spp."
        ):
            raise CorrectionUnsafeSelectorError(
                "Genus resolution must match exactly its unchanged genus and set species to spp."
            )
        return
    if override.scope != "tree":
        raise CorrectionUnsafeSelectorError(f"Unknown taxon override scope: {override.scope}")
    missing = REQUIRED_TREE_SELECTOR_COLUMNS.difference(override.match)
    if missing:
        columns = ", ".join(sorted(missing))
        raise CorrectionUnsafeSelectorError(
            f"Taxon override must select one resolved tree with {columns}: {override.note}"
        )


def _canonical_genus(value: str, config: Config) -> str:
    key = value.strip().lower()
    return config.genus_aliases.get(key, value.strip() or config.unknown_genus)


def _canonical_species(value: str, genus: str, config: Config) -> str:
    key = value.strip().lower()
    genus_aliases = config.species_aliases_by_genus.get(genus.lower(), {})
    return genus_aliases.get(key, config.species_aliases.get(key, value.strip() or config.unknown_species))


def _taxon_code(genus: str, species: str) -> str:
    return f"{genus[:3]}{species[:3]}".upper().replace(".", "")
