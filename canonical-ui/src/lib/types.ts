export type TreeCase = {
  tree_uid: string;
  site: string;
  plot: string;
  identity_tag: string;
  identity_label: string;
  public_tags: string;
  first_survey: string;
  last_survey: string;
  present_in_october_2025: boolean;
  first_seen_in_october_2025: boolean;
  missing_from_october_2025: boolean;
  last_pre_october_status: string;
  primary_taxon_code: string;
  taxon_codes: string;
  max_dbh_mm: string;
  october_max_dbh_mm: string;
  max_stem_count: string;
  invariant_codes: string;
  invariant_actions: string;
  diagnostic_codes: string;
  evidence_rows: string;
  primary_evidence_rows: string;
  accepted_input_evidence_rows: string;
  note_flags: string;
  candidate_link_count: string;
  best_candidate_link_score: string;
  review_bucket: string;
  review_status: 'needs_review' | 'watch' | 'quiet';
  review_status_label: string;
  review_reasons: string;
  priority_score: number;
  summary: string;
};

export type CanonicalHistoryRow = {
  survey_id: string;
  date: string;
  site: string;
  zone: string;
  plot: string;
  tree_uid: string;
  public_tag: string;
  identity_tag: string;
  identity_label: string;
  tree_number: string;
  stem_rank: string;
  datasheet_slot: string;
  genus: string;
  species: string;
  taxon_code: string;
  dbh_mm: string;
  health_observed: string;
  alive_observed: string;
  standing_observed: string;
  field_status: string;
  interpreted_status: string;
  alive_interpreted: string;
  zombie_ever: string;
  origin: string;
  source_file: string;
  source_row: string;
  notes: string;
  correction_notes: string;
};

export type SurveyTimelineItem = {
  survey_id: string;
  date: string;
};

export type EvidenceObservation = {
  evidence_id: string;
  source_id: string;
  source_path: string;
  source_sheet: string;
  source_row: string;
  source_kind: string;
  evidence_rank: string;
  canonical_role: string;
  observation_role: string;
  survey_id: string;
  date: string;
  year: string;
  month: string;
  day: string;
  site: string;
  zone: string;
  plot: string;
  public_tag_raw: string;
  tree_code_raw: string;
  old_tag_raw: string;
  datasheet_slot_raw: string;
  genus_raw: string;
  species_raw: string;
  taxon_raw: string;
  dbh_mm_raw: string;
  health_raw: string;
  alive_raw: string;
  standing_raw: string;
  poison_ivy_raw: string;
  notes_raw: string;
  note_flags: string;
  raw_payload_json: string;
  evidence_relation: string;
};

export type CandidateLink = {
  link_id: string;
  link_type: string;
  score: string;
  site: string;
  plot: string;
  source_tree_uid: string;
  source_identity_tag: string;
  source_public_tag: string;
  target_tree_uid: string;
  target_identity_tag: string;
  target_public_tag: string;
  source_max_dbh_mm: string;
  target_max_dbh_mm: string;
  dbh_delta_mm: string;
  dbh_delta_pct: string;
  taxon_match: string;
  review_status: string;
  review_reason: string;
  evidence_source: string;
  evidence_source_row: string;
  details: string;
};

export type TagChangeAssertion = {
  assertion_id: string;
  source_id: string;
  source_path: string;
  source_sheet: string;
  source_row: string;
  old_tree_code: string;
  new_tree_code: string;
  old_plot: string;
  old_tag: string;
  old_taxon_hint: string;
  new_plot: string;
  new_tag: string;
  new_taxon_hint: string;
  change_type: string;
  year_changed: string;
  raw_payload_json: string;
};

export type CanonicalReviewDecision = {
  key: string;
  tree_uid: string;
  plot: string;
  identity_tag: string;
  action_type: string;
  target_identity: string;
  target_taxon: string;
  note: string;
  decided_at: string;
};

export type ConfiguredDecision = {
  decision_id: string;
  operation: string;
  source_config: string;
  note: string;
  selector: string;
  parameters: string;
};

