"""CLI tests for datasheets generation."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from forcen.cli import app


runner = CliRunner()


def run_cli(args: list[str]):
    env = {"PYTHONPATH": "src"}
    return runner.invoke(app, args, env=env)


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")
TX2_DIR = Path("planning/fixtures/transactions/tx-2-ops")


def _prepare_workspace(workspace: Path) -> None:
    submit1 = run_cli(
        [
            "tx",
            "submit",
            str(TX1_DIR),
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    assert submit1.exit_code == 0

    submit2 = run_cli(
        [
            "tx",
            "submit",
            str(TX2_DIR),
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    assert submit2.exit_code == 0


def test_datasheets_generate_context(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    out_dir = tmp_path / "datasheets"
    _prepare_workspace(workspace)

    result = run_cli(
        [
            "datasheets",
            "generate",
            "--survey",
            "2020_Jun",
            "--site",
            "BRNV",
            "--plot",
            "H4",
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
            "--out",
            str(out_dir),
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    output_path = Path(payload["output"])
    assert output_path.exists()
    assert output_path.name == "context_BRNV_H4_2020_Jun.json"

    context = json.loads(output_path.read_text(encoding="utf-8"))
    assert context["survey_id"] == "2020_Jun"
    assert context["site"] == "BRNV"
    assert context["plot"] == "H4"
    assert context["tags_used"] == ["112", "508"]
    assert context["previous_surveys"] == ["2019_Jun"]

    trees = context["trees"]
    assert len(trees) == 2
    for tree in trees:
        assert "tree_uid" in tree
        assert tree["dhs1_marked"] is True
        assert tree["dhs2"] == []
        assert tree["stems_next"][0]["rank"] == 1


def test_datasheets_generate_requires_prior_survey(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"
    _prepare_workspace(workspace)

    result = run_cli(
        [
            "datasheets",
            "generate",
            "--survey",
            "2019_Jun",
            "--site",
            "BRNV",
            "--plot",
            "H4",
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
            "--out",
            str(tmp_path / "datasheets"),
        ]
    )
    assert result.exit_code == 4
