import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'csv-parse/sync';
import type {
  BrowserMode,
  CandidateLink,
  CanonicalDossier,
  CanonicalHistoryRow,
  CanonicalReviewDecision,
  ConfiguredDecision,
  DecisionCandidate,
  DiagnosticIssue,
  EvidenceObservation,
  InvariantFinding,
  ReviewWorklistItem,
  SurveyTimelineItem,
  TagCard,
  TagDossier,
  TagChangeAssertion,
  TagTreeScope,
  TreeCase
} from '$lib/types';

type CsvRecord = Record<string, string>;
type LoadedData = {
  cases: TreeCase[];
  allTrees: TreeCase[];
  history: CanonicalHistoryRow[];
  surveys: SurveyTimelineItem[];
  evidence: EvidenceObservation[];
  links: CandidateLink[];
  tagChanges: TagChangeAssertion[];
  issues: DiagnosticIssue[];
  invariants: InvariantFinding[];
  rawIssues: DiagnosticIssue[];
  rawInvariants: InvariantFinding[];
  configuredDecisions: ConfiguredDecision[];
  decisionCandidates: DecisionCandidate[];
  reviewWorklist: ReviewWorklistItem[];
  tagCards: Record<'tags' | 'tag-plot', TagCard[]>;
  bucketCounts: Record<string, number>;
};
type ReviewStatus = TreeCase['review_status'];
type StatusCounts = Record<ReviewStatus, number> & { total: number };
type LaneCounts = Record<'needs_human_call' | 'suggested_fix', number> & { total: number };

const repoRoot = path.resolve('..');
const dataPaths = {
  cases: path.join(repoRoot, 'output/canonical_review/tree_cases.csv'),
  history: path.join(repoRoot, 'output/canonical_review/canonical_history.csv'),
  evidence: path.join(repoRoot, 'output/evidence/evidence_observations.csv'),
  links: path.join(repoRoot, 'output/canonical_review/candidate_links.csv'),
  tagChanges: path.join(repoRoot, 'output/evidence/tag_change_assertions.csv'),
  issues: path.join(repoRoot, 'output/diagnostics/issues.csv'),
  invariants: path.join(repoRoot, 'output/diagnostics/invariants.csv'),
  rawIssues: path.join(repoRoot, 'output/raw_diagnostics/issues.csv'),
  rawInvariants: path.join(repoRoot, 'output/raw_diagnostics/invariants.csv'),
  configuredDecisions: path.join(repoRoot, 'output/decisions/configured_decisions.csv'),
  decisionCandidates: path.join(repoRoot, 'output/canonical_review/decision_candidates.csv'),
  reviewWorklist: path.join(repoRoot, 'output/canonical_review/review_worklist.csv'),
  decisions: path.join(repoRoot, 'output/canonical_review/review_decisions.jsonl')
};
const listLimit = 300;
let cachedData: { signature: string; data: LoadedData } | null = null;

const humanReviewCodes = new Set([
  'taxon_conflict',
  'tag_scope_note_review',
  'mortality_contradiction',
  'max_dbh_jump',
  'ranked_dbh_jump',
  'single_survey_dbh_outlier',
  'short_run_dbh_outlier',
  'persistent_dbh_regime_shift',
  'stable_incompatible_dbh_era',
  'early_low_dbh_source_era_candidate',
  'source_note_dbh_conflict',
  'dead_tree_dbh_increase',
  'single_survey_death_label_outlier',
  'new_persistent_large_stem',
  'blank_missing_stem_backfill_candidate',
  'first_qualifying_after_prior_observation',
  'alive_health_conflict',
  'dead_health_conflict'
]);

const watchBuckets = new Set(['missing_from_october_2025', 'note_context', 'rule_assisted_cleanup', 'watch_context']);
const watchCodes = new Set([
  'probable_duplicate_stem_artifact',
  'subthreshold_dbh_present',
  'duplicate_stem_conflicting_fields',
  'dead_low_health_to_zero_candidate',
  'dead_label_low_health_later_alive',
  'near_duplicate_stem_artifact',
  'single_survey_low_health_death_label_outlier',
  'explicit_note_mortality_correction_candidate',
  'bounded_stem_rank_gap',
  'cluster_measurement_dbh_context',
  'dead_tree_stable_dbh_loss_context',
  'dead_tree_stem_context',
  'dead_tree_dbh_gap',
  'dead_tree_dbh_loss',
  'health_rebound_alive_context',
  'health_rebound_new_stem_context',
  'measurement_note_dbh_context',
  'merge_note_context',
  'morella_cluster_rank_jump_context',
  'new_noticed_stem_context',
  'observed_mortality_event',
  'oct_2025_protocol_missing_dbh',
  'nonqualifying_tree_excluded',
  'prior_dead_first_qualifying_dbh',
  'prior_live_blank_dbh_history',
  'stem_mortality_context',
  'structural_measurement_dbh_context',
  'threshold_edge_dbh_context',
  'dead_tree_threshold_dbh_context',
  'threshold_multistem_gap_context',
  'threshold_new_stem_context'
]);

function readCsv(filePath: string): CsvRecord[] {
  if (!fs.existsSync(filePath)) return [];
  return parse(fs.readFileSync(filePath, 'utf8'), {
    columns: true,
    bom: true,
    skip_empty_lines: true
  }) as CsvRecord[];
}

function readJsonl<T>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) return [];
  return fs
    .readFileSync(filePath, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line) as T);
}

function sourceSignature() {
  return [
    dataPaths.cases,
    dataPaths.history,
    dataPaths.evidence,
    dataPaths.links,
    dataPaths.tagChanges,
    dataPaths.issues,
    dataPaths.invariants,
    dataPaths.rawIssues,
    dataPaths.rawInvariants,
    dataPaths.configuredDecisions,
    dataPaths.decisionCandidates,
    dataPaths.reviewWorklist
  ]
    .map((filePath) => {
      if (!fs.existsSync(filePath)) return `${filePath}:missing`;
      const stat = fs.statSync(filePath);
      return `${filePath}:${stat.size}:${stat.mtimeMs}`;
    })
    .join('|');
}