export type DecisionCandidate = {
  candidate_id: string;
  lane: string;
  generator: string;
  operation: string;
  priority: string;
  status: string;
  confidence: string;
  decision_scope: string;
  site: string;
  plot: string;
  tree_uid: string;
  identity_tag: string;
  public_tag: string;
  survey_id: string;
  stem_rank: string;
  source_file: string;
  source_row: string;
  selector: string;
  parameters: string;
  reason: string;
  guardrail_notes: string;
  source_code: string;
  source_summary: string;
  details: string;
};

export type ReviewWorklistItem = {
  item_id: string;
  lane: 'suggested_fix' | 'needs_human_call' | string;
  work_type: string;
  priority: string;
  status: string;
  site: string;
  plot: string;
  tree_uid: string;
  related_tree_uids: string;
  identity_tag: string;
  identity_label: string;
  public_tags: string;
  review_bucket: string;
  review_status: string;
  current_codes: string;
  diagnostic_codes: string;
  candidate_decision_ids: string;
  summary: string;
  recommended_action: string;
  decision_scope: string;
  confidence: string;
  needs_riley_call: string;
  source_rows_to_check: string;
  guardrail_notes: string;
};

export type DiagnosticIssue = {
  severity: string;
  code: string;
  message: string;
  survey_id: string;
  site: string;
  plot: string;
  public_tag: string;
  identity_tag: string;
  tree_uid: string;
  source_file: string;
  source_row: string;
  details: string;
};

export type InvariantFinding = {
  code: string;
  tree_uid: string;
  site: string;
  plot: string;
  identity_tag: string;
  identity_label: string;
  public_tag: string;
  severity: string;
  suggested_action: string;
  summary: string;
  resolution_kind: string;
  resolution_note: string;
  details: string;
};

export type CanonicalDossier = {
  selected: TreeCase;
  history: CanonicalHistoryRow[];
  directEvidence: EvidenceObservation[];
  linkedEvidence: EvidenceObservation[];
  noteMentionEvidence: EvidenceObservation[];
  sameTagOtherPlots: EvidenceObservation[];
  similarDbhSamePlot: EvidenceObservation[];
  complementaryMissingSamePlot: TreeCase[];
  candidateLinks: CandidateLink[];
  tagChanges: TagChangeAssertion[];
  decisions: CanonicalReviewDecision[];
  configuredDecisions: ConfiguredDecision[];
  decisionCandidates: DecisionCandidate[];
  reviewWorklist: ReviewWorklistItem[];
  issues: DiagnosticIssue[];
  invariants: InvariantFinding[];
  rawIssues: DiagnosticIssue[];
  rawInvariants: InvariantFinding[];
};

export type BrowserMode = 'tags' | 'tag-plot' | 'trees';

export type TagCard = {
  key: string;
  mode: 'tags' | 'tag-plot';
  tag: string;
  plot: string;
  plots: string;
  zone: string;
  zones: string;
  label: string;
  evidence_count: number;
  canonical_tree_count: number;
  canonical_tree_uids: string;
  first_survey: string;
  last_survey: string;
  max_dbh_mm: string;
  taxa: string;
  source_count: number;
  review_case_count: number;
  watch_case_count: number;
  quiet_case_count: number;
  review_status: 'needs_review' | 'watch' | 'quiet';
};

export type TagTreeScope = {
  tree_uid: string;
  scope: 'direct' | 'candidate_link' | 'tag_change' | 'same_tag_other_plot';
  scope_label: string;
  detail: string;
};

export type TagDossier = {
  selected: TagCard;
  evidence: EvidenceObservation[];
  treeCases: TreeCase[];
  treeScopes: TagTreeScope[];
  history: CanonicalHistoryRow[];
  issues: DiagnosticIssue[];
  invariants: InvariantFinding[];
  configuredDecisions: ConfiguredDecision[];
  decisionCandidates: DecisionCandidate[];
  reviewWorklist: ReviewWorklistItem[];
  rawIssues: DiagnosticIssue[];
  rawInvariants: InvariantFinding[];
};
