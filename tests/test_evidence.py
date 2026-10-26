from pathlib import Path

import pandas as pd

from forestcensus.config import load_config
from forestcensus.evidence import build_evidence_ledger, write_evidence_ledger
from forestcensus.llm_transcribe import materialize_llm_review


def test_evidence_ledger_extracts_sources_notes_and_tag_changes(tmp_path: Path) -> None:
    config = load_config("config")
    materialize_llm_review(
        "docs/oct_2025_reviewed_run_manifest.json",
        "output/llm_transcription/oct_2025_reviewed",
    )

    frames = build_evidence_ledger(
        raw_dir="data/raw/forest_census",
        archive_dir="data/raw/forest_census/original_drive_records",
        config=config,
    )

    may_path = Path("output/llm_transcription/may_2026_reviewed/import_recent_format_reviewed.csv")
    may_included = may_path.exists()
    assert len(frames.source_catalog) == 24 + int(may_included)
    assert len(frames.source_sheets) == 47 + int(may_included)
    assert len(frames.evidence_observations) > 59_000
    assert len(frames.evidence_notes) > 10_000
    assert len(frames.tag_change_assertions) == 27

    tag_changes = frames.tag_change_assertions
    assert (
        tag_changes["old_tree_code"].eq("L3_284_Jun")
        & tag_changes["new_tree_code"].eq("L3_1000_Jun")
    ).any()

    notes = frames.evidence_notes
    assert notes["note_flags"].str.contains("tag", na=False).any()
    assert notes["note_flags"].str.contains("poison_ivy", na=False).any()

    october_reviewed = frames.evidence_observations[
        frames.evidence_observations["source_path"].eq(
            "output/llm_transcription/oct_2025_reviewed/import_recent_format_reviewed.csv"
        )
    ]
    assert len(october_reviewed) == 1413
    assert set(october_reviewed["source_kind"]) == {"llm_reviewed_input_csv"}
    assert set(october_reviewed["canonical_role"]) == {"canonical_input"}

    if may_included:
        may_reviewed = frames.evidence_observations.loc[
            frames.evidence_observations["source_path"].eq(str(may_path))
        ]
        may_input = pd.read_csv(may_path, dtype=str, keep_default_na=False)
        # The untagged cancelled slot remains in the source, not a tree observation.
        tagged_input = may_input.loc[may_input["tree_number"].str.strip().ne("")]
        assert len(may_reviewed) == len(tagged_input)
        assert set(may_reviewed["source_kind"]) == {"llm_reviewed_input_csv"}
        assert set(may_reviewed["canonical_role"]) == {"canonical_input"}

    m0_826 = frames.evidence_observations[
        frames.evidence_observations["plot"].eq("M0")
        & frames.evidence_observations["public_tag_raw"].eq("826")
    ]
    assert {"accepted_input", "primary", "weak_secondary"}.issubset(set(m0_826["evidence_rank"]))
    assert {"accepted_input_observation", "observed_current", "carried_forward_context"}.issubset(
        set(m0_826["observation_role"])
    )

    summary = write_evidence_ledger(frames, tmp_path)
    assert Path(summary["outputs"]["evidence_observations"]).exists()
    written = pd.read_parquet(summary["outputs"]["tag_change_assertions"])
    assert len(written) == 27