function bool(value: string | undefined) {
  return String(value ?? '').toLowerCase() === 'true';
}

function cleanTag(value: string | undefined) {
  const tag = String(value ?? '').trim();
  return /^\d+\.0$/.test(tag) ? tag.slice(0, -2) : tag;
}

function numberValue(value: string | undefined) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function statusCounts<T extends { review_status: ReviewStatus }>(items: T[]): StatusCounts {
  const counts: StatusCounts = {
    needs_review: 0,
    watch: 0,
    quiet: 0,
    total: items.length
  };
  for (const item of items) {
    counts[item.review_status] += 1;
  }
  return counts;
}

function laneCountsForTrees(trees: TreeCase[], worklist: ReviewWorklistItem[]): LaneCounts {
  const counts: LaneCounts = {
    needs_human_call: 0,
    suggested_fix: 0,
    total: trees.length
  };
  for (const tree of trees) {
    const lanes = worklistLanesForTree(tree, worklist);
    if (lanes.has('needs_human_call')) counts.needs_human_call += 1;
    if (lanes.has('suggested_fix')) counts.suggested_fix += 1;
  }
  return counts;
}

function laneCountsForCards(cards: TagCard[], cases: TreeCase[], worklist: ReviewWorklistItem[]): LaneCounts {
  const byUid = new Map(cases.map((tree) => [tree.tree_uid, tree]));
  const counts: LaneCounts = {
    needs_human_call: 0,
    suggested_fix: 0,
    total: cards.length
  };
  for (const card of cards) {
    const lanes = worklistLanesForCard(card, byUid, worklist);
    if (lanes.has('needs_human_call')) counts.needs_human_call += 1;
    if (lanes.has('suggested_fix')) counts.suggested_fix += 1;
  }
  return counts;
}

function worklistLanesForTree(tree: TreeCase, worklist: ReviewWorklistItem[]) {
  return new Set(worklist.filter((item) => worklistItemMatchesTree(item, tree)).map((item) => item.lane));
}

function worklistLanesForCard(card: TagCard, casesByUid: Map<string, TreeCase>, worklist: ReviewWorklistItem[]) {
  const lanes = new Set<string>();
  for (const uid of card.canonical_tree_uids.split('|').filter(Boolean)) {
    const tree = casesByUid.get(uid);
    if (!tree) continue;
    for (const lane of worklistLanesForTree(tree, worklist)) {
      lanes.add(lane);
    }
  }
  return lanes;
}

function cardHasWorklistLane(card: TagCard, casesByUid: Map<string, TreeCase>, worklist: ReviewWorklistItem[], lane: string) {
  return worklistLanesForCard(card, casesByUid, worklist).has(lane);
}

function treeHasWorklistLane(tree: TreeCase, worklist: ReviewWorklistItem[], lane: string) {
  return worklistLanesForTree(tree, worklist).has(lane);
}

function splitCodes(value: string | undefined) {
  return String(value ?? '')
    .split('|')
    .map((code) => code.trim())
    .filter(Boolean);
}

function reviewReasons(record: CsvRecord) {
  const invariantCodes = splitCodes(record.invariant_codes);
  const reasons = invariantCodes.filter((code) => humanReviewCodes.has(code));
  if (record.review_bucket === 'candidate_identity_link') {
    reasons.unshift('candidate_identity_link');
  }
  if (record.first_seen_in_october_2025 === 'True' || record.first_seen_in_october_2025 === 'true') {
    reasons.push('new_in_october_2025');
  }
  return [...new Set(reasons)];
}

function reviewStatus(record: CsvRecord) {
  if (reviewReasons(record).length > 0) return 'needs_review' as const;
  if (splitCodes(record.invariant_codes).some((code) => watchCodes.has(code))) return 'watch' as const;
  if (watchBuckets.has(record.review_bucket ?? '') || splitCodes(record.note_flags).length > 0) return 'watch' as const;
  return 'quiet' as const;
}

function reviewStatusLabel(status: ReviewStatus) {
  if (status === 'needs_review') return 'Review';
  if (status === 'watch') return 'Watch';
  return 'Quiet';
}

function normalizeCase(record: CsvRecord): TreeCase {
  const status = reviewStatus(record);
  return {
    tree_uid: record.tree_uid ?? '',
    site: record.site ?? '',
    plot: record.plot ?? '',
    identity_tag: record.identity_tag ?? '',
    identity_label: record.identity_label ?? '',
    public_tags: record.public_tags ?? '',
    first_survey: record.first_survey ?? '',
    last_survey: record.last_survey ?? '',
    present_in_october_2025: bool(record.present_in_october_2025),
    first_seen_in_october_2025: bool(record.first_seen_in_october_2025),
    missing_from_october_2025: bool(record.missing_from_october_2025),
    last_pre_october_status: record.last_pre_october_status ?? '',
    primary_taxon_code: record.primary_taxon_code ?? '',
    taxon_codes: record.taxon_codes ?? '',
    max_dbh_mm: record.max_dbh_mm ?? '',
    october_max_dbh_mm: record.october_max_dbh_mm ?? '',
    max_stem_count: record.max_stem_count ?? '',
    invariant_codes: record.invariant_codes ?? '',
    invariant_actions: record.invariant_actions ?? '',
    diagnostic_codes: record.diagnostic_codes ?? '',
    evidence_rows: record.evidence_rows ?? '',
    primary_evidence_rows: record.primary_evidence_rows ?? '',
    accepted_input_evidence_rows: record.accepted_input_evidence_rows ?? '',
    note_flags: record.note_flags ?? '',
    candidate_link_count: record.candidate_link_count ?? '',
    best_candidate_link_score: record.best_candidate_link_score ?? '',
    review_bucket: record.review_bucket ?? '',
    review_status: status,
    review_status_label: reviewStatusLabel(status),
    review_reasons: reviewReasons(record).join('|'),
    priority_score: numberValue(record.priority_score),
    summary: record.summary ?? ''
  };
}

