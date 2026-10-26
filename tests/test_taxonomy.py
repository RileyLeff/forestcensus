from __future__ import annotations

from datetime import date
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from forestcensus.config import TaxonOverride, load_config
from forestcensus.errors import CorrectionUnsafeSelectorError
from forestcensus.taxonomy import apply_taxon_overrides
from forestcensus.adapters import _canonical_species
from forestcensus.decisions import apply_decisions, build_configured_decision_ledger


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


def test_vaccinium_resolution_is_audited_without_changing_raw_species():
    config = load_config()
    rule = next(rule for rule in config.taxon_overrides if rule.scope == "genus")
    config = replace(
        config, row_corrections=(), row_exclusions=(), identity_aliases=(),
        row_reassignments=(), split_operations=(), taxon_overrides=(rule,),
    )
    events = pd.DataFrame([
        _event(genus="Vaccinium", species=species, taxon_code="VAC" + species[:3].upper())
        for species in ["cor", "corymbosum", "spp.", "cerifera", "unresolved-name"]
    ] + [_event(genus="Morella", species="cerifera", taxon_code="MORCER")])
    original = events.copy(deep=True)
    result = apply_decisions(events, config)
    pd.testing.assert_frame_equal(events, original)
    vac = result[result.genus.eq("Vaccinium")]
    assert vac.species.eq("spp.").all()
    assert vac.taxon_code.eq("VACSPP").all()
    assert vac.correction_notes.eq(rule.note).all()
    assert result.iloc[-1].species == "cerifera"
    assert result.iloc[-1].correction_notes == ""
    assert build_configured_decision_ledger(config).iloc[0].operation == "set_taxon"
    assert _canonical_species("cor", config, "Morella") == "cerifera"
    assert _canonical_species("cor", config, "Vaccinium") == "cor"


def test_genus_resolution_also_covers_a_later_listed_tree_taxon_override():
    config = load_config()
    policy = next(rule for rule in config.taxon_overrides if rule.scope == "genus")
    tree = TaxonOverride(
        "tree identified as Vaccinium", {"site": "BRNV", "plot": "H0", "identity_tag": "298"},
        "Vaccinium", "corymbosum",
    )
    config = replace(config, taxon_overrides=(policy, tree))
    result = apply_taxon_overrides(pd.DataFrame([_event()]), config)
    assert result.iloc[0].genus == "Vaccinium"
    assert result.iloc[0].species == "spp."
    assert "tree identified as Vaccinium" in result.iloc[0].correction_notes
    assert policy.note in result.iloc[0].correction_notes


@pytest.mark.parametrize("changes", [
    {"match": {}}, {"match": {"genus": "Vaccinium", "plot": "R2"}},
    {"genus": "Morella"}, {"species": "corymbosum"}, {"scope": "everything"},
])
def test_genus_resolution_cannot_silently_broaden_or_rename_a_genus(changes):
    rule = TaxonOverride("bad scope", {"genus": "Vaccinium"}, "Vaccinium", "spp.", "genus")
    rule = replace(rule, **changes)
    with pytest.raises(CorrectionUnsafeSelectorError):
        apply_taxon_overrides(pd.DataFrame([_event()]), SimpleNamespace(taxon_overrides=(rule,)))
