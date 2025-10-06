"""Tests for tree identity resolution."""

from __future__ import annotations

from datetime import date
from datetime import date
from pathlib import Path

from forcen.config import load_config_bundle
from forcen.config.models import (
    ConfigBundle,
    DatasheetsConfig,
    SiteConfig,
    SitesConfig,
    SpeciesEntry,
    SurveyWindow,
    SurveysConfig,
    TaxonomyConfig,
    ValidationConfig,
)
from forcen.engine.utils import determine_default_effective_date, with_default_effective
from forcen.assembly.treebuilder import assign_tree_uids, build_alias_resolver
from forcen.assembly.trees import generate_implied_rows
from forcen.assembly.split import apply_splits
from forcen.assembly.survey import SurveyCatalog
from forcen.assembly.properties import apply_properties, build_property_timelines
from forcen.transactions import NormalizationConfig, load_transaction
from forcen.transactions.models import MeasurementRow
from forcen.dsl import DSLParser
from forcen.dsl.types import SplitCommand, TagRef, UpdateCommand


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")
TX2_DIR = Path("planning/fixtures/transactions/tx-2-ops")


def _prepare_transaction(tx_dir: Path):
    config = load_config_bundle(CONFIG_DIR)
    tx = load_transaction(tx_dir, normalization=NormalizationConfig())
    default_effective = determine_default_effective_date(config, tx)
    tx.commands = with_default_effective(tx.commands, default_effective)
    resolver = build_alias_resolver(tx.measurements, tx.commands)
    assign_tree_uids(tx.measurements, resolver)
    return tx


def test_tree_uid_consistent_for_same_tag():
    tx = _prepare_transaction(TX1_DIR)
    tree_uids = {row.tree_uid for row in tx.measurements}
    assert len(tree_uids) == 1


def test_alias_rebinds_tag_to_existing_tree():
    tx_initial = _prepare_transaction(TX1_DIR)
    base_tree_uid = tx_initial.measurements[0].tree_uid

    tx_alias = _prepare_transaction(TX2_DIR)
    alias_tree_uid = tx_alias.measurements[0].tree_uid

    assert alias_tree_uid == base_tree_uid


def test_split_selector_reassigns_historical_rows():
    config = load_config_bundle(CONFIG_DIR)
    measurements = load_transaction(TX1_DIR, normalization=NormalizationConfig()).measurements
    tx_split = load_transaction(TX2_DIR, normalization=NormalizationConfig())
    default_effective = determine_default_effective_date(config, tx_split)
    commands = with_default_effective(tx_split.commands, default_effective)

    resolver = build_alias_resolver(measurements, commands)
    assign_tree_uids(measurements, resolver)
    splits = [cmd for cmd in commands if isinstance(cmd, SplitCommand)]
    apply_splits(measurements, splits, resolver, SurveyCatalog.from_config(config))

    split_cmd = splits[0]
    target_uid = resolver.resolve(split_cmd.target, split_cmd.effective_date)

    largest_row = max(measurements, key=lambda row: row.dbh_mm or 0)
    assert largest_row.tree_uid == target_uid


def test_update_properties_applied_to_measurements():
    config = load_config_bundle(CONFIG_DIR)
    tx = load_transaction(TX1_DIR, normalization=NormalizationConfig())
    parser = DSLParser()
    update_commands = parser.parse(
        "UPDATE BRNV/H4/112 SET genus=Pinus,species=taeda,code=PINTAE EFFECTIVE 2018-01-01"
    )
    commands = with_default_effective(update_commands, determine_default_effective_date(config, tx))

    resolver = build_alias_resolver(tx.measurements, commands)
    assign_tree_uids(tx.measurements, resolver)
    timelines = build_property_timelines(
        [cmd for cmd in commands if isinstance(cmd, UpdateCommand)],
        resolver,
    )
    apply_properties(tx.measurements, timelines)

    for row in tx.measurements:
        assert row.genus == "Pinus"
        assert row.species == "taeda"
        assert row.code == "PINTAE"


def _make_config_with_three_surveys() -> ConfigBundle:
    taxonomy = TaxonomyConfig(
        species=[SpeciesEntry(genus="Pinus", species="taeda", code="PINTAE")],
        enforce_no_synonyms=True,
    )
    sites = SitesConfig(
        sites={
            "BRNV": SiteConfig(zone_order=["Z"], plots=["H1"], girdling={})
        }
    )
    surveys = SurveysConfig(
        surveys=[
            SurveyWindow(id="2019", start=date(2019, 1, 1), end=date(2019, 1, 31)),
            SurveyWindow(id="2020", start=date(2020, 1, 1), end=date(2020, 1, 31)),
            SurveyWindow(id="2021", start=date(2021, 1, 1), end=date(2021, 1, 31)),
        ]
    )
    validation = ValidationConfig(
        rounding="half_up",
        dbh_pct_warn=0.08,
        dbh_pct_error=0.16,
        dbh_abs_floor_warn_mm=3,
        dbh_abs_floor_error_mm=6,
        retag_delta_pct=0.10,
        new_tree_flag_min_dbh_mm=60,
        drop_after_absent_surveys=2,
    )
    datasheets = DatasheetsConfig(
        show_previous_surveys=2,
        sort="public_tag_numeric_asc",
        show_zombie_asterisk=True,
    )
    return ConfigBundle(
        taxonomy=taxonomy,
        sites=sites,
        surveys=surveys,
        validation=validation,
        datasheets=datasheets,
    )


def test_generate_implied_row_for_trailing_gap():
    config = _make_config_with_three_surveys()
    row = MeasurementRow(
        row_number=1,
        site="BRNV",
        plot="H1",
        tag="100",
        date=date(2019, 1, 15),
        dbh_mm=120,
        health=9,
        standing=True,
        notes="",
        origin="field",
    )
    row.tree_uid = "tree-uid"
    implied_rows = generate_implied_rows([row], config)
    assert len(implied_rows) == 1
    implied = implied_rows[0]
    assert implied.origin == "implied"
    assert implied.date == date(2020, 1, 1)


def test_generate_implied_removed_when_rediscovered():
    config = _make_config_with_three_surveys()
    row1 = MeasurementRow(
        row_number=1,
        site="BRNV",
        plot="H1",
        tag="100",
        date=date(2019, 1, 15),
        dbh_mm=120,
        health=9,
        standing=True,
        notes="",
        origin="field",
    )
    row2 = MeasurementRow(
        row_number=2,
        site="BRNV",
        plot="H1",
        tag="100",
        date=date(2021, 1, 15),
        dbh_mm=125,
        health=9,
        standing=True,
        notes="",
        origin="field",
    )
    row1.tree_uid = row2.tree_uid = "tree-uid"
    implied_rows = generate_implied_rows([row1, row2], config)
    assert implied_rows == []
