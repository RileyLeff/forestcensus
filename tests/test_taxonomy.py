from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from forestcensus.config import TaxonOverride, load_config
from forestcensus.errors import CorrectionUnsafeSelectorError
from forestcensus.taxonomy import apply_taxon_overrides


def _copy_base_config(config_dir: Path) -> None:
    config_dir.mkdir()
    for name in ["pipeline.toml", "sites.toml", "surveys.toml", "taxonomy.toml"]:
        (config_dir / name).write_text(Path("config", name).read_text(encoding="utf-8"), encoding="utf-8")
    (config_dir / "identity.toml").write_text("", encoding="utf-8")


def _event(**overrides) -> dict:
    base = {
        "source_file": "test.csv",
        "source_row": 2,
        "survey_id": "June_2022",
        "date": date(2022, 6, 16),
        "site": "BRNV",
        "zone": "H",
        "plot": "H0",
        "public_tag": "298",
        "identity_tag": "298",
        "tree_number": "298",
        "datasheet_slot": "1",
        "genus": "Acer",
        "species": "spp.",
        "taxon_code": "ACESPP",
        "dbh_mm": 130,
        "health_observed": 8,
        "alive_observed": True,
        "standing_observed": True,
        "field_status": "observed_alive",
        "notes": "",
        "correction_notes": "",
        "origin": "test",
    }
    return {**base, **overrides}


def test_taxon_override_applies_one_canonical_taxon_to_resolved_tree(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    _copy_base_config(config_dir)
    (config_dir / "corrections.toml").write_text(
        """
[[taxon_overrides]]
note = "Resolved Acer rubrum"
match = { site = "BRNV", plot = "H0", identity_tag = "298" }
genus = "Acer"
species = "rubrum"
""",
        encoding="utf-8",
    )
    config = load_config(config_dir)
    events = pd.DataFrame(
        [
            _event(source_row=2, species="spp.", taxon_code="ACESPP"),
            _event(source_row=3, species="rubrum", taxon_code="ACERUB"),
        ]
    )

    resolved = apply_taxon_overrides(events, config)

    assert resolved["species"].tolist() == ["rubrum", "rubrum"]
    assert resolved["taxon_code"].tolist() == ["ACERUB", "ACERUB"]
    assert resolved["correction_notes"].str.contains("Resolved Acer rubrum", regex=False).all()


def test_taxon_override_requires_resolved_tree_selector() -> None:
    events = pd.DataFrame([_event()])
    config = SimpleNamespace(
        taxon_overrides=(
            TaxonOverride(
                note="too broad",
                match={"site": "BRNV", "plot": "H0"},
                genus="Acer",
                species="rubrum",
            ),
        )
    )

    with pytest.raises(CorrectionUnsafeSelectorError, match="identity_tag"):
        apply_taxon_overrides(events, config)
