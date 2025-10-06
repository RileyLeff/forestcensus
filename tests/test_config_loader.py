"""Unit tests for configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from forcen.config import ConfigBundle, load_config_bundle
from forcen.exceptions import ConfigError


FIXTURE_CONFIG_DIR = Path("planning/fixtures/configs")


def test_load_config_bundle_success() -> None:
    bundle = load_config_bundle(FIXTURE_CONFIG_DIR)
    assert isinstance(bundle, ConfigBundle)
    assert bundle.taxonomy.species[0].code == "PINTAE"
    assert "BRNV" in bundle.sites.sites
    assert bundle.surveys.surveys[0].id == "2019_Jun"
    assert bundle.validation.rounding == "half_up"
    assert bundle.datasheets.sort == "public_tag_numeric_asc"


def test_load_config_bundle_reports_taxonomy_error(tmp_path: Path) -> None:
    _write_minimal_configs(tmp_path)
    taxonomy_path = tmp_path / "taxonomy.toml"
    taxonomy_path.write_text(
        """
species = [
{ genus = "Pinus", species = "taeda", code = "WRONG" }
]

enforce_no_synonyms = true
""".strip()
    )

    with pytest.raises(ConfigError) as exc:
        load_config_bundle(tmp_path)

    message = str(exc.value)
    assert "taxonomy.toml" in message
    assert "species" in message


def test_load_config_bundle_reports_survey_overlap(tmp_path: Path) -> None:
    _write_minimal_configs(tmp_path)
    surveys_path = tmp_path / "surveys.toml"
    surveys_path.write_text(
        """
surveys = [
{ id = "S1", start = "2020-01-01", end = "2020-01-10" },
{ id = "S2", start = "2020-01-05", end = "2020-01-15" }
]
""".strip()
    )

    with pytest.raises(ConfigError) as exc:
        load_config_bundle(tmp_path)

    assert "surveys" in str(exc.value)


def _write_minimal_configs(target: Path) -> None:
    (target / "taxonomy.toml").write_text(
        """
species = [
{ genus = "Pinus", species = "taeda", code = "PINTAE" }
]

enforce_no_synonyms = true
""".strip()
    )

    (target / "sites.toml").write_text(
        """
[sites.TEST]
zone_order = ["Low Forest"]
plots = ["H0"]
girdling = {}
""".strip()
    )

    (target / "surveys.toml").write_text(
        """
surveys = [
{ id = "S1", start = "2020-01-01", end = "2020-01-10" }
]
""".strip()
    )

    (target / "validation.toml").write_text(
        """
rounding = "half_up"

dbh_pct_warn = 0.08
dbh_pct_error = 0.16

dbh_abs_floor_warn_mm = 3
dbh_abs_floor_error_mm = 6

retag_delta_pct = 0.10
new_tree_flag_min_dbh_mm = 60
drop_after_absent_surveys = 2
""".strip()
    )

    (target / "datasheets.toml").write_text(
        """
show_previous_surveys = 2
sort = "public_tag_numeric_asc"
show_zombie_asterisk = true
""".strip()
    )
