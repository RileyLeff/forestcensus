"""Tests for validation logic."""

from __future__ import annotations

import pytest

from forcen.config import load_config_bundle
from forcen.dsl import DSLParser
from forcen.transactions import load_measurements
from forcen.validators import (
    validate_dsl_commands,
    validate_growth,
    validate_measurement_rows,
)

CONFIG = load_config_bundle("planning/fixtures/configs")


def test_row_validator_detects_unknown_site(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
UNKNOWN,H4,112,2019-06-16,171,9,TRUE,""
"""
    )
    rows = load_measurements(csv_path)
    issues = validate_measurement_rows(rows, CONFIG)
    assert any(issue.code == "E_ROW_SITE_OR_PLOT_UNKNOWN" for issue in issues)


def test_row_validator_dbh_na_not_implied(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes,origin
BRNV,H4,112,2019-06-16,NA,9,TRUE,"",field
"""
    )
    rows = load_measurements(csv_path)
    issues = validate_measurement_rows(rows, CONFIG)
    assert any(issue.code == "E_ROW_DBH_NA_NOT_IMPLIED" for issue in issues)


def test_row_validator_taxonomy_mismatch(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes,genus,species,code
BRNV,H4,112,2019-06-16,171,9,TRUE,"",Pinus,wrong,PINTAE
"""
    )
    rows = load_measurements(csv_path)
    issues = validate_measurement_rows(rows, CONFIG)
    assert any(issue.code == "E_ROW_TAXONOMY_MISMATCH" for issue in issues)


def test_row_validator_date_outside_survey(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
BRNV,H4,112,2018-06-16,171,9,TRUE,""
"""
    )
    rows = load_measurements(csv_path)
    issues = validate_measurement_rows(rows, CONFIG)
    assert any(issue.code == "E_ROW_DATE_OUTSIDE_SURVEY" for issue in issues)


def test_dsl_validator_reports_alias_overlap():
    parser = DSLParser()
    commands = parser.parse(
        "\n".join(
            [
                "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY EFFECTIVE 2020-06-15",
                "ALIAS BRNV/H4/508 TO 923e4567-e89b-12d3-a456-426614174000 EFFECTIVE 2020-06-15",
            ]
        )
    )
    issues = validate_dsl_commands(commands)
    assert any(issue.code == "E_ALIAS_OVERLAP" for issue in issues)


def test_dsl_validator_accepts_clean_commands():
    parser = DSLParser()
    commands = parser.parse(
        "ALIAS BRNV/H4/508 TO 123e4567-e89b-12d3-a456-426614174000 PRIMARY"
    )
    issues = validate_dsl_commands(commands)
    assert not issues


def test_growth_validator_warns_on_large_delta(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
BRNV,H4,112,2019-06-16,100,9,TRUE,""
BRNV,H4,112,2020-06-16,120,9,TRUE,""
"""
    )
    rows = load_measurements(csv_path)
    issues = validate_growth(rows, CONFIG)
    codes = {issue.code for issue in issues}
    assert "W_DBH_GROWTH_WARN" in codes or "E_DBH_GROWTH_ERROR" in codes
