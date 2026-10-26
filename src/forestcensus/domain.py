"""Shared forest census domain constants and observation rules."""

import re

import pandas as pd

MIN_MEASURED_DBH_MM = 50
NON_MORELLA_CERIFERA_MIN_DBH_MM = 20
MORELLA_CERIFERA_MIN_DBH_MM = 50
DBH_JUMP_MIN_DELTA_MM = 6
DBH_JUMP_MIN_PCT = 0.16

NOT_FOUND_RE = re.compile(
    r"(?:couldn['\u2019]?t\s+find|could\s+not\s+find|not\s+found|unfound|missing|\bdnf\b)",
    re.IGNORECASE,
)
MISSING_PART_RE = re.compile(
    r"\b(?:tags?|top)\s+(?:(?:is|was)\s+)?missing\b|\bmissing\s+(?:tags?|top)\b",
    re.IGNORECASE,
)


def has_direct_observation(dbh_mm: object, health: object, standing: object) -> bool:
    """Normalized measurement inputs establish presence, including zero/False."""
    return any(pd.notna(value) for value in (dbh_mm, health, standing))


def note_mentions_tree_absence(notes: str) -> bool:
    """A missing tag or treetop does not by itself mean the tree was unfound."""
    return bool(NOT_FOUND_RE.search(MISSING_PART_RE.sub("", notes)))


def is_morella_cerifera(genus: object, species: object, taxon_code: object = "") -> bool:
    taxon = str(taxon_code or "").strip().upper()
    if taxon == "MORCER":
        return True
    return str(genus or "").strip().lower() == "morella" and str(species or "").strip().lower() == "cerifera"


def size_filter_min_dbh_mm(genus: object, species: object, taxon_code: object = "") -> int:
    if is_morella_cerifera(genus, species, taxon_code):
        return MORELLA_CERIFERA_MIN_DBH_MM
    return NON_MORELLA_CERIFERA_MIN_DBH_MM


def passes_size_filter(dbh_mm: object, genus: object, species: object, taxon_code: object = "") -> bool:
    if dbh_mm is None:
        return False
    try:
        dbh = float(dbh_mm)
    except (TypeError, ValueError):
        return False
    return dbh >= size_filter_min_dbh_mm(genus, species, taxon_code)
