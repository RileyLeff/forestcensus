"""Regression tests for retroactive DSL effects and implied rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

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
from forcen.engine import lint_transaction, submit_transaction
from forcen.engine.utils import determine_default_effective_date, with_default_effective
from forcen.assembly.tree_outputs import build_retag_suggestions
from forcen.assembly.reassemble import assemble_dataset, clone_raw_measurement
from forcen.assembly.trees import generate_implied_rows
from forcen.ledger.storage import Ledger
from forcen.transactions import NormalizationConfig, load_transaction
from forcen.transactions.models import MeasurementRow


CONFIG_DIR = Path("planning/fixtures/configs")
CONFIG = load_config_bundle(CONFIG_DIR)


def _assemble_from_workspace(workspace: Path) -> list[MeasurementRow]:
    ledger = Ledger(workspace)
    raw_rows = ledger.load_raw_measurements()
    commands = ledger.load_commands()
    return assemble_dataset(raw_rows, commands, CONFIG)


def test_retroactive_alias_and_split_updates_history(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    workspace.mkdir()

    submit_transaction(
        Path("planning/fixtures/transactions/tx-1-initial"),
        CONFIG_DIR,
        workspace,
    )
    submit_transaction(
        Path("planning/fixtures/transactions/tx-2-ops"),
        CONFIG_DIR,
        workspace,
    )

    assembled = _assemble_from_workspace(workspace)

    by_key = {(row.date, row.dbh_mm): row for row in assembled if row.origin == "field"}
    largest_2019 = by_key[(date(2019, 6, 16), 171)]
    largest_2020 = by_key[(date(2020, 6, 16), 174)]
    smaller_2019 = by_key[(date(2019, 6, 16), 95)]
    smaller_2020 = by_key[(date(2020, 6, 16), 97)]

    assert largest_2019.tree_uid == largest_2020.tree_uid
    assert smaller_2019.tree_uid == smaller_2020.tree_uid
    assert smaller_2019.tree_uid != largest_2019.tree_uid
    assert largest_2020.public_tag == "508"
    assert largest_2019.public_tag == "112"


def test_retroactive_update_applies_to_prior_rows(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    workspace.mkdir()

    submit_transaction(
        Path("planning/fixtures/transactions/tx-1-initial"),
        CONFIG_DIR,
        workspace,
    )

    tx_update = tmp_path / "tx-update"
    tx_update.mkdir()
    (tx_update / "measurements.csv").write_text(
        "site,plot,tag,date,dbh_mm,health,standing,notes\n", encoding="utf-8"
    )
    (tx_update / "updates.tdl").write_text(
        "UPDATE BRNV/H4/112 SET genus=Picea,species=abies,code=PICEAB EFFECTIVE 2018-01-01\n",
        encoding="utf-8",
    )

    submit_transaction(tx_update, CONFIG_DIR, workspace)

    assembled = _assemble_from_workspace(workspace)
    for row in assembled:
        if row.origin == "field":
            assert row.genus == "Picea"
            assert row.species == "abies"
            assert row.code == "PICEAB"


def test_retag_deduplicates_closest_candidate() -> None:
    rows = [
        MeasurementRow(
            row_number=1,
            site="BRNV",
            plot="H1",
            tag="100",
            date=date(2019, 6, 16),
            dbh_mm=110,
            health=9,
            standing=True,
            notes="",
            origin="field",
            tree_uid="lost",
            public_tag="100",
        ),
        MeasurementRow(
            row_number=2,
            site="BRNV",
            plot="H1",
            tag="200",
            date=date(2020, 6, 16),
            dbh_mm=109,
            health=9,
            standing=True,
            notes="",
            origin="field",
            tree_uid="newA",
            public_tag="200",
        ),
        MeasurementRow(
            row_number=3,
            site="BRNV",
            plot="H1",
            tag="300",
            date=date(2020, 6, 16),
            dbh_mm=100,
            health=9,
            standing=True,
            notes="",
            origin="field",
            tree_uid="newB",
            public_tag="300",
        ),
    ]

    suggestions = build_retag_suggestions(rows, CONFIG)
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion["lost_tree_uid"] == "lost"
    assert suggestion["new_tree_uid"] == "newA"
    assert suggestion["new_public_tag"] == "200"


def test_retag_skips_pre_aliased_tags() -> None:
    rows = [
        MeasurementRow(
            row_number=1,
            site="BRNV",
            plot="H1",
            tag="100",
            date=date(2019, 6, 16),
            dbh_mm=110,
            health=9,
            standing=True,
            notes="",
            origin="field",
            tree_uid="lost",
            public_tag="200",
        ),
        MeasurementRow(
            row_number=2,
            site="BRNV",
            plot="H1",
            tag="200",
            date=date(2020, 6, 16),
            dbh_mm=109,
            health=9,
            standing=True,
            notes="",
            origin="field",
            tree_uid="lost",
            public_tag="200",
        ),
    ]

    suggestions = build_retag_suggestions(rows, CONFIG)
    assert suggestions == []


def test_implied_rows_for_trailing_gaps(tmp_path: Path) -> None:
    config = _make_config_with_surveys(
        [
            ("2019", "2019-01-01", "2019-12-31"),
            ("2020", "2020-01-01", "2020-12-31"),
            ("2021", "2021-01-01", "2021-12-31"),
            ("2022", "2022-01-01", "2022-12-31"),
            ("2023", "2023-01-01", "2023-12-31"),
        ],
        drop_after=2,
    )

    row_2019 = MeasurementRow(
        row_number=1,
        site="BRNV",
        plot="H1",
        tag="100",
        date=date(2019, 6, 16),
        dbh_mm=150,
        health=9,
        standing=True,
        notes="",
        origin="field",
        tree_uid="tree-100",
        public_tag="100",
    )
    row_2022 = MeasurementRow(
        row_number=2,
        site="BRNV",
        plot="H1",
        tag="100",
        date=date(2022, 6, 16),
        dbh_mm=155,
        health=9,
        standing=True,
        notes="",
        origin="field",
        tree_uid="tree-100",
        public_tag="100",
    )

    dataset = assemble_dataset([row_2019, row_2022], [], config)
    implied = [row for row in dataset if row.origin == "implied"]
    assert len(implied) == 0

    # Add trailing gap after 2022 (missing 2023/2024) and expect implied at 2023
    config_longer = _make_config_with_surveys(
        [
            ("2019", "2019-01-01", "2019-12-31"),
            ("2020", "2020-01-01", "2020-12-31"),
            ("2021", "2021-01-01", "2021-12-31"),
            ("2022", "2022-01-01", "2022-12-31"),
            ("2023", "2023-01-01", "2023-12-31"),
            ("2024", "2024-01-01", "2024-12-31"),
        ],
        drop_after=2,
    )

    dataset_trailing = assemble_dataset([row_2019, row_2022], [], config_longer)
    implied_trailing = [row for row in dataset_trailing if row.origin == "implied"]
    assert len(implied_trailing) == 1
    assert implied_trailing[0].date == date(2023, 1, 1)


def test_split_idempotent() -> None:
    tx_initial = load_transaction(Path("planning/fixtures/transactions/tx-1-initial"), normalization=NormalizationConfig())
    tx_split = load_transaction(Path("planning/fixtures/transactions/tx-2-ops"), normalization=NormalizationConfig())
    default_effective = determine_default_effective_date(CONFIG, tx_split)
    commands = with_default_effective(tx_split.commands, default_effective)

    raw_rows = [clone_raw_measurement(row) for row in tx_initial.measurements + tx_split.measurements]
    for idx, row in enumerate(raw_rows):
        row.source_tx = "tx1" if idx < len(tx_initial.measurements) else "tx2"

    first_pass = assemble_dataset(raw_rows, commands, CONFIG)
    second_pass = assemble_dataset(raw_rows, commands, CONFIG)

    first = [(row.date, row.dbh_mm, row.tree_uid) for row in first_pass]
    second = [(row.date, row.dbh_mm, row.tree_uid) for row in second_pass]
    assert first == second


def test_lint_with_workspace_merges_history(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    workspace.mkdir()
    submit_transaction(Path("planning/fixtures/transactions/tx-1-initial"), CONFIG_DIR, workspace)

    report_no_ws = lint_transaction(
        Path("planning/fixtures/transactions/tx-2-ops"),
        CONFIG_DIR,
        normalization=NormalizationConfig(),
    )
    assert report_no_ws.error_count == 0

    report_with_ws = lint_transaction(
        Path("planning/fixtures/transactions/tx-2-ops"),
        CONFIG_DIR,
        normalization=NormalizationConfig(),
        workspace=workspace,
    )
    assert report_with_ws.error_count == 0
    assert report_with_ws.tree_view


def _make_config_with_surveys(surveys: list[tuple[str, str, str]], drop_after: int) -> ConfigBundle:
    taxonomy = TaxonomyConfig(
        species=[SpeciesEntry(genus="Pinus", species="taeda", code="PINTAE")],
        enforce_no_synonyms=True,
    )
    sites = SitesConfig(
        sites={"BRNV": SiteConfig(zone_order=["Z"], plots=["H1"], girdling={})}
    )
    surveys_config = SurveysConfig(
        surveys=[
            SurveyWindow(id=ident, start=date.fromisoformat(start), end=date.fromisoformat(end))
            for ident, start, end in surveys
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
        drop_after_absent_surveys=drop_after,
    )
    datasheets = DatasheetsConfig(
        show_previous_surveys=2,
        sort="public_tag_numeric_asc",
        show_zombie_asterisk=True,
    )
    return ConfigBundle(
        taxonomy=taxonomy,
        sites=sites,
        surveys=surveys_config,
        validation=validation,
        datasheets=datasheets,
    )