function syntheticCaseFromHistory(rows: CanonicalHistoryRow[]): TreeCase {
  const ordered = [...rows].sort((a, b) => surveySortValueHistory(a).localeCompare(surveySortValueHistory(b)));
  const first = ordered[0];
  const octoberRows = ordered.filter((row) => row.survey_id === 'October_2025');
  const preOctoberRows = ordered.filter((row) => row.survey_id !== 'October_2025');
  const lastPreOctober = preOctoberRows.at(-1);
  const dbhs = ordered.map((row) => numberValue(row.dbh_mm)).filter((dbh) => dbh > 0);
  const octoberDbhs = octoberRows.map((row) => numberValue(row.dbh_mm)).filter((dbh) => dbh > 0);
  const stemCounts = new Map<string, number>();
  for (const row of ordered) {
    stemCounts.set(row.survey_id, (stemCounts.get(row.survey_id) ?? 0) + 1);
  }
  const publicTags = uniqueStrings(ordered.map((row) => cleanTag(row.public_tag || row.tree_number)));
  const taxonCodes = uniqueStrings(ordered.map((row) => row.taxon_code));
  const primaryTaxonCode = modeString(ordered.map((row) => row.taxon_code));
  return {
    tree_uid: first.tree_uid,
    site: first.site,
    plot: first.plot,
    identity_tag: cleanTag(first.identity_tag || first.tree_number || first.public_tag),
    identity_label: first.identity_label || `${first.plot}/${cleanTag(first.identity_tag || first.public_tag)}`,
    public_tags: publicTags.join('|'),
    first_survey: ordered[0]?.survey_id ?? '',
    last_survey: ordered.at(-1)?.survey_id ?? '',
    present_in_october_2025: octoberRows.length > 0,
    first_seen_in_october_2025: ordered[0]?.survey_id === 'October_2025',
    missing_from_october_2025: octoberRows.length === 0 && preOctoberRows.length > 0,
    last_pre_october_status: lastPreOctober?.interpreted_status ?? '',
    primary_taxon_code: primaryTaxonCode,
    taxon_codes: taxonCodes.join('|'),
    max_dbh_mm: dbhs.length ? String(Math.max(...dbhs)) : '',
    october_max_dbh_mm: octoberDbhs.length ? String(Math.max(...octoberDbhs)) : '',
    max_stem_count: String(Math.max(0, ...stemCounts.values())),
    invariant_codes: '',
    invariant_actions: '',
    diagnostic_codes: '',
    evidence_rows: '',
    primary_evidence_rows: '',
    accepted_input_evidence_rows: '',
    note_flags: '',
    candidate_link_count: '',
    best_candidate_link_score: '',
    review_bucket: '',
    review_status: 'quiet',
    review_status_label: reviewStatusLabel('quiet'),
    review_reasons: '',
    priority_score: 0,
    summary: `${first.plot}/${cleanTag(first.identity_tag || first.public_tag)} is present in canonical history.`
  };
}

function buildAllTreeCases(cases: TreeCase[], history: CanonicalHistoryRow[]): TreeCase[] {
  const historyRowsByUid = new Map<string, CanonicalHistoryRow[]>();
  for (const row of history) {
    const rows = historyRowsByUid.get(row.tree_uid);
    if (rows) {
      rows.push(row);
    } else {
      historyRowsByUid.set(row.tree_uid, [row]);
    }
  }

  const allTrees = new Map<string, TreeCase>();
  for (const rows of historyRowsByUid.values()) {
    allTrees.set(rows[0].tree_uid, syntheticCaseFromHistory(rows));
  }
  for (const tree of cases) {
    allTrees.set(tree.tree_uid, tree);
  }
  return [...allTrees.values()];
}

function uniqueStrings(values: Array<string | undefined>) {
  return [...new Set(values.map((value) => String(value ?? '').trim()).filter(Boolean))].sort();
}

