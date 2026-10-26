# Second review

This review pass starts after the rebuilt diagnostic classifier split raw invariant noise into
`needs_review`, `watch`, and `quiet` cases.

Default scope for this pass is UUID/tag-plot/candidate-link rather than bare tag. Bare tags remain
useful for finding collisions, but decisions should be attached to the identity or link being
reviewed.

Current consolidation:

- Rule synthesis and implemented routing: `rule_consolidation.md`
- Targeted QA after random-QA consolidation: `targeted_qa_after_consolidation.md`
- Per-case items still needing Riley/Juan/source-sheet attention: `human_attention_queue.md`
