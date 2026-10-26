# Forest Census Agent Orientation

Read `docs/researcher_handoff.md` and `docs/handoff_open_questions.md` first.
They distinguish implemented behavior, historical proposals, and open science
questions. Do not infer that a proposal in an old review note was accepted.

## Non-Negotiable Data Rules

- Preserve scans, source exports, raw model JSON, and saved reviewer decisions.
- Field tags identify trees within plots, not individually tagged stems.
  `stem_rank` is a within-survey DBH ordering, not longitudinal stem identity.
- Inspect shared-tag cases together; scope actual changes to the source row,
  plot/identity window, or resolved tree UID. Bare tags are not globally unique.
- `health = 0` is dead, positive health is alive. Missing is not zero. Presence
  exists if DBH, health, or standing is recorded, including zero/false.
- Retrospective absence inference is not observed death. It cannot establish
  a zombie. Do not turn blank standing boxes into fallen automatically.
- Current inclusive size thresholds: 20 mm generally, 50 mm for Morella
  cerifera. Some older diagnostics still use 50 mm; see the open register.
- DBH became optional during October 2025. Never import printed previous DBH
  or HSP context as a new measurement. Dead-tree DBH loss can be real.
- Raw diagnostics -> one accepted decision phase -> assembly -> post-decision
  verification. `config/resolutions.toml` acknowledgements and UI proposals
  are not permission to silently change measurements.
- Do not automatically delete equal-sized stems, infer tag swaps from size
  alone, or invent corrected values. Preserve uncertainty and ask for judgment.

## Safe Work

- Keep the transcription reviewer (`review-ui`) separate from historical
  identity/evidence review (`canonical-ui`). Pin `REVIEW_RUN_DIR` explicitly.
- Never bind either unauthenticated local app to a public interface.
- Build candidates to a fresh `output/<work-name>/forest_census.parquet`.
  Bare `build` overwrites the publication. Promote only after approval.
- Full LLM runs spend credits. Do not start them as a setup or test step.
- Restore the release data bundle before claiming a complete build. The
  ignored `output/` directory contains irreplaceable edits, not just caches.
- New source rows can change CSV coordinates. Use provenance plus expected
  values as guards, verify unique matches, and never renumber raw inputs.
- Preserve current work; do not reset or clean a dirty checkout.
- Use `uv sync --locked`, `uv run pytest`, and each app's check/build scripts.
- Never commit credentials. Scan code and release data before uploading.
- Update the handoff/open register when closing an item; record evidence,
  accepted decision, checks performed, and remaining limitations.