function modeString(values: Array<string | undefined>) {
  const counts = new Map<string, number>();
  for (const value of values) {
    const cleaned = String(value ?? '').trim();
    if (!cleaned) continue;
    counts.set(cleaned, (counts.get(cleaned) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? '';
}

function asHistory(record: CsvRecord): CanonicalHistoryRow {
  return record as unknown as CanonicalHistoryRow;
}

function asEvidence(record: CsvRecord, relation = ''): EvidenceObservation {
  return { ...(record as unknown as EvidenceObservation), evidence_relation: relation };
}

function asDiagnosticIssue(record: CsvRecord): DiagnosticIssue {
  return record as unknown as DiagnosticIssue;
}

function asInvariantFinding(record: CsvRecord): InvariantFinding {
  return record as unknown as InvariantFinding;
}

function asConfiguredDecision(record: CsvRecord): ConfiguredDecision {
  return record as unknown as ConfiguredDecision;
}

function asDecisionCandidate(record: CsvRecord): DecisionCandidate {
  return record as unknown as DecisionCandidate;
}

function asReviewWorklistItem(record: CsvRecord): ReviewWorklistItem {
  return record as unknown as ReviewWorklistItem;
}

function tagsForCase(tree: TreeCase) {
  return new Set(
    [tree.identity_tag, ...tree.public_tags.split('|')]
      .map(cleanTag)
      .filter(Boolean)
  );
}

function parseJsonObject(value: string | undefined): Record<string, unknown> {
  try {
    const parsed = JSON.parse(value || '{}') as unknown;
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? (parsed as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

function cleanSelectorValue(value: unknown) {
  return cleanTag(String(value ?? ''));
}

function selectorTags(selector: Record<string, unknown>) {
  return [
    selector.identity_tag,
    selector.public_tag,
    selector.tag,
    selector.tree_number,
    selector.old_tag,
    selector.new_tag
  ]
    .map(cleanSelectorValue)
    .filter(Boolean);
}

function selectorPlot(selector: Record<string, unknown>) {
  return String(selector.plot ?? selector.old_plot ?? selector.new_plot ?? '').trim().toUpperCase();
}

function selectorMatchesTree(selector: Record<string, unknown>, tree: TreeCase) {
  const plot = selectorPlot(selector);
  if (plot && plot !== tree.plot) return false;
  const selectorTagSet = new Set(selectorTags(selector));
  if (!selectorTagSet.size) return false;
  const treeTags = tagsForCase(tree);
  return [...selectorTagSet].some((tag) => treeTags.has(tag));
}

function configuredDecisionMatchesTree(decision: ConfiguredDecision, tree: TreeCase) {
  const selector = parseJsonObject(decision.selector);
  if (selectorMatchesTree(selector, tree)) return true;
  for (const nested of ['source', 'selector']) {
    const value = selector[nested];
    if (value && typeof value === 'object' && !Array.isArray(value) && selectorMatchesTree(value as Record<string, unknown>, tree)) {
      return true;
    }
  }
  return false;
}

function treeLikeRecordMatchesTree(record: { tree_uid: string; plot: string; identity_tag: string; public_tag?: string }, tree: TreeCase) {
  if (record.tree_uid && record.tree_uid === tree.tree_uid) return true;
  if (record.plot && record.plot !== tree.plot) return false;
  const rowTags = [record.identity_tag, record.public_tag].map(cleanTag).filter(Boolean);
  if (!rowTags.length) return false;
  const treeTags = tagsForCase(tree);
  return rowTags.some((tag) => treeTags.has(tag));
}

function selectorMatchesTreeUid(selector: Record<string, unknown>, tree: TreeCase) {
  return [selector.tree_uid, selector.source_tree_uid, selector.target_tree_uid].map(String).includes(tree.tree_uid);
}

function candidateMatchesTree(candidate: DecisionCandidate, tree: TreeCase) {
  if (treeLikeRecordMatchesTree(candidate, tree)) return true;
  const selector = parseJsonObject(candidate.selector);
  return selectorMatchesTreeUid(selector, tree) || selectorMatchesTree(selector, tree);
}

function worklistItemMatchesTree(item: ReviewWorklistItem, tree: TreeCase) {
  if (String(item.related_tree_uids ?? '').split('|').filter(Boolean).includes(tree.tree_uid)) return true;
  if (treeLikeRecordMatchesTree({ ...item, public_tag: item.public_tags }, tree)) return true;
  return item.candidate_decision_ids
    .split('|')
    .filter(Boolean)
    .some((candidateId) => candidateId.includes(tree.tree_uid));
}

function diagnosticMatchesTree(row: DiagnosticIssue | InvariantFinding, tree: TreeCase) {
  if (row.tree_uid && row.tree_uid === tree.tree_uid) return true;
  if (row.plot && row.plot !== tree.plot) return false;
  const rowTags = [row.identity_tag, row.public_tag].map(cleanTag).filter(Boolean);
  if (!rowTags.length) return false;
  const treeTags = tagsForCase(tree);
  return rowTags.some((tag) => treeTags.has(tag));
}

function configuredDecisionsForTrees(decisions: ConfiguredDecision[], trees: TreeCase[]) {
  return decisions.filter((decision) => trees.some((tree) => configuredDecisionMatchesTree(decision, tree)));
}

function decisionCandidatesForTrees(candidates: DecisionCandidate[], trees: TreeCase[]) {
  return candidates.filter((candidate) => trees.some((tree) => candidateMatchesTree(candidate, tree)));
}

function reviewWorklistForTrees(worklist: ReviewWorklistItem[], trees: TreeCase[]) {
  return worklist.filter((item) => trees.some((tree) => worklistItemMatchesTree(item, tree)));
}

function issuesForTrees(issues: DiagnosticIssue[], trees: TreeCase[]) {
  return issues.filter((issue) => trees.some((tree) => diagnosticMatchesTree(issue, tree)));
}

function invariantsForTrees(invariants: InvariantFinding[], trees: TreeCase[]) {
  return invariants.filter((finding) => trees.some((tree) => diagnosticMatchesTree(finding, tree)));
}

function taxonForCase(tree: TreeCase) {
  return tree.primary_taxon_code || tree.taxon_codes.split('|').find(Boolean) || '';
}

function dbhForCase(tree: TreeCase) {
  return numberValue(tree.october_max_dbh_mm || tree.max_dbh_mm);
}

function evidenceDbh(row: EvidenceObservation) {
  return numberValue(row.dbh_mm_raw);
}

function evidenceTagMatch(row: EvidenceObservation, plot: string, tags: Set<string>) {
  if (row.plot !== plot) return false;
  if (tags.has(cleanTag(row.public_tag_raw)) || tags.has(cleanTag(row.old_tag_raw))) return true;
  return [...tags].some((tag) => row.tree_code_raw.includes(`${plot}_${tag}_`));
}

function tagMentionRegex(tags: Set<string>, plot: string) {
  const patterns = [...tags]
    .filter((tag) => tag.length >= 3)
    .flatMap((tag) => [
      `(?:^|\\D)${escapeRegex(tag)}(?:\\D|$)`,
      `${escapeRegex(plot)}[ _/-]?${escapeRegex(tag)}`
    ]);
  return patterns.length ? new RegExp(patterns.join('|'), 'i') : null;
}

function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function uniqueEvidence(rows: EvidenceObservation[]) {
  const seen = new Set<string>();
  return rows.filter((row) => {
    if (seen.has(row.evidence_id)) return false;
    seen.add(row.evidence_id);
    return true;
  });
}

function sortEvidence(rows: EvidenceObservation[]) {
  const rankWeights: Record<string, number> = {
    accepted_input: 0,
    source_table: 1,
    derived_context: 2
  };
  return [...rows].sort((a, b) => {
    const dateDelta = (a.date || '').localeCompare(b.date || '');
    if (dateDelta !== 0) return dateDelta;
    const rankDelta = (rankWeights[a.evidence_rank] ?? 9) - (rankWeights[b.evidence_rank] ?? 9);
    if (rankDelta !== 0) return rankDelta;
    return numberValue(a.source_row) - numberValue(b.source_row);
  });
}

function similarDbh(a: number, b: number) {
  if (!a || !b) return false;
  const delta = Math.abs(a - b);
  return delta <= 15 || delta / Math.max(a, b) <= 0.12;
}

function surveySortValue(row: EvidenceObservation) {
  return row.date || row.survey_id || row.year || '';
}

function surveySortValueHistory(row: CanonicalHistoryRow) {
  return row.date || row.survey_id || '';
}

function buildSurveyTimeline(history: CanonicalHistoryRow[]): SurveyTimelineItem[] {
  const surveys = new Map<string, SurveyTimelineItem>();
  for (const row of history) {
    if (!row.survey_id) continue;
    const existing = surveys.get(row.survey_id);
    if (!existing || (!existing.date && row.date)) {
      surveys.set(row.survey_id, { survey_id: row.survey_id, date: row.date || '' });
    }
  }
  return [...surveys.values()].sort((a, b) => (a.date || a.survey_id).localeCompare(b.date || b.survey_id));
}

function tagKey(mode: 'tags' | 'tag-plot', row: EvidenceObservation) {
  const tag = cleanTag(row.public_tag_raw || row.old_tag_raw) || 'untagged';
  if (mode === 'tag-plot') return `${row.plot || 'plot?'}:${tag}`;
  return tag;
}

function buildTagCards(
  mode: 'tags' | 'tag-plot',
  evidence: EvidenceObservation[],
  cases: TreeCase[],
  history: CanonicalHistoryRow[]
): TagCard[] {
  const grouped = new Map<string, EvidenceObservation[]>();
  for (const row of evidence) {
    const tag = cleanTag(row.public_tag_raw || row.old_tag_raw);
    if (!tag) continue;
    const key = tagKey(mode, row);
    const rows = grouped.get(key);
    if (rows) {
      rows.push(row);
    } else {
      grouped.set(key, [row]);
    }
  }

  const casesByTag = new Map<string, TreeCase[]>();
  const casesByPlotTag = new Map<string, TreeCase[]>();
  for (const tree of cases) {
    for (const tag of tagsForCase(tree)) {
      const byTag = casesByTag.get(tag);
      if (byTag) {
        byTag.push(tree);
      } else {
        casesByTag.set(tag, [tree]);
      }
      const plotTag = `${tree.plot}:${tag}`;
      const byPlotTag = casesByPlotTag.get(plotTag);
      if (byPlotTag) {
        byPlotTag.push(tree);
      } else {
        casesByPlotTag.set(plotTag, [tree]);
      }
    }
  }
  const historyCountByUid = new Map<string, number>();
  for (const row of history) {
    historyCountByUid.set(row.tree_uid, (historyCountByUid.get(row.tree_uid) ?? 0) + 1);
  }

  return [...grouped.entries()]
    .map(([key, rows]) => {
      const first = rows[0];
      const tag = mode === 'tag-plot' ? key.split(':').slice(1).join(':') : key;
      const plot = mode === 'tag-plot' ? first.plot : '';
      const matchingCases = mode === 'tags' ? (casesByTag.get(tag) ?? []) : (casesByPlotTag.get(`${plot}:${tag}`) ?? []);
      const matchingUids = new Set(matchingCases.map((tree) => tree.tree_uid));
      const surveys = rows.map(surveySortValue).filter(Boolean).sort();
      const dbhs = rows.map(evidenceDbh).filter((dbh) => dbh > 0);
      const taxa = new Set(rows.map((row) => row.taxon_raw || `${row.genus_raw} ${row.species_raw}`.trim()).filter(Boolean));
      const sources = new Set(rows.map((row) => `${row.source_path}:${row.source_sheet}`).filter(Boolean));
      const plots = new Set(rows.map((row) => row.plot).filter(Boolean));
      const zones = new Set(rows.map((row) => row.zone).filter(Boolean));
      const matchingHistoryCount = [...matchingUids].reduce((count, uid) => count + (historyCountByUid.get(uid) ?? 0), 0);
      const reviewCaseCount = matchingCases.filter((tree) => tree.review_status === 'needs_review').length;
      const watchCaseCount = matchingCases.filter((tree) => tree.review_status === 'watch').length;
      const quietCaseCount = matchingCases.filter((tree) => tree.review_status === 'quiet').length;
      const reviewStatus: ReviewStatus = reviewCaseCount > 0 ? 'needs_review' : watchCaseCount > 0 ? 'watch' : 'quiet';
      return {
        key,
        mode,
        tag,
        plot,
        plots: [...plots].sort().join('|'),
        zone: mode === 'tag-plot' ? first.zone : '',
        zones: [...zones].sort().join('|'),
        label: mode === 'tag-plot' ? `${plot}/${tag}` : tag,
        evidence_count: rows.length,
        canonical_tree_count: matchingUids.size,
        canonical_tree_uids: [...matchingUids].join('|'),
        first_survey: surveys[0] ?? '',
        last_survey: surveys.at(-1) ?? '',
        max_dbh_mm: dbhs.length ? String(Math.max(...dbhs)) : '',
        taxa: [...taxa].sort().slice(0, 6).join('|'),
        source_count: sources.size,
        review_case_count: reviewCaseCount,
        watch_case_count: watchCaseCount,
        quiet_case_count: quietCaseCount,
        review_status: reviewStatus
      };
    })
    .sort((a, b) => b.evidence_count - a.evidence_count || a.label.localeCompare(b.label));
}

function buildTagDossier(
  selected: TagCard,
  evidence: EvidenceObservation[],
  cases: TreeCase[],
  history: CanonicalHistoryRow[],
  links: CandidateLink[],
  tagChanges: TagChangeAssertion[],
  issues: DiagnosticIssue[],
  invariants: InvariantFinding[],
  rawIssues: DiagnosticIssue[],
  rawInvariants: InvariantFinding[],
  configuredDecisions: ConfiguredDecision[],
  decisionCandidates: DecisionCandidate[],
  reviewWorklist: ReviewWorklistItem[]
): TagDossier {
  const rows = evidence
    .filter((row) => {
      if (cleanTag(row.public_tag_raw || row.old_tag_raw) !== selected.tag) return false;
      return selected.mode === 'tags' || row.plot === selected.plot;
    })
    .map((row) => asEvidence(row, selected.mode === 'tag-plot' ? 'tag_plot_evidence' : 'tag_evidence'));
  const treeCases = cases.filter((tree) => {
    const treeTags = tagsForCase(tree);
    if (!treeTags.has(selected.tag)) return false;
    return selected.mode === 'tags' || tree.plot === selected.plot;
  });
  const treeScopes = buildTagTreeScopes(selected, treeCases, cases, links, tagChanges);
  const treeUids = new Set(treeScopes.map((scope) => scope.tree_uid));
  const scopedTreeCases = cases.filter((tree) => treeUids.has(tree.tree_uid));
  const treeHistory = history
    .filter((row) => treeUids.has(row.tree_uid))
    .sort((a, b) => surveySortValueHistory(a).localeCompare(surveySortValueHistory(b)));

  return {
    selected,
    evidence: sortEvidence(uniqueEvidence(rows)),
    treeCases: scopedTreeCases,
    treeScopes,
    history: treeHistory,
    issues: issues.filter((issue) => treeUids.has(issue.tree_uid)),
    invariants: invariants.filter((finding) => treeUids.has(finding.tree_uid)),
    configuredDecisions: configuredDecisionsForTrees(configuredDecisions, scopedTreeCases),
    decisionCandidates: decisionCandidatesForTrees(decisionCandidates, scopedTreeCases),
    reviewWorklist: reviewWorklistForTrees(reviewWorklist, scopedTreeCases),
    rawIssues: issuesForTrees(rawIssues, scopedTreeCases),
    rawInvariants: invariantsForTrees(rawInvariants, scopedTreeCases)
  };
}

function buildTagTreeScopes(
  selected: TagCard,
  directTrees: TreeCase[],
  cases: TreeCase[],
  links: CandidateLink[],
  tagChanges: TagChangeAssertion[]
): TagTreeScope[] {
  const scopes = new Map<string, TagTreeScope>();
  const directUids = new Set(directTrees.map((tree) => tree.tree_uid));
  const addScope = (tree: TreeCase | undefined, scope: TagTreeScope['scope'], scope_label: string, detail: string) => {
    if (!tree) return;
    const key = `${tree.tree_uid}:${scope}:${detail}`;
    scopes.set(key, { tree_uid: tree.tree_uid, scope, scope_label, detail });
  };

  for (const tree of directTrees) {
    addScope(tree, 'direct', 'Direct', selected.mode === 'tag-plot' ? `${tree.plot}/${selected.tag}` : selected.tag);
  }

  const byUid = new Map(cases.map((tree) => [tree.tree_uid, tree]));
  const byPlotTag = indexCasesByPlotTag(cases);
  for (const link of links) {
    const sourceDirect = directUids.has(link.source_tree_uid);
    const targetDirect = directUids.has(link.target_tree_uid);
    if (!sourceDirect && !targetDirect) continue;
    const source = byUid.get(link.source_tree_uid);
    const target = byUid.get(link.target_tree_uid);
    addScope(source, 'candidate_link', 'Candidate', `${link.link_type} ${link.score}`);
    addScope(target, 'candidate_link', 'Candidate', `${link.link_type} ${link.score}`);
  }

  for (const change of tagChanges) {
    const oldMatches = selectedTagSideMatches(selected, change.old_plot, change.old_tag);
    const newMatches = selectedTagSideMatches(selected, change.new_plot, change.new_tag);
    if (!oldMatches && !newMatches) continue;
    for (const tree of byPlotTag.get(`${change.old_plot}:${cleanTag(change.old_tag)}`) ?? []) {
      addScope(tree, 'tag_change', 'Tag change', `${change.old_plot}/${change.old_tag} -> ${change.new_plot}/${change.new_tag}`);
    }
    for (const tree of byPlotTag.get(`${change.new_plot}:${cleanTag(change.new_tag)}`) ?? []) {
      addScope(tree, 'tag_change', 'Tag change', `${change.old_plot}/${change.old_tag} -> ${change.new_plot}/${change.new_tag}`);
    }
  }

  if (selected.mode === 'tag-plot') {
    for (const tree of cases) {
      if (tree.plot === selected.plot) continue;
      if (!tagsForCase(tree).has(selected.tag)) continue;
      addScope(tree, 'same_tag_other_plot', 'Same tag other plot', `${tree.plot}/${selected.tag}`);
    }
  }

  return [...scopes.values()].sort(
    (a, b) => scopeWeight(a.scope) - scopeWeight(b.scope) || a.detail.localeCompare(b.detail) || a.tree_uid.localeCompare(b.tree_uid)
  );
}

function selectedTagSideMatches(selected: TagCard, plot: string, tag: string) {
  if (cleanTag(tag) !== selected.tag) return false;
  return selected.mode === 'tags' || plot === selected.plot;
}

function indexCasesByPlotTag(cases: TreeCase[]) {
  const index = new Map<string, TreeCase[]>();
  for (const tree of cases) {
    for (const tag of tagsForCase(tree)) {
      const key = `${tree.plot}:${tag}`;
      const rows = index.get(key);
      if (rows) {
        rows.push(tree);
      } else {
        index.set(key, [tree]);
      }
    }
  }
  return index;
}

function scopeWeight(scope: TagTreeScope['scope']) {
  return { direct: 0, tag_change: 1, candidate_link: 2, same_tag_other_plot: 3 }[scope];
}

function tagCardHasEvidenceIn(card: TagCard, evidence: EvidenceObservation[], filters: { plot: string; zone: string }) {
  if (!filters.plot && !filters.zone) return true;
  const plots = new Set(card.plots.split('|').filter(Boolean));
  const zones = new Set(card.zones.split('|').filter(Boolean));
  return (!filters.plot || plots.has(filters.plot)) && (!filters.zone || zones.has(filters.zone));
}

function buildDossier(
  selected: TreeCase,
  allCases: TreeCase[],
  history: CanonicalHistoryRow[],
  evidence: EvidenceObservation[],
  links: CandidateLink[],
  tagChanges: TagChangeAssertion[],
  decisions: CanonicalReviewDecision[],
  issues: DiagnosticIssue[],
  invariants: InvariantFinding[],
  rawIssues: DiagnosticIssue[],
  rawInvariants: InvariantFinding[],
  configuredDecisions: ConfiguredDecision[],
  decisionCandidates: DecisionCandidate[],
  reviewWorklist: ReviewWorklistItem[]
): CanonicalDossier {
  const tags = tagsForCase(selected);
  const plot = selected.plot;
  const selectedDbh = dbhForCase(selected);
  const selectedTaxon = taxonForCase(selected);
  const mentionRegex = tagMentionRegex(tags, plot);
  const selectedHistory = history.filter((row) => row.tree_uid === selected.tree_uid);
  const directEvidence = evidence.filter((row) => evidenceTagMatch(row, plot, tags)).map((row) => asEvidence(row, 'direct_tag'));

  const candidateLinks = links.filter(
    (link) => link.source_tree_uid === selected.tree_uid || link.target_tree_uid === selected.tree_uid
  );
  const linkedTags = new Set<string>();
  for (const link of candidateLinks) {
    linkedTags.add(link.source_identity_tag);
    linkedTags.add(link.target_identity_tag);
  }
  for (const change of tagChanges) {
    if (change.old_plot === plot && tags.has(change.old_tag)) linkedTags.add(change.new_tag);
    if (change.new_plot === plot && tags.has(change.new_tag)) linkedTags.add(change.old_tag);
  }
  for (const tag of tags) linkedTags.delete(tag);

  const linkedEvidence = evidence
    .filter((row) => evidenceTagMatch(row, plot, linkedTags))
    .map((row) => asEvidence(row, 'linked_tag'));
  const noteMentionEvidence = mentionRegex
    ? evidence
        .filter((row) => row.notes_raw && mentionRegex.test(row.notes_raw))
        .map((row) => asEvidence(row, 'note_mention'))
    : [];
  const sameTagOtherPlots = evidence
    .filter((row) => row.plot !== plot && tags.has(row.public_tag_raw))
    .map((row) => asEvidence(row, 'same_tag_other_plot'));
  const similarDbhSamePlot = evidence
    .filter((row) => {
      if (row.plot !== plot || tags.has(row.public_tag_raw)) return false;
      if (selectedTaxon && row.taxon_raw && !row.taxon_raw.toUpperCase().includes(selectedTaxon.slice(0, 3))) {
        return false;
      }
      return similarDbh(selectedDbh, numberValue(row.dbh_mm_raw));
    })
    .map((row) => asEvidence(row, 'similar_dbh_same_plot'));
  const complementaryMissingSamePlot = allCases.filter((tree) => {
    if (tree.tree_uid === selected.tree_uid || tree.plot !== plot || !tree.missing_from_october_2025) return false;
    return similarDbh(selectedDbh, dbhForCase(tree));
  });
  const relevantTagChanges = tagChanges.filter(
    (change) =>
      (change.old_plot === plot && tags.has(change.old_tag)) ||
      (change.new_plot === plot && tags.has(change.new_tag)) ||
      (change.old_plot === plot && linkedTags.has(change.old_tag)) ||
      (change.new_plot === plot && linkedTags.has(change.new_tag))
  );

  return {
    selected,
    history: selectedHistory,
    directEvidence: sortEvidence(uniqueEvidence(directEvidence)),
    linkedEvidence: sortEvidence(uniqueEvidence(linkedEvidence)),
    noteMentionEvidence: sortEvidence(uniqueEvidence(noteMentionEvidence)),
    sameTagOtherPlots: sortEvidence(uniqueEvidence(sameTagOtherPlots)),
    similarDbhSamePlot: sortEvidence(uniqueEvidence(similarDbhSamePlot)).slice(0, 120),
    complementaryMissingSamePlot: complementaryMissingSamePlot.slice(0, 40),
    candidateLinks,
    tagChanges: relevantTagChanges,
    decisions: decisions.filter((decision) => decision.tree_uid === selected.tree_uid),
    issues: issues.filter((issue) => issue.tree_uid === selected.tree_uid),
    invariants: invariants.filter((finding) => finding.tree_uid === selected.tree_uid),
    configuredDecisions: configuredDecisionsForTrees(configuredDecisions, [selected]),
    decisionCandidates: decisionCandidatesForTrees(decisionCandidates, [selected]),
    reviewWorklist: reviewWorklistForTrees(reviewWorklist, [selected]),
    rawIssues: issuesForTrees(rawIssues, [selected]),
    rawInvariants: invariantsForTrees(rawInvariants, [selected])
  };
}

export function loadCanonicalData(url: URL) {
  const loaded = loadData();
  const allCases = loaded.allTrees;
  const history = loaded.history;
  const evidence = loaded.evidence;
  const links = loaded.links;
  const tagChanges = loaded.tagChanges;
  const issues = loaded.issues;
  const invariants = loaded.invariants;
  const rawIssues = loaded.rawIssues;
  const rawInvariants = loaded.rawInvariants;
  const configuredDecisions = loaded.configuredDecisions;
  const decisionCandidates = loaded.decisionCandidates;
  const reviewWorklist = loaded.reviewWorklist;
  const decisions = readJsonl<CanonicalReviewDecision>(dataPaths.decisions);
  const requestedMode = url.searchParams.get('mode');
  const selectedUid = url.searchParams.get('uid') ?? '';
  const selectedTagKey = url.searchParams.get('tagkey') ?? '';
  const mode: BrowserMode =
    requestedMode === 'tag-plot' || requestedMode === 'trees' || requestedMode === 'tags'
      ? requestedMode
      : selectedUid
        ? 'trees'
        : selectedTagKey.includes(':')
          ? 'tag-plot'
          : 'tags';
  const filters = {
    bucket: url.searchParams.get('bucket') ?? '',
    status: url.searchParams.get('status') ?? '',
    lane: url.searchParams.get('lane') ?? '',
    plot: (url.searchParams.get('plot') ?? '').toUpperCase(),
    zone: (url.searchParams.get('zone') ?? '').toUpperCase(),
    q: (url.searchParams.get('q') ?? '').trim().toLowerCase()
  };
  const bucketCounts = loaded.bucketCounts;
  const tagMode = mode === 'trees' ? 'tag-plot' : mode;
  let tagCards = loaded.tagCards[tagMode];
  if (filters.plot || filters.zone) {
    tagCards =
      mode === 'tags'
        ? tagCards.filter((card) => tagCardHasEvidenceIn(card, evidence, filters))
        : tagCards.filter(
            (card) => (!filters.plot || card.plot === filters.plot) && (!filters.zone || card.zone === filters.zone)
          );
  }
  if (filters.q) {
    tagCards = tagCards.filter((card) =>
      [card.label, card.tag, card.plot, card.zone, card.taxa, card.canonical_tree_uids].join(' ').toLowerCase().includes(filters.q)
    );
  }
  const casesByUid = new Map(allCases.map((tree) => [tree.tree_uid, tree]));
  const tagLaneCounts = laneCountsForCards(tagCards, allCases, reviewWorklist);
  if (filters.lane === 'needs_human_call' || filters.lane === 'suggested_fix') {
    tagCards = tagCards.filter((card) => cardHasWorklistLane(card, casesByUid, reviewWorklist, filters.lane));
  }
  const tagStatusCounts = statusCounts(tagCards);
  if (filters.status === 'needs_review' || filters.status === 'watch' || filters.status === 'quiet') {
    tagCards = tagCards.filter((card) => card.review_status === filters.status);
  }
  const totalTagCards = tagCards.length;
  let cases = allCases;
  if (filters.bucket) cases = cases.filter((tree) => tree.review_bucket === filters.bucket);
  if (filters.plot) cases = cases.filter((tree) => tree.plot === filters.plot);
  if (filters.q) {
    cases = cases.filter((tree) =>
      [tree.identity_label, tree.identity_tag, tree.public_tags, tree.primary_taxon_code, tree.summary]
        .join(' ')
        .toLowerCase()
        .includes(filters.q)
    );
  }
  const caseLaneCounts = laneCountsForTrees(cases, reviewWorklist);
  if (filters.lane === 'needs_human_call' || filters.lane === 'suggested_fix') {
    cases = cases.filter((tree) => treeHasWorklistLane(tree, reviewWorklist, filters.lane));
  }
  const caseStatusCounts = statusCounts(cases);
  if (filters.status === 'needs_review' || filters.status === 'watch' || filters.status === 'quiet') {
    cases = cases.filter((tree) => tree.review_status === filters.status);
  }
  cases = [...cases].sort((a, b) => b.priority_score - a.priority_score || a.identity_label.localeCompare(b.identity_label));
  const totalCases = cases.length;
  const selected = allCases.find((tree) => tree.tree_uid === selectedUid) ?? cases[0] ?? null;
  const selectedTag = tagCards.find((card) => card.key === selectedTagKey) ?? tagCards[0] ?? null;

  return {
    mode,
    filters,
    cases: cases.slice(0, listLimit),
    tagCards: tagCards.slice(0, listLimit),
    totalCases,
    totalTagCards,
    listLimit,
    allCaseCount: allCases.length,
    bucketCounts,
    surveys: loaded.surveys,
    statusCounts: mode === 'trees' ? caseStatusCounts : tagStatusCounts,
    laneCounts: mode === 'trees' ? caseLaneCounts : tagLaneCounts,
    selectedUid: selected?.tree_uid ?? '',
    selectedTagKey: selectedTag?.key ?? '',
    tagDossier: selectedTag
      ? buildTagDossier(
          selectedTag,
          evidence,
          allCases,
          history,
          links,
          tagChanges,
          issues,
          invariants,
          rawIssues,
          rawInvariants,
          configuredDecisions,
          decisionCandidates,
          reviewWorklist
        )
      : null,
    dossier: selected
      ? buildDossier(
          selected,
          allCases,
          history,
          evidence,
          links,
          tagChanges,
          decisions,
          issues,
          invariants,
          rawIssues,
          rawInvariants,
          configuredDecisions,
          decisionCandidates,
          reviewWorklist
        )
      : null
  };
}

function loadData() {
  const signature = sourceSignature();
  if (cachedData?.signature === signature) return cachedData.data;

  const cases = readCsv(dataPaths.cases).map(normalizeCase);
  const history = readCsv(dataPaths.history).map(asHistory);
  const surveys = buildSurveyTimeline(history);
  const allTrees = buildAllTreeCases(cases, history);
  const evidence = readCsv(dataPaths.evidence).map((row) => asEvidence(row));
  const links = readCsv(dataPaths.links) as unknown as CandidateLink[];
  const tagChanges = readCsv(dataPaths.tagChanges) as unknown as TagChangeAssertion[];
  const issues = readCsv(dataPaths.issues).map(asDiagnosticIssue);
  const invariants = readCsv(dataPaths.invariants).map(asInvariantFinding);
  const rawIssues = readCsv(dataPaths.rawIssues).map(asDiagnosticIssue);
  const rawInvariants = readCsv(dataPaths.rawInvariants).map(asInvariantFinding);
  const configuredDecisions = readCsv(dataPaths.configuredDecisions).map(asConfiguredDecision);
  const decisionCandidates = readCsv(dataPaths.decisionCandidates).map(asDecisionCandidate);
  const reviewWorklist = readCsv(dataPaths.reviewWorklist).map(asReviewWorklistItem);
  const bucketCounts = cases.reduce<Record<string, number>>((counts, tree) => {
    counts[tree.review_bucket] = (counts[tree.review_bucket] ?? 0) + 1;
    return counts;
  }, {});
  const data = {
    cases,
    allTrees,
    history,
    surveys,
    evidence,
    links,
    tagChanges,
    issues,
    invariants,
    rawIssues,
    rawInvariants,
    configuredDecisions,
    decisionCandidates,
    reviewWorklist,
    tagCards: {
      tags: buildTagCards('tags', evidence, allTrees, history),
      'tag-plot': buildTagCards('tag-plot', evidence, allTrees, history)
    },
    bucketCounts
  };
  cachedData = { signature, data };
  return data;
}

export function appendDecision(decision: Omit<CanonicalReviewDecision, 'key' | 'decided_at'>) {
  fs.mkdirSync(path.dirname(dataPaths.decisions), { recursive: true });
  const payload: CanonicalReviewDecision = {
    ...decision,
    key: `${decision.tree_uid}:${Date.now()}`,
    decided_at: new Date().toISOString()
  };
  fs.appendFileSync(dataPaths.decisions, `${JSON.stringify(payload)}\n`);
}
