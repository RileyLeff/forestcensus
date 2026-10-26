<script lang="ts">
  import { resolve } from '$app/paths';
  import { GitMerge, Info, Layers3, ListTree, Search, Split, Tag, Trees } from 'lucide-svelte';
  import type { PageData } from './$types';
  import type {
    BrowserMode,
    CanonicalHistoryRow,
    ConfiguredDecision,
    DecisionCandidate,
    DiagnosticIssue,
    EvidenceObservation,
    InvariantFinding,
    ReviewWorklistItem,
    SurveyTimelineItem,
    TagCard,
    TagTreeScope,
    TreeCase
  } from '$lib/types';

  type MergedEvidenceRow = {
    key: string;
    representative: EvidenceObservation;
    count: number;
    origins: string[];
  };

  type CanonicalDisplayRow = CanonicalHistoryRow & {
    is_placeholder?: boolean;
    placeholder_kind?: string;
  };

  type CanonicalStemGroup = {
    rank: string;
    rows: CanonicalDisplayRow[];
  };
  type MatrixEvidenceItem = {
    row: CanonicalDisplayRow;
    evidence: EvidenceObservation[];
  };
  type RowMarker = {
    code: string;
    label: string;
    title: string;
    severity: string;
  };
  type CanonicalSection = {
    tree: TreeCase;
    rows: CanonicalHistoryRow[];
    scopes: TagTreeScope[];
  };
  type ScopeFilter = 'all' | TagTreeScope['scope'];
  type LocalHref = `/?${string}`;

  let { data }: { data: PageData } = $props();

  let expandedObservationKey = $state('');
  let canonicalView = $state<'together' | 'stems'>('stems');
  let stemLayout = $state<'stacked' | 'columns'>('columns');
  let scopeFilter = $state<ScopeFilter>('all');

  let mode = $derived(data.mode as BrowserMode);
  let cases = $derived(data.cases as TreeCase[]);
  let tagCards = $derived(data.tagCards as TagCard[]);
  let dossier = $derived(data.dossier);
  let tagDossier = $derived(data.tagDossier);
  let selectedTree = $derived(dossier?.selected);
  let selectedTag = $derived(tagDossier?.selected);
  let canonicalRows = $derived.by((): CanonicalHistoryRow[] => {
    if (mode === 'trees') return dossier?.history ?? [];
    return tagDossier?.history ?? [];
  });
  let surveys = $derived(data.surveys as SurveyTimelineItem[]);
  let canonicalSections = $derived.by((): CanonicalSection[] => buildCanonicalSections());
  let scopeFilters = $derived.by(() => availableScopeFilters());
  let effectiveScopeFilter = $derived.by((): ScopeFilter => {
    const allowed = new Set(scopeFilters.map((filter) => filter.value));
    return allowed.has(scopeFilter) ? scopeFilter : 'all';
  });
  let visibleCanonicalSections = $derived.by((): CanonicalSection[] => {
    if (effectiveScopeFilter === 'all') return canonicalSections;
    return canonicalSections.filter((section) => section.scopes.some((scope) => scope.scope === effectiveScopeFilter));
  });
  let allRelatedEvidence = $derived.by((): EvidenceObservation[] => {
    if (mode !== 'trees') return tagDossier?.evidence ?? [];
    if (!dossier) return [];
    const rows = [
      ...dossier.directEvidence,
      ...dossier.linkedEvidence,
      ...dossier.noteMentionEvidence,
      ...dossier.sameTagOtherPlots,
      ...dossier.similarDbhSamePlot
    ];
    return uniqueEvidence(rows);
  });
  let mergedRelatedEvidence = $derived.by((): MergedEvidenceRow[] => mergeEvidenceRows(allRelatedEvidence));
  let diagnosticIssues = $derived.by((): DiagnosticIssue[] => {
    if (mode === 'trees') return dossier?.issues ?? [];
    return tagDossier?.issues ?? [];
  });
  let invariantFindings = $derived.by((): InvariantFinding[] => {
    if (mode === 'trees') return dossier?.invariants ?? [];
    return tagDossier?.invariants ?? [];
  });
  let configuredDecisions = $derived.by((): ConfiguredDecision[] => {
    if (mode === 'trees') return dossier?.configuredDecisions ?? [];
    return tagDossier?.configuredDecisions ?? [];
  });
  let decisionCandidates = $derived.by((): DecisionCandidate[] => {
    if (mode === 'trees') return dossier?.decisionCandidates ?? [];
    return tagDossier?.decisionCandidates ?? [];
  });
  let reviewWorklist = $derived.by((): ReviewWorklistItem[] => {
    if (mode === 'trees') return dossier?.reviewWorklist ?? [];
    return tagDossier?.reviewWorklist ?? [];
  });
  let suggestedWork = $derived(reviewWorklist.filter((item) => item.lane === 'suggested_fix'));
  let humanWork = $derived(reviewWorklist.filter((item) => item.lane === 'needs_human_call'));
  let candidateById = $derived.by(() => new Map(decisionCandidates.map((candidate) => [candidate.candidate_id, candidate])));
  let rawDiagnosticIssues = $derived.by((): DiagnosticIssue[] => {
    if (mode === 'trees') return dossier?.rawIssues ?? [];
    return tagDossier?.rawIssues ?? [];
  });
  let rawInvariantFindings = $derived.by((): InvariantFinding[] => {
    if (mode === 'trees') return dossier?.rawInvariants ?? [];
    return tagDossier?.rawInvariants ?? [];
  });
  let decisionPhaseSummary = $derived.by(() => {
    const rawIssueCount = rawDiagnosticIssues.filter((issue) => issue.severity !== 'info').length;
    const currentIssueCount = diagnosticIssues.filter((issue) => issue.severity !== 'info').length;
    return {
      rawFlags: rawIssueCount + rawInvariantFindings.length,
      rawIssueCount,
      rawInvariantCount: rawInvariantFindings.length,
      configuredDecisionCount: configuredDecisions.length,
      currentFlags: currentIssueCount + invariantFindings.length,
      currentIssueCount,
      currentInvariantCount: invariantFindings.length
    };
  });

  const modes = [
    ['tags', 'Tags', Tag],
    ['tag-plot', 'Tag x Plot', Split],
    ['trees', 'Tree UUID', Trees]
  ] as const;

  function modeHref(nextMode: BrowserMode): LocalHref {
    const params = new URLSearchParams();
    params.set('mode', nextMode);
    if (data.filters.status) params.set('status', data.filters.status);
    if (data.filters.lane) params.set('lane', data.filters.lane);
    if (data.filters.plot) params.set('plot', data.filters.plot);
    if (data.filters.zone) params.set('zone', data.filters.zone);
    if (data.filters.q) params.set('q', data.filters.q);
    return `/?${params.toString()}`;
  }

  function tagHref(item: TagCard): LocalHref {
    const params = new URLSearchParams();
    params.set('mode', item.mode);
    params.set('tagkey', item.key);
    if (data.filters.status) params.set('status', data.filters.status);
    if (data.filters.lane) params.set('lane', data.filters.lane);
    if (data.filters.plot) params.set('plot', data.filters.plot);
    if (data.filters.zone) params.set('zone', data.filters.zone);
    if (data.filters.q) params.set('q', data.filters.q);
    return `/?${params.toString()}`;
  }

  function caseHref(item: TreeCase): LocalHref {
    const params = new URLSearchParams();
    params.set('mode', 'trees');
    params.set('uid', item.tree_uid);
    if (data.filters.status) params.set('status', data.filters.status);
    if (data.filters.lane) params.set('lane', data.filters.lane);
    if (data.filters.plot) params.set('plot', data.filters.plot);
    if (data.filters.zone) params.set('zone', data.filters.zone);
    if (data.filters.q) params.set('q', data.filters.q);
    return `/?${params.toString()}`;
  }

  function display(value: string | number | boolean | null | undefined) {
    if (value === undefined || value === null || value === '') return '-';
    return String(value);
  }

  function compactValue(value: string | number | null | undefined) {
    const text = String(value ?? '').trim();
    if (!text || text.toUpperCase() === 'NA') return '-';
    const numeric = Number(text);
    return Number.isFinite(numeric) ? String(Number(numeric.toFixed(1))) : text;
  }

  function statusValue(value: string | undefined, one: string, zero: string) {
    const text = String(value ?? '').trim().toLowerCase();
    if (!text || text === 'na') return '-';
    if (text === '1' || text === '1.0' || text === 'true') return one;
    if (text === '0' || text === '0.0' || text === 'false') return zero;
    return text;
  }

  function aliveValue(row: CanonicalDisplayRow) {
    return statusValue(row.alive_observed || row.alive_interpreted, 'A', 'D');
  }

  function standingValue(row: CanonicalDisplayRow) {
    return statusValue(row.standing_observed, 'S', 'F');
  }

  function matrixNotes(row: CanonicalDisplayRow) {
    return [row.notes, row.correction_notes].map((value) => String(value ?? '').trim()).filter(Boolean);
  }

  function matrixNoteTitle(row: CanonicalDisplayRow) {
    const notes = matrixNotes(row);
    return notes.length ? notes.join('\n') : 'No notes';
  }

  function cleanTag(value: string | undefined) {
    const tag = String(value ?? '').trim();
    return /^\d+\.0$/.test(tag) ? tag.slice(0, -2) : tag;
  }

  function cleanComparableValue(value: string | undefined) {
    const cleaned = cleanTag(value);
    if (!cleaned || cleaned.toUpperCase() === 'NA' || cleaned.toLowerCase() === 'not recorded') return '';
    return cleaned;
  }

  function reviewStatusLabel(status: string) {
    if (status === 'needs_review') return 'Review';
    if (status === 'watch') return 'Watch';
    return 'Quiet';
  }

  function reviewReasonLabel(value: string | undefined) {
    return String(value ?? '')
      .split('|')
      .filter(Boolean)
      .slice(0, 3)
      .map((reason) => reason.replaceAll('_', ' '))
      .join(', ');
  }

  function splitReasonCodes(value: string | undefined) {
    return String(value ?? '')
      .split('|')
      .map((reason) => reason.trim())
      .filter(Boolean);
  }

  function codeLabel(code: string) {
    const labels: Record<string, string> = {
      candidate_identity_link: 'candidate link',
      new_in_october_2025: 'new 2025',
      taxon_conflict: 'taxon conflict',
      max_dbh_jump: 'dbh jump',
      ranked_dbh_jump: 'rank jump',
      stem_count_change: 'stem count',
      large_stem_appearance: 'stem appeared',
      large_stem_disappearance: 'stem vanished',
      qualifying_rank_gap: 'rank gap',
      first_qualifying_after_prior_observation: 'late qualify',
      duplicate_dbh_profile_values: 'duplicate dbh',
      subthreshold_measurement: '<50 dbh',
      alive_health_conflict: 'alive/health',
      dead_health_conflict: 'dead/health',
      W_BELOW_THRESHOLD_DBH: '<50 dbh',
      W_TREE_STEM_COUNT_CHANGE: 'stem count',
      W_TREE_LARGE_STEM_APPEARANCE: 'stem appeared',
      W_TREE_LARGE_STEM_DISAPPEARANCE: 'stem vanished',
      W_TREE_RANKED_DBH_JUMP: 'rank jump',
      W_DBH_JUMP: 'dbh jump',
      W_TAXON_CONFLICT: 'taxon conflict',
      I_CORRECTED_ROW: 'corrected'
    };
    return labels[code] ?? code.replace(/^W_/, '').replace(/^I_/, '').replaceAll('_', ' ').toLowerCase();
  }

  function reviewCodesForTree(tree: TreeCase) {
    const primaryReasons = splitReasonCodes(tree.review_reasons);
    const codes = [
      ...(primaryReasons.length ? primaryReasons : [...splitReasonCodes(tree.invariant_codes), ...splitReasonCodes(tree.diagnostic_codes)]),
      ...splitReasonCodes(tree.note_flags).map((flag) => `note:${flag}`)
    ].filter((code) => !code.startsWith('I_') && !code.startsWith('W_'));
    return [...new Set(codes)].slice(0, 8);
  }

  function decisionLabel(decision: ConfiguredDecision) {
    return decision.operation.replaceAll('_', ' ');
  }

  function decisionTitle(decision: ConfiguredDecision) {
    return [decision.source_config, decision.note, decisionSelectorSummary(decision)].filter(Boolean).join('\n');
  }

  function parsedJsonText(value: string | undefined) {
    try {
      return JSON.parse(value || '{}') as Record<string, unknown>;
    } catch {
      return {};
    }
  }

  function decisionSelectorSummary(decision: ConfiguredDecision) {
    const selector = parsedJsonText(decision.selector);
    const nestedSelector = selector.source && typeof selector.source === 'object' ? (selector.source as Record<string, unknown>) : selector;
    const bits = [
      nestedSelector.plot,
      nestedSelector.public_tag ?? nestedSelector.identity_tag ?? nestedSelector.tag ?? nestedSelector.tree_number,
      nestedSelector.survey_id,
      nestedSelector.source_row ? `row ${nestedSelector.source_row}` : ''
    ]
      .map((value) => String(value ?? '').trim())
      .filter(Boolean);
    return bits.join(' / ') || decision.selector;
  }

  function humanLabel(item: ReviewWorklistItem) {
    return item.work_type.replaceAll('_', ' ');
  }

  function workItemTitle(item: ReviewWorklistItem) {
    return [item.summary, item.recommended_action, item.guardrail_notes, item.source_rows_to_check].filter(Boolean).join('\n');
  }

  function candidateLabel(candidate: DecisionCandidate) {
    return candidate.generator.replaceAll('_', ' ');
  }

  function candidateTitle(candidate: DecisionCandidate) {
    return [
      candidate.reason,
      candidate.operation.replaceAll('_', ' '),
      candidate.guardrail_notes,
      candidate.source_file && candidate.source_row ? `${candidate.source_file}:${candidate.source_row}` : candidate.source_file
    ]
      .filter(Boolean)
      .join('\n');
  }

  function candidateIdsForItem(item: ReviewWorklistItem) {
    return item.candidate_decision_ids.split('|').filter(Boolean);
  }

  function candidateCountForItem(item: ReviewWorklistItem) {
    return candidateIdsForItem(item).length;
  }

  function diagnosticCodeCounts(issues: DiagnosticIssue[], invariants: InvariantFinding[]) {
    const counts: Record<string, number> = {};
    for (const issue of issues) {
      if (issue.severity === 'info') continue;
      counts[issue.code] = (counts[issue.code] ?? 0) + 1;
    }
    for (const finding of invariants) {
      counts[finding.code] = (counts[finding.code] ?? 0) + 1;
    }
    return Object.entries(counts)
      .map(([code, count]) => ({ code, count }))
      .sort((a, b) => b.count - a.count || a.code.localeCompare(b.code))
      .slice(0, 8);
  }

  function submitFilters(event: Event) {
    const control = event.currentTarget as HTMLSelectElement;
    control.form?.requestSubmit();
  }

  function rowTaxon(row: EvidenceObservation | CanonicalHistoryRow) {
    if ('taxon_raw' in row) return row.taxon_raw || `${row.genus_raw} ${row.species_raw}`.trim();
    return `${row.genus} ${row.species}`.trim();
  }

  function rowKey(row: CanonicalDisplayRow) {
    return `${row.tree_uid}:${row.survey_id}:${row.source_file}:${row.source_row}:${row.stem_rank}`;
  }

  function numericString(value: string | undefined) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? String(parsed) : String(value ?? '').trim();
  }

  function parsedDetails(row: { details: string }) {
    try {
      return JSON.parse(row.details || '{}') as Record<string, unknown>;
    } catch {
      return {};
    }
  }

  function rankMatches(details: Record<string, unknown>, rank: string) {
    const affected = details.affected_ranks;
    if (!Array.isArray(affected) || affected.length === 0) return true;
    return affected.map((item) => String(item)).includes(cleanComparableValue(rank));
  }

  function surveyInDetails(details: Record<string, unknown>, surveyId: string) {
    const surveyFields = ['survey_id', 'current_survey', 'previous_survey', 'before_survey', 'after_survey'];
    if (surveyFields.some((field) => details[field] === surveyId)) return true;
    const gaps = details.gap_surveys;
    return Array.isArray(gaps) && gaps.map((item) => String(item)).includes(surveyId);
  }

  function issueMatchesRow(issue: DiagnosticIssue, row: CanonicalDisplayRow) {
    if (issue.tree_uid !== row.tree_uid || issue.survey_id !== row.survey_id) return false;
    if (issue.source_file && issue.source_row) {
      return issue.source_file === row.source_file && numericString(issue.source_row) === numericString(row.source_row);
    }
    const details = parsedDetails(issue);
    return rankMatches(details, row.stem_rank);
  }

  function invariantMatchesRow(finding: InvariantFinding, row: CanonicalDisplayRow) {
    if (finding.tree_uid !== row.tree_uid) return false;
    const details = parsedDetails(finding);
    if (!surveyInDetails(details, row.survey_id)) return false;
    if ('rank' in details && String(details.rank) !== cleanComparableValue(row.stem_rank)) return false;
    return rankMatches(details, row.stem_rank);
  }

  function rowMarkers(row: CanonicalDisplayRow): RowMarker[] {
    if (row.is_placeholder) return [];
    const issueMarkers = diagnosticIssues
      .filter((issue) => issue.severity !== 'info' && issueMatchesRow(issue, row))
      .map((issue) => ({
        code: issue.code,
        label: codeLabel(issue.code),
        title: issue.message,
        severity: issue.severity
      }));
    const invariantMarkers = invariantFindings.filter((finding) => invariantMatchesRow(finding, row)).map((finding) => ({
      code: finding.code,
      label: codeLabel(finding.code),
      title: finding.summary,
      severity: finding.severity
    }));
    const seen: Record<string, boolean> = {};
    return [...issueMarkers, ...invariantMarkers].filter((marker) => {
      const key = `${marker.label}:${marker.title}`;
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    });
  }

  function markerTitle(markers: RowMarker[]) {
    return markers.map((marker) => `${marker.label}: ${marker.title}`).join('\n');
  }

  function toggleObservation(row: CanonicalDisplayRow) {
    if (row.is_placeholder) return;
    const key = rowKey(row);
    expandedObservationKey = expandedObservationKey === key ? '' : key;
  }

  function evidenceForObservation(row: CanonicalDisplayRow) {
    if (row.is_placeholder) return [];
    const tag = cleanTag(row.public_tag || row.identity_tag || row.tree_number);
    const treeSurveyEvidence = allRelatedEvidence.filter((evidence) => {
      const evidenceTag = cleanTag(evidence.public_tag_raw || evidence.old_tag_raw);
      return evidence.plot === row.plot && evidence.survey_id === row.survey_id && evidenceTag === tag;
    });
    const rowSlot = cleanComparableValue(row.datasheet_slot || row.stem_rank);
    if (rowSlot) {
      const stemEvidence = treeSurveyEvidence.filter((evidence) => cleanComparableValue(evidence.datasheet_slot_raw) === rowSlot);
      if (stemEvidence.length) return stemEvidence;
    }
    if (treeSurveyEvidence.length) return treeSurveyEvidence;
    return allRelatedEvidence.filter((evidence) => evidence.plot === row.plot && evidence.survey_id === row.survey_id).slice(0, 12);
  }

  function rowsWithSurveyGaps(rows: CanonicalHistoryRow[]) {
    const displayRows: CanonicalDisplayRow[] = [];
    for (const uid of uniqueStrings(rows.map((row) => row.tree_uid))) {
      const uidRows = sortedCanonicalRows(rows.filter((row) => row.tree_uid === uid));
      if (!uidRows.length) continue;
      const surveyWindow = surveysForRows(uidRows);
      const rowsBySurvey = groupRowsBySurvey(uidRows);
      for (const survey of surveyWindow) {
        const surveyRows = rowsBySurvey[survey.survey_id] ?? [];
        if (surveyRows.length) {
          displayRows.push(...surveyRows);
        } else {
          displayRows.push(placeholderRow(uidRows, survey, ''));
        }
      }
    }
    return sortedCanonicalRows(displayRows);
  }

  function groupCanonicalRowsByStem(rows: CanonicalHistoryRow[]) {
    const groups: Record<string, CanonicalDisplayRow[]> = {};
    for (const uid of uniqueStrings(rows.map((row) => row.tree_uid))) {
      const uidRows = sortedCanonicalRows(rows.filter((row) => row.tree_uid === uid));
      if (!uidRows.length) continue;
      const ranks = uniqueStrings(uidRows.map((row) => row.stem_rank || 'unknown'));
      const surveyWindow = surveysForRows(uidRows);
      const rowsBySurveyRank = groupRowsBySurveyRank(uidRows);
      for (const rank of ranks) {
        groups[rank] ??= [];
        for (const survey of surveyWindow) {
          const key = `${survey.survey_id}:${rank}`;
          groups[rank].push(rowsBySurveyRank[key] ?? placeholderRow(uidRows, survey, rank));
        }
      }
    }
    return Object.entries(groups)
      .map(([rank, groupRows]) => ({
        rank,
        rows: sortedCanonicalRows(groupRows)
      }))
      .sort((a, b) => rankSortValue(a.rank) - rankSortValue(b.rank) || a.rank.localeCompare(b.rank));
  }

  function rankSortValue(rank: string) {
    const parsed = Number(rank);
    return Number.isFinite(parsed) ? parsed : 999;
  }

  function groupRowsBySurvey(rows: CanonicalHistoryRow[]) {
    const groups: Record<string, CanonicalHistoryRow[]> = {};
    for (const row of rows) {
      groups[row.survey_id] ??= [];
      groups[row.survey_id].push(row);
    }
    return groups;
  }

  function groupRowsBySurveyRank(rows: CanonicalHistoryRow[]) {
    const groups: Record<string, CanonicalHistoryRow> = {};
    for (const row of rows) {
      groups[`${row.survey_id}:${row.stem_rank || 'unknown'}`] = row;
    }
    return groups;
  }

  function surveysForRows(rows: CanonicalHistoryRow[]) {
    const rowSurveyIds = new Set(rows.map((row) => row.survey_id));
    const firstIndex = surveys.findIndex((survey) => rowSurveyIds.has(survey.survey_id));
    if (firstIndex < 0) return [];
    return surveys.slice(firstIndex);
  }

  function placeholderRow(rows: CanonicalHistoryRow[], survey: SurveyTimelineItem, stemRank: string): CanonicalDisplayRow {
    const reference = nearestPreviousRow(rows, survey) ?? rows[0];
    const suffix = stemRank || 'whole';
    return {
      ...reference,
      survey_id: survey.survey_id,
      date: survey.date,
      stem_rank: stemRank,
      datasheet_slot: '',
      dbh_mm: '',
      health_observed: '',
      alive_observed: '',
      standing_observed: '',
      field_status: 'not_reported',
      interpreted_status: 'not_reported',
      alive_interpreted: '',
      origin: 'display_gap',
      source_file: '__display_gap__',
      source_row: `${survey.survey_id}:${reference.tree_uid}:${suffix}`,
      notes: 'No canonical row for this survey.',
      correction_notes: '',
      is_placeholder: true,
      placeholder_kind: 'not_reported'
    };
  }

  function nearestPreviousRow(rows: CanonicalHistoryRow[], survey: SurveyTimelineItem) {
    const surveyValue = survey.date || survey.survey_id;
    return sortedCanonicalRows(rows)
      .filter((row) => (row.date || row.survey_id).localeCompare(surveyValue) <= 0)
      .at(-1);
  }

  function stemLabel(rank: string) {
    return rank === 'unknown' ? 'Stem unknown' : `Stem ${rank}`;
  }

  function buildCanonicalSections() {
    if (mode === 'trees') {
      if (!selectedTree) return [];
      return [{ tree: selectedTree, rows: dossier?.history ?? [], scopes: [] }];
    }
    if (!tagDossier) return [];
    return tagDossier.treeCases.map((tree) => ({
      tree,
      rows: tagDossier.history.filter((row) => row.tree_uid === tree.tree_uid),
      scopes: tagDossier.treeScopes.filter((scope) => scope.tree_uid === tree.tree_uid)
    }));
  }

  function availableScopeFilters() {
    if (mode === 'trees' || !tagDossier) return [];
    const scopes = [...new Set(tagDossier.treeScopes.map((scope) => scope.scope))];
    const ordered = scopes.sort((a, b) => scopeWeight(a) - scopeWeight(b));
    return [
      { value: 'all' as ScopeFilter, label: 'All', count: canonicalSections.length },
      ...ordered.map((scope) => ({
        value: scope as ScopeFilter,
        label: scopeLabel(scope),
        count: canonicalSections.filter((section) => section.scopes.some((item) => item.scope === scope)).length
      }))
    ];
  }

  function scopeWeight(scope: ScopeFilter) {
    return { all: -1, direct: 0, tag_change: 1, candidate_link: 2, same_tag_other_plot: 3 }[scope];
  }

  function scopeLabel(scope: ScopeFilter) {
    return {
      all: 'All related UUIDs',
      direct: 'Direct matches',
      tag_change: 'Tag changes',
      candidate_link: 'Candidate links',
      same_tag_other_plot: 'Same tag elsewhere'
    }[scope];
  }

  function scopeHelp(scope: ScopeFilter) {
    return {
      all: 'Show direct matches plus UUIDs related by tag changes, candidate links, or same bare tag elsewhere.',
      direct: 'Only UUIDs whose canonical plot/tag directly match this selection.',
      tag_change: 'UUIDs connected by a tag-change assertion.',
      candidate_link: 'UUIDs connected by a possible identity-link diagnostic.',
      same_tag_other_plot: 'UUIDs with the same bare tag number in a different plot.'
    }[scope];
  }

  function sectionTitle(section: CanonicalSection) {
    return `${section.tree.plot}/${section.tree.identity_tag}`;
  }

  function sectionSubtitle(section: CanonicalSection) {
    return section.tree.tree_uid;
  }

  function sectionScopeLabels(section: CanonicalSection) {
    return section.scopes.length ? section.scopes : [{ tree_uid: section.tree.tree_uid, scope: 'direct' as const, scope_label: 'Direct match', detail: '' }];
  }

  function evidenceTitle(row: CanonicalDisplayRow) {
    return `Evidence for ${row.survey_id} stem ${display(row.stem_rank)}`;
  }

  function evidenceCountLabel(count: number) {
    return count ? `${count} rows` : 'no exact rows';
  }

  function rowSortValue(row: CanonicalDisplayRow) {
    return `${row.date || row.survey_id}:${String(row.stem_rank || '').padStart(3, '0')}`;
  }

  function sortedCanonicalRows<T extends CanonicalHistoryRow | CanonicalDisplayRow>(rows: T[]) {
    return [...rows].sort((a, b) => rowSortValue(a).localeCompare(rowSortValue(b)));
  }

  function canonicalRowsForStem(group: CanonicalStemGroup) {
    return sortedCanonicalRows(group.rows);
  }

  function matrixSurveyRows(groups: CanonicalStemGroup[]) {
    return groups[0]?.rows ?? [];
  }

  function expandedMatrixItem(groups: CanonicalStemGroup[]): MatrixEvidenceItem | null {
    const row = groups.flatMap((group) => group.rows).find((candidate) => rowIsExpanded(candidate));
    return row ? { row, evidence: evidenceForObservation(row) } : null;
  }

  function canonicalTableColspan(compact = false) {
    return compact ? 4 : 7;
  }

  function noCanonicalMessage() {
    return 'No canonical observations are currently associated with this selection.';
  }

  function rowIsExpanded(row: CanonicalDisplayRow) {
    return expandedObservationKey === rowKey(row);
  }

  function stemGroupKey(group: CanonicalStemGroup) {
    return group.rank;
  }

  function renderEvidenceHealth(evidence: EvidenceObservation) {
    return display(evidence.health_raw || evidence.alive_raw);
  }

  function renderEvidenceTag(evidence: EvidenceObservation) {
    return `${evidence.plot}/${evidence.public_tag_raw}`;
  }

  function renderEvidenceSource(evidence: EvidenceObservation) {
    return `${evidence.source_path}:${evidence.source_row}`;
  }

  function renderRowTaxon(row: CanonicalDisplayRow) {
    return rowTaxon(row);
  }

  function canonicalTableRows(viewRows: CanonicalDisplayRow[]) {
    return viewRows.map((row) => {
      const expanded = rowIsExpanded(row);
      const markers = rowMarkers(row);
      return {
        row,
        key: rowKey(row),
        expanded,
        markers,
        evidence: expanded ? evidenceForObservation(row) : []
      };
    });
  }

  function groupTitle(group: CanonicalStemGroup) {
    return stemLabel(group.rank);
  }

  function groupSubtitle(group: CanonicalStemGroup) {
    return `${group.rows.length} observations`;
  }

  function showEvidenceEmptyText() {
    return 'No matching evidence rows found for this canonical row yet.';
  }

  function uniqueStrings(values: Array<string | undefined>) {
    return [...new Set(values.map((value) => String(value ?? '').trim()).filter(Boolean))].sort();
  }

  function uniqueEvidence(rows: EvidenceObservation[]) {
    const seen: Record<string, boolean> = {};
    return rows.filter((row) => {
      if (seen[row.evidence_id]) return false;
      seen[row.evidence_id] = true;
      return true;
    });
  }

  function evidenceIdentity(row: EvidenceObservation) {
    return JSON.stringify([
      row.survey_id,
      row.date,
      row.year,
      row.site,
      row.zone,
      row.plot,
      cleanTag(row.public_tag_raw),
      cleanTag(row.old_tag_raw),
      row.tree_code_raw,
      row.datasheet_slot_raw,
      row.genus_raw,
      row.species_raw,
      row.taxon_raw,
      row.dbh_mm_raw,
      row.health_raw,
      row.alive_raw,
      row.standing_raw,
      row.poison_ivy_raw,
      row.notes_raw,
      row.note_flags
    ]);
  }

  function originKey(row: EvidenceObservation) {
    return [row.source_kind, row.source_path, row.source_sheet].join('|');
  }

  function originLabel(row: EvidenceObservation, count: number) {
    const sheet = row.source_sheet ? ` [${row.source_sheet}]` : '';
    return `${row.source_kind}: ${row.source_path}${sheet} x${count}`;
  }

  function mergeEvidenceRows(rows: EvidenceObservation[]) {
    const groups: Record<string, { representative: EvidenceObservation; origins: Record<string, { row: EvidenceObservation; count: number }>; count: number }> = {};
    for (const row of rows) {
      const key = evidenceIdentity(row);
      const origin = originKey(row);
      groups[key] ??= { representative: row, origins: {}, count: 0 };
      groups[key].count += 1;
      groups[key].origins[origin] ??= { row, count: 0 };
      groups[key].origins[origin].count += 1;
    }
    return Object.entries(groups).map(([key, group]) => ({
      key,
      representative: group.representative,
      count: group.count,
      origins: Object.values(group.origins).map((origin) => originLabel(origin.row, origin.count))
    }));
  }

  function entityTitle() {
    if (mode === 'trees' && selectedTree) return `${selectedTree.plot}/${selectedTree.identity_tag}`;
    if (selectedTag) return selectedTag.label;
    return 'No selection';
  }

  function entitySubtitle() {
    if (mode === 'trees' && selectedTree) return selectedTree.tree_uid;
    if (selectedTag) return `${selectedTag.evidence_count} evidence rows across ${selectedTag.source_count} sources`;
    return '';
  }
</script>

<svelte:head>
  <title>Canonical Forest Census</title>
</svelte:head>

<div class="workbench">
  <aside class="entity-list">
    <div class="list-head">
      <h1>{mode === 'trees' ? 'Tree UUIDs' : mode === 'tag-plot' ? 'Tag x Plot' : 'Tags'}</h1>
      <p>{mode === 'trees' ? `${data.totalCases} matches` : `${data.totalTagCards} matches`}</p>
    </div>

    <nav class="mode-tabs" aria-label="Mission control mode">
      {#each modes as [key, label, Icon] (key)}
        <a class={{ active: mode === key }} href={resolve(modeHref(key))} title={label}>
          <Icon size={16} />
          <span>{label}</span>
        </a>
      {/each}
    </nav>

    <form class="filters" method="GET">
      <input type="hidden" name="mode" value={mode} />
      <label class="wide">
        <div class="filter-label">
          <span>Status</span>
          <strong>Needs review {data.statusCounts.needs_review}/{data.statusCounts.total}</strong>
        </div>
        <select name="status" value={data.filters.status} onchange={submitFilters}>
          <option value="">All statuses</option>
          <option value="needs_review">Needs review</option>
          <option value="watch">Watch/context</option>
          <option value="quiet">Quiet</option>
        </select>
      </label>
      <label class="wide">
        <div class="filter-label">
          <span>Review lane</span>
          <strong>Human call {data.laneCounts.needs_human_call}/{data.laneCounts.total}</strong>
        </div>
        <select name="lane" value={data.filters.lane} onchange={submitFilters}>
          <option value="">All lanes</option>
          <option value="needs_human_call">Needs human call</option>
          <option value="suggested_fix">Suggested fix candidate</option>
        </select>
      </label>
      <label>
        <span>Plot</span>
        <input name="plot" value={data.filters.plot} placeholder="M0" />
      </label>
      <label>
        <span>Zone</span>
        <input name="zone" value={data.filters.zone} placeholder="H" />
      </label>
      <label class="wide">
        <span>Find</span>
        <input name="q" value={data.filters.q} placeholder="tag, uuid, taxon, note" />
      </label>
      <button type="submit"><Search size={15} /> Search</button>
    </form>
    <a class="clear-filters" href={resolve(`/?mode=${mode}`)}>Clear filters</a>

    <div class="entries">
      {#if mode !== 'trees' && data.totalTagCards > data.listLimit}
        <p class="list-note">Showing first {data.listLimit}. Narrow the selector above.</p>
      {:else if mode === 'trees' && data.totalCases > data.listLimit}
        <p class="list-note">Showing first {data.listLimit}. Narrow the selector above.</p>
      {/if}

      {#if mode === 'trees'}
        {#each cases as item (item.tree_uid)}
          <a class={{ selected: item.tree_uid === data.selectedUid }} href={resolve(caseHref(item))}>
            <div class="entry-title">
              <strong>{item.plot}/{item.identity_tag}</strong>
              <span class={['status-pill', item.review_status]}>{item.review_status_label}</span>
            </div>
            <span>{item.primary_taxon_code || 'taxon?'} | {display(item.max_dbh_mm)} mm</span>
            {#if item.review_reasons}
              <small>{reviewReasonLabel(item.review_reasons)}</small>
            {/if}
            <code>{item.tree_uid}</code>
          </a>
        {:else}
          <p class="empty">No matching tree UUIDs.</p>
        {/each}
      {:else}
        {#each tagCards as item (item.key)}
          <a class={{ selected: item.key === data.selectedTagKey }} href={resolve(tagHref(item))}>
            <div class="entry-title">
              <strong>{item.label}</strong>
              <span class={['status-pill', item.review_status]}>{reviewStatusLabel(item.review_status)}</span>
            </div>
            <span>{item.zone || item.zones || 'all zones'} | {display(item.max_dbh_mm)} mm</span>
            <small>
              {item.evidence_count} evidence | {item.canonical_tree_count} uuid | {item.review_case_count} review | {item.source_count} sources
            </small>
          </a>
        {:else}
          <p class="empty">No matching tag evidence.</p>
        {/each}
      {/if}
    </div>
  </aside>

  <main class="mission">
    <header class="mission-head">
      <div>
        <p>{mode === 'trees' ? 'Tree UUID View' : selectedTag?.mode === 'tag-plot' ? 'Tag x Plot View' : 'Tag View'}</p>
        <h2>{entityTitle()}</h2>
        <code>{entitySubtitle()}</code>
      </div>
      <div class="head-actions">
        <a href={resolve(`/?mode=tag-plot${selectedTree ? `&plot=${selectedTree.plot}&q=${selectedTree.identity_tag}` : ''}`)}>
          <Search size={15} /> Similar/Complement
        </a>
      </div>
    </header>

    <section class="summary-strip">
      <div><span>Canonical Rows</span><strong>{canonicalRows.length}</strong></div>
      <div><span>Related Evidence</span><strong>{allRelatedEvidence.length}</strong></div>
      <div><span>First</span><strong>{display(selectedTree?.first_survey || selectedTag?.first_survey)}</strong></div>
      <div><span>Last</span><strong>{display(selectedTree?.last_survey || selectedTag?.last_survey)}</strong></div>
      <div><span>Taxon</span><strong>{display(selectedTree?.primary_taxon_code || selectedTag?.taxa)}</strong></div>
    </section>

    <section class="panel decision-flow-panel">
      <div class="panel-title">
        <div class="title-copy">
          <GitMerge size={17} />
          <h3>Raw -> Decisions -> Current</h3>
        </div>
      </div>
      <div class="decision-flow-grid">
        <div class="decision-stage">
          <span>Raw flags</span>
          <strong>{decisionPhaseSummary.rawFlags}</strong>
          <small>{decisionPhaseSummary.rawIssueCount} issues / {decisionPhaseSummary.rawInvariantCount} invariants</small>
          <div class="code-chip-row">
            {#each diagnosticCodeCounts(rawDiagnosticIssues, rawInvariantFindings) as item (item.code)}
              <span class="code-chip" title={item.code}>{codeLabel(item.code)} x{item.count}</span>
            {/each}
          </div>
        </div>
        <div class="decision-stage accepted">
          <span>Accepted decisions</span>
          <strong>{decisionPhaseSummary.configuredDecisionCount}</strong>
          <small>{configuredDecisions.length ? 'configured calls matched to this selection' : 'no configured decisions matched'}</small>
          {#if configuredDecisions.length}
            <div class="decision-chip-row">
              {#each configuredDecisions.slice(0, 10) as decision (decision.decision_id)}
                <span class="decision-chip" title={decisionTitle(decision)}>
                  {decisionLabel(decision)}
                  <small>{decisionSelectorSummary(decision)}</small>
                </span>
              {/each}
            </div>
          {/if}
        </div>
        <div class="decision-stage">
          <span>Current flags</span>
          <strong>{decisionPhaseSummary.currentFlags}</strong>
          <small>{decisionPhaseSummary.currentIssueCount} issues / {decisionPhaseSummary.currentInvariantCount} invariants</small>
          <div class="code-chip-row">
            {#each diagnosticCodeCounts(diagnosticIssues, invariantFindings) as item (item.code)}
              <span class="code-chip" title={item.code}>{codeLabel(item.code)} x{item.count}</span>
            {/each}
          </div>
        </div>
      </div>
    </section>

    <section class="panel worklist-panel">
      <div class="panel-title">
        <div class="title-copy">
          <GitMerge size={17} />
          <h3>Review Lanes</h3>
        </div>
      </div>
      <div class="worklist-grid">
        <div class="worklist-stage human">
          <div class="worklist-heading">
            <span>Needs Human Call</span>
            <strong>{humanWork.length}</strong>
          </div>
          <small>UUID-level calls, source-sheet checks, or tag/stem ambiguity before a fix should exist.</small>
          {#if humanWork.length}
            <div class="worklist-chip-row">
              {#each humanWork.slice(0, 12) as item (item.item_id)}
                <span class="worklist-chip human" title={workItemTitle(item)}>
                  {humanLabel(item)}
                  {#if candidateCountForItem(item)}
                    <small>{candidateCountForItem(item)} candidate</small>
                  {/if}
                </span>
              {/each}
            </div>
          {:else}
            <p>No human-call worklist item matched this selection.</p>
          {/if}
        </div>
        <div class="worklist-stage suggested">
          <div class="worklist-heading">
            <span>Suggested Fix Candidates</span>
            <strong>{suggestedWork.length}</strong>
          </div>
          <small>Generated proposals only; nothing here changes canonical output until accepted into the decision layer.</small>
          {#if suggestedWork.length}
            <div class="worklist-chip-row">
              {#each suggestedWork.slice(0, 12) as item (item.item_id)}
                {@const ids = candidateIdsForItem(item)}
                {@const candidate = ids.length ? candidateById.get(ids[0]) : undefined}
                <span class="worklist-chip suggested" title={candidate ? candidateTitle(candidate) : workItemTitle(item)}>
                  {candidate ? candidateLabel(candidate) : humanLabel(item)}
                  <small>{item.decision_scope || item.status}</small>
                </span>
              {/each}
            </div>
          {:else}
            <p>No suggested fix candidate matched this selection.</p>
          {/if}
        </div>
      </div>
    </section>

    <section class="panel canonical-panel">
      <div class="panel-title">
        <div class="title-copy">
          <ListTree size={17} />
          <h3>Current Canonical Dataset Guess</h3>
        </div>
        <div class="panel-controls">
          {#if canonicalView === 'stems'}
            <div class="segmented compact" aria-label="Stem table layout">
              <button class={{ active: stemLayout === 'stacked' }} type="button" onclick={() => (stemLayout = 'stacked')}>
                Stacked
              </button>
              <button class={{ active: stemLayout === 'columns' }} type="button" onclick={() => (stemLayout = 'columns')}>
                Columns
              </button>
            </div>
          {/if}
          <div class="segmented" aria-label="Canonical observation view">
            <button class={{ active: canonicalView === 'together' }} type="button" onclick={() => (canonicalView = 'together')}>
              Together
            </button>
            <button class={{ active: canonicalView === 'stems' }} type="button" onclick={() => (canonicalView = 'stems')}>
              Per stem
            </button>
          </div>
        </div>
      </div>
      {#snippet canonicalRowsTable(viewRows: CanonicalDisplayRow[], compact = false)}
        <div class="table-wrap canonical-table-wrap">
          <table class={['canonical-table', compact && 'compact']}>
            <thead>
              <tr>
                <th>Survey</th>
                {#if !compact}
                  <th>Plot/Tag</th>
                  <th>Stem</th>
                {/if}
                <th>DBH</th>
                <th>Health</th>
                <th>Status</th>
                {#if !compact}
                  <th>Taxon</th>
                {/if}
              </tr>
            </thead>
            <tbody>
              {#each canonicalTableRows(viewRows) as item (item.key)}
                <tr class={{ expanded: item.expanded, placeholder: item.row.is_placeholder, flagged: item.markers.length > 0 }} title={markerTitle(item.markers)}>
                  <td>
                    <button class="row-link" type="button" disabled={item.row.is_placeholder} onclick={() => toggleObservation(item.row)}>
                      {item.row.survey_id}
                    </button>
                  </td>
                  {#if !compact}
                    <td><strong>{item.row.plot}/{item.row.public_tag}</strong></td>
                    <td>{display(item.row.stem_rank)}</td>
                  {/if}
                  <td>{display(item.row.dbh_mm)} mm</td>
                  <td>{display(item.row.health_observed)}</td>
                  <td>
                    <span>{item.row.interpreted_status}</span>
                    {#if item.markers.length}
                      <span class="row-marker-list">
                        {#each item.markers.slice(0, 3) as marker (`${marker.code}:${marker.title}`)}
                          <span class={['row-marker', marker.severity]} title={marker.title}>{marker.label}</span>
                        {/each}
                      </span>
                    {/if}
                  </td>
                  {#if !compact}
                    <td>{renderRowTaxon(item.row)}</td>
                  {/if}
                </tr>
                {#if item.expanded}
                  <tr class="evidence-detail">
                    <td colspan={canonicalTableColspan(compact)}>
                      <div class="evidence-popout">
                        <div class="popout-title">
                          <GitMerge size={16} />
                          <strong>{evidenceTitle(item.row)}</strong>
                          <span>{evidenceCountLabel(item.evidence.length)}</span>
                        </div>
                        {#each item.evidence as evidence (evidence.evidence_id)}
                          <div class="evidence-row">
                            <span>{display(evidence.survey_id || evidence.year)}</span>
                            <strong>{renderEvidenceTag(evidence)}</strong>
                            <span>{display(evidence.dbh_mm_raw)} mm</span>
                            <span>health {renderEvidenceHealth(evidence)}</span>
                            <span>{evidence.source_kind}</span>
                            <code>{renderEvidenceSource(evidence)}</code>
                            <p>{display(evidence.notes_raw)}</p>
                          </div>
                        {:else}
                          <p class="empty pad">{showEvidenceEmptyText()}</p>
                        {/each}
                      </div>
                    </td>
                  </tr>
                {/if}
              {:else}
                <tr><td colspan={canonicalTableColspan(compact)}>{noCanonicalMessage()}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/snippet}

      {#snippet stemMatrix(groups: CanonicalStemGroup[])}
        {#if groups.length}
          {@const surveyRows = matrixSurveyRows(groups)}
          {@const expandedItem = expandedMatrixItem(groups)}
          <div class="stem-matrix-wrap">
            <div class="stem-matrix" style:--stem-count={groups.length}>
              <div class="matrix-axis">
                <div class="matrix-head">Survey</div>
                {#each surveyRows as row (rowKey(row))}
                  <div class="matrix-survey">{row.survey_id}</div>
                {/each}
              </div>
              {#each groups as group (stemGroupKey(group))}
                <section class="matrix-stem">
                  <div class="matrix-head">
                    <strong>{groupTitle(group)}</strong>
                    <span>{groupSubtitle(group)}</span>
                  </div>
                  {#each canonicalRowsForStem(group) as row (rowKey(row))}
                    {@const markers = rowMarkers(row)}
                    <button
                      class={['matrix-cell', rowIsExpanded(row) && 'expanded', row.is_placeholder && 'placeholder', markers.length && 'flagged']}
                      type="button"
                      disabled={row.is_placeholder}
                      title={markerTitle(markers)}
                      onclick={() => toggleObservation(row)}
                    >
                      <span class="matrix-value dbh">{compactValue(row.dbh_mm)}</span>
                      <span class="matrix-sep">/</span>
                      <span class="matrix-value health">{compactValue(row.health_observed)}</span>
                      <span class="matrix-sep">/</span>
                      <span class="matrix-value state">{aliveValue(row)}</span>
                      <span class="matrix-sep">/</span>
                      <span class="matrix-value state">{standingValue(row)}</span>
                      <span class={['note-icon', matrixNotes(row).length === 0 && 'muted']} title={matrixNoteTitle(row)} aria-label={matrixNoteTitle(row)}>
                        <Info size={13} />
                      </span>
                    </button>
                  {/each}
                </section>
              {/each}
            </div>
            {#if expandedItem}
              <div class="matrix-popout evidence-popout">
                <div class="popout-title">
                  <GitMerge size={16} />
                  <strong>{evidenceTitle(expandedItem.row)}</strong>
                  <span>{evidenceCountLabel(expandedItem.evidence.length)}</span>
                </div>
                {#each expandedItem.evidence as evidence (evidence.evidence_id)}
                  <div class="evidence-row">
                    <span>{display(evidence.survey_id || evidence.year)}</span>
                    <strong>{renderEvidenceTag(evidence)}</strong>
                    <span>{display(evidence.dbh_mm_raw)} mm</span>
                    <span>health {renderEvidenceHealth(evidence)}</span>
                    <span>{evidence.source_kind}</span>
                    <code>{renderEvidenceSource(evidence)}</code>
                    <p>{display(evidence.notes_raw)}</p>
                  </div>
                {:else}
                  <p class="empty pad">{showEvidenceEmptyText()}</p>
                {/each}
              </div>
            {/if}
          </div>
        {:else}
          <p class="empty pad">{noCanonicalMessage()}</p>
        {/if}
      {/snippet}

      {#if mode !== 'trees' && scopeFilters.length}
        <div class="scope-tabs" aria-label="UUID scope filter">
          {#each scopeFilters as filter (filter.value)}
            <button
              class={{ active: effectiveScopeFilter === filter.value }}
              type="button"
              title={scopeHelp(filter.value)}
              onclick={() => (scopeFilter = filter.value)}
            >
              <span>{filter.label}</span>
              <strong>{filter.count}</strong>
            </button>
          {/each}
        </div>
      {/if}

      <div class="observation-list">
        {#each visibleCanonicalSections as section (section.tree.tree_uid)}
          <section class={{ 'uuid-section': mode !== 'trees' }}>
            {#if mode !== 'trees'}
              <div class="uuid-section-head">
                <div>
                  <h4>{sectionTitle(section)}</h4>
                  <code>{sectionSubtitle(section)}</code>
                  {#if reviewCodesForTree(section.tree).length}
                    <div class="review-chip-row">
                      {#each reviewCodesForTree(section.tree) as code (code)}
                        <span class="review-chip" title={code}>{codeLabel(code)}</span>
                      {/each}
                    </div>
                  {/if}
                </div>
                <div class="scope-chip-row">
                  {#each sectionScopeLabels(section) as scope (`${scope.scope}:${scope.detail}`)}
                    <span class={['scope-chip', scope.scope]} title={scope.detail}>{scopeLabel(scope.scope)}</span>
                  {/each}
                </div>
              </div>
            {/if}

            {#if canonicalView === 'together'}
              {@render canonicalRowsTable(rowsWithSurveyGaps(section.rows))}
            {:else}
              {@const stemGroups = groupCanonicalRowsByStem(section.rows)}
              {#if stemLayout === 'columns'}
                {@render stemMatrix(stemGroups)}
              {:else}
                <div class="stem-stack">
                  {#each stemGroups as group (stemGroupKey(group))}
                    <section class="stem-section">
                      <div class="stem-title">
                        <h4>{groupTitle(group)}</h4>
                        <span>{groupSubtitle(group)}</span>
                      </div>
                      {@render canonicalRowsTable(canonicalRowsForStem(group))}
                    </section>
                  {:else}
                    <p class="empty pad">{noCanonicalMessage()}</p>
                  {/each}
                </div>
              {/if}
            {/if}
          </section>
        {:else}
          <p class="empty pad">{noCanonicalMessage()}</p>
        {/each}
      </div>
    </section>

    <section class="panel">
      <details open>
        <summary>
          <Layers3 size={17} />
          <span>All Related Evidence</span>
          <strong>{mergedRelatedEvidence.length} merged / {allRelatedEvidence.length} raw</strong>
        </summary>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Count</th>
                <th>Survey</th>
                <th>Plot/Tag</th>
                <th>Slot</th>
                <th>Taxon</th>
                <th>DBH</th>
                <th>Health</th>
                <th>Origins</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {#each mergedRelatedEvidence as merged (merged.key)}
                {@const row = merged.representative}
                <tr>
                  <td>{merged.count}</td>
                  <td>{display(row.survey_id || row.year)}</td>
                  <td>{row.plot}/{row.public_tag_raw}</td>
                  <td>{display(row.datasheet_slot_raw)}</td>
                  <td>{display(rowTaxon(row))}</td>
                  <td>{display(row.dbh_mm_raw)}</td>
                  <td>{display(row.health_raw || row.alive_raw)}</td>
                  <td>
                    <div class="origin-list">
                      {#each merged.origins as origin (origin)}
                        <span>{origin}</span>
                      {/each}
                    </div>
                  </td>
                  <td>{display(row.notes_raw)}</td>
                </tr>
              {:else}
                <tr><td colspan="9">No related evidence loaded for this selection.</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  </main>
</div>

<style>
  .workbench {
    display: grid;
    grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
    min-height: 100vh;
    background: #f3f5f1;
    color: #172018;
  }

  .mode-tabs a,
  .head-actions a,
  .filters button,
  .panel-title,
  .title-copy,
  summary,
  .popout-title {
    display: flex;
    align-items: center;
  }

  .mode-tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 7px;
  }

  .mode-tabs a {
    gap: 6px;
    min-height: 38px;
    justify-content: center;
    border: 1px solid #d9ded4;
    border-radius: 6px;
    background: #fff;
    color: #172018;
    text-align: center;
    text-decoration: none;
    font-size: 12px;
    font-weight: 800;
  }

  .mode-tabs a.active {
    border-color: #2c6b4f;
    background: #e7f1eb;
  }

  .entity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: 100vh;
    overflow: hidden;
    border-right: 1px solid #d9ded4;
    background: #fbfcf8;
    padding: 16px;
  }

  h1,
  h2,
  h3,
  p {
    margin: 0;
  }

  h1 {
    font-size: 18px;
  }

  h2 {
    font-size: 30px;
    line-height: 1.05;
  }

  h3 {
    font-size: 15px;
  }

  code {
    overflow-wrap: anywhere;
    font-size: 11px;
  }

  .list-head p,
  .entries span,
  .entries small,
  .summary-strip span,
  .mission-head p,
  .evidence-row span,
  .empty,
  .list-note {
    color: #687363;
    font-size: 12px;
  }

  .filters {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .filters .wide,
  .filters button {
    grid-column: 1 / -1;
  }

  label {
    display: grid;
    gap: 4px;
    min-width: 0;
  }

  label span,
  .filter-label span {
    color: #596553;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .filter-label {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    min-width: 0;
  }

  .filter-label strong {
    flex: 0 0 auto;
    border: 1px solid #c9824d;
    border-radius: 999px;
    background: #fff0e4;
    color: #7b3d12;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  input,
  select {
    width: 100%;
    min-width: 0;
    border: 1px solid #cfd8ca;
    border-radius: 6px;
    background: #fff;
    color: #172018;
    padding: 8px 9px;
  }

  button,
  .head-actions a {
    border: 1px solid #cfd8ca;
    border-radius: 6px;
    background: #fff;
    color: #172018;
    padding: 8px 10px;
  }

  .filters button,
  .head-actions a {
    gap: 6px;
    justify-content: center;
    text-decoration: none;
    white-space: nowrap;
  }

  .clear-filters {
    display: flex;
    justify-content: center;
    border: 1px solid #d9ded4;
    border-radius: 6px;
    background: #fff;
    color: #334435;
    padding: 8px 10px;
    text-decoration: none;
    font-size: 12px;
    font-weight: 800;
  }

  .entries {
    display: grid;
    gap: 7px;
    overflow: auto;
    padding-right: 2px;
  }

  .list-note,
  .entries a {
    border: 1px solid #e0e5dc;
    border-radius: 6px;
    background: #fff;
    padding: 10px;
  }

  .entries a {
    display: grid;
    gap: 4px;
    color: inherit;
    text-decoration: none;
  }

  .entry-title {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    min-width: 0;
  }

  .entry-title strong {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .status-pill {
    flex: 0 0 auto;
    border: 1px solid #d8ded2;
    border-radius: 999px;
    background: #f4f6f0;
    color: #52604d;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  .status-pill.needs_review {
    border-color: #c9824d;
    background: #fff0e4;
    color: #7b3d12;
  }

  .status-pill.watch {
    border-color: #b9c3dc;
    background: #edf3ff;
    color: #344d82;
  }

  .status-pill.quiet {
    border-color: #cdd8cd;
    background: #eef6ee;
    color: #3f6f3f;
  }

  .entries a.selected {
    border-color: #2c6b4f;
    background: #e7f1eb;
  }

  .mission {
    display: grid;
    gap: 16px;
    align-content: start;
    height: 100vh;
    overflow: auto;
    padding: 22px;
  }

  .mission-head {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: start;
  }

  .head-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: end;
  }

  .summary-strip {
    display: grid;
    grid-template-columns: repeat(5, minmax(110px, 1fr));
    gap: 8px;
  }

  .summary-strip div,
  .panel {
    border: 1px solid #d9ded4;
    border-radius: 8px;
    background: #fff;
  }

  .summary-strip div {
    display: grid;
    gap: 3px;
    padding: 10px;
  }

  .summary-strip strong {
    overflow-wrap: anywhere;
    font-size: 15px;
  }

  .decision-flow-panel {
    overflow: visible;
  }

  .decision-flow-grid {
    display: grid;
    grid-template-columns: 1fr 1.4fr 1fr;
    gap: 10px;
    padding: 12px;
  }

  .decision-stage {
    display: grid;
    gap: 5px;
    align-content: start;
    min-width: 0;
    border: 1px solid #e0e5dc;
    border-radius: 6px;
    background: #fbfcf8;
    padding: 9px;
  }

  .decision-stage.accepted {
    border-color: #b9d0c3;
    background: #f3f8f1;
  }

  .decision-stage > span {
    color: #596553;
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
  }

  .decision-stage > strong {
    font-size: 19px;
    line-height: 1;
  }

  .decision-stage > small {
    color: #687363;
    font-size: 11px;
  }

  .decision-chip-row,
  .code-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    min-width: 0;
  }

  .decision-chip,
  .code-chip {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    max-width: 100%;
    border: 1px solid #d8ded2;
    border-radius: 999px;
    background: #fff;
    color: #334435;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .decision-chip {
    gap: 5px;
    border-color: #b9d0c3;
    background: #fff;
    color: #184a34;
  }

  .decision-chip small {
    overflow: hidden;
    max-width: 180px;
    color: #52604d;
    font-size: 10px;
    font-weight: 700;
    text-overflow: ellipsis;
    text-transform: none;
  }

  .worklist-panel {
    overflow: visible;
  }

  .worklist-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    padding: 12px;
  }

  .worklist-stage {
    display: grid;
    gap: 7px;
    align-content: start;
    min-width: 0;
    border: 1px solid #e0e5dc;
    border-radius: 6px;
    background: #fbfcf8;
    padding: 9px;
  }

  .worklist-stage.human {
    border-color: #e0c4b3;
    background: #fff8f2;
  }

  .worklist-stage.suggested {
    border-color: #b9d0c3;
    background: #f3f8f1;
  }

  .worklist-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
  }

  .worklist-heading span {
    color: #596553;
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
  }

  .worklist-heading strong {
    font-size: 19px;
    line-height: 1;
  }

  .worklist-stage small,
  .worklist-stage p {
    margin: 0;
    color: #687363;
    font-size: 11px;
  }

  .worklist-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    min-width: 0;
  }

  .worklist-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    width: fit-content;
    max-width: 100%;
    border: 1px solid #d8ded2;
    border-radius: 999px;
    background: #fff;
    padding: 2px 7px;
    color: #334435;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .worklist-chip.human {
    border-color: #e0c4b3;
    color: #65351f;
  }

  .worklist-chip.suggested {
    border-color: #b9d0c3;
    color: #184a34;
  }

  .worklist-chip small {
    overflow: hidden;
    max-width: 120px;
    color: #52604d;
    font-size: 10px;
    font-weight: 700;
    text-overflow: ellipsis;
    text-transform: none;
  }

  .panel {
    min-width: 0;
    overflow: hidden;
  }

  .canonical-panel {
    display: flex;
    flex-direction: column;
    max-height: min(74vh, 860px);
    min-height: 360px;
  }

  .canonical-panel .observation-list {
    flex: 1 1 auto;
    min-height: 0;
    overflow: auto;
  }

  .canonical-panel .canonical-table-wrap {
    max-height: none;
    overflow: visible;
  }

  .panel-title,
  .title-copy,
  summary {
    gap: 7px;
    border-bottom: 1px solid #edf0ea;
    padding: 10px 12px;
  }

  .panel-title {
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .title-copy {
    border-bottom: 0;
    padding: 0;
  }

  .panel-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: end;
  }

  .segmented {
    display: flex;
    flex: 0 0 auto;
    overflow: hidden;
    border: 1px solid #cfd8ca;
    border-radius: 6px;
    background: #fff;
  }

  .segmented button {
    min-width: 82px;
    border: 0;
    border-radius: 0;
    background: transparent;
    padding: 6px 9px;
    color: #596553;
    font-size: 12px;
    font-weight: 850;
  }

  .segmented button + button {
    border-left: 1px solid #cfd8ca;
  }

  .segmented button.active {
    background: #e7f1eb;
    color: #184a34;
  }

  .segmented.compact button {
    min-width: 74px;
  }

  summary {
    justify-content: space-between;
    cursor: pointer;
    font-weight: 800;
    list-style: none;
  }

  summary::-webkit-details-marker {
    display: none;
  }

  .scope-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    border-bottom: 1px solid #edf0ea;
    padding: 10px 12px;
  }

  .scope-tabs button {
    display: flex;
    gap: 6px;
    align-items: center;
    border: 1px solid #cfd8ca;
    border-radius: 999px;
    background: #fff;
    padding: 6px 9px;
    color: #52604d;
    font-size: 12px;
    font-weight: 850;
  }

  .scope-tabs button.active {
    border-color: #2c6b4f;
    background: #e7f1eb;
    color: #184a34;
  }

  .scope-tabs strong {
    font-size: 11px;
  }

  .observation-list {
    display: grid;
  }

  .uuid-section {
    min-width: 0;
    border-top: 1px solid #d9ded4;
  }

  .uuid-section:first-child {
    border-top: 0;
  }

  .uuid-section-head {
    display: flex;
    gap: 12px;
    align-items: start;
    justify-content: space-between;
    border-bottom: 1px solid #edf0ea;
    background: #fbfcf8;
    padding: 12px;
  }

  .uuid-section-head h4 {
    margin: 0 0 3px;
    font-size: 15px;
  }

  .scope-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: end;
  }

  .review-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 6px;
  }

  .review-chip,
  .row-marker {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    border: 1px solid #c9824d;
    border-radius: 999px;
    background: #fff0e4;
    color: #7b3d12;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .row-marker.info {
    border-color: #b9c3dc;
    background: #edf3ff;
    color: #344d82;
  }

  .scope-chip {
    border: 1px solid #d8ded2;
    border-radius: 999px;
    background: #f4f6f0;
    color: #52604d;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .scope-chip.direct {
    border-color: #b9d0c3;
    background: #e7f1eb;
    color: #184a34;
  }

  .scope-chip.tag_change {
    border-color: #b9c3dc;
    background: #edf3ff;
    color: #344d82;
  }

  .scope-chip.candidate_link {
    border-color: #c9824d;
    background: #fff0e4;
    color: #7b3d12;
  }

  .scope-chip.same_tag_other_plot {
    border-color: #c8bdd8;
    background: #f4f0fb;
    color: #514266;
  }

  .canonical-table-wrap {
    max-height: 620px;
  }

  .canonical-table tr.expanded td {
    background: #f3f8f1;
  }

  .canonical-table tr.placeholder td {
    background: #fbfbf7;
    color: #7a8176;
    font-style: italic;
  }

  .canonical-table tr.flagged td {
    background: #fff9ef;
  }

  .canonical-table tr.flagged.expanded td {
    background: #fff4df;
  }

  .row-marker-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;
  }

  .row-link {
    border: 0;
    border-radius: 4px;
    background: transparent;
    color: #184a34;
    padding: 0;
    text-align: left;
    font-weight: 850;
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  .row-link:disabled {
    color: #7a8176;
    cursor: default;
    opacity: 1;
    text-decoration: none;
  }

  .evidence-detail td {
    padding: 0;
  }

  .evidence-detail .evidence-popout {
    border-bottom: 1px solid #d9ded4;
  }

  .stem-stack {
    display: grid;
    gap: 14px;
    padding: 12px;
  }

  .stem-section {
    min-width: 0;
    border-top: 1px solid #d9ded4;
  }

  .stem-section:first-child {
    border-top: 0;
  }

  .stem-title {
    display: flex;
    gap: 8px;
    align-items: baseline;
    justify-content: space-between;
    padding: 10px 0 8px;
  }

  .stem-title h4 {
    margin: 0;
    font-size: 14px;
  }

  .stem-title span {
    color: #687363;
    font-size: 12px;
  }

  .stem-matrix-wrap {
    display: grid;
    gap: 8px;
    overflow: auto;
    padding: 8px;
  }

  .stem-matrix {
    display: grid;
    grid-template-columns: 96px repeat(var(--stem-count), 210px);
    align-items: start;
    width: max-content;
    max-width: 100%;
    border: 1px solid #d9ded4;
    border-radius: 6px;
    background: #fff;
  }

  .matrix-axis,
  .matrix-stem {
    display: grid;
    grid-auto-rows: 32px;
    min-width: 0;
  }

  .matrix-stem {
    border-left: 1px solid #d9ded4;
  }

  .matrix-head,
  .matrix-survey,
  .matrix-cell {
    min-width: 0;
    min-height: 32px;
    border-bottom: 1px solid #edf0ea;
  }

  .matrix-head {
    display: flex;
    gap: 6px;
    align-items: center;
    justify-content: space-between;
    background: #fbfcf8;
    color: #596553;
    padding: 0 7px;
    font-size: 10px;
    font-weight: 900;
    text-transform: uppercase;
  }

  .matrix-head strong {
    color: #172018;
    font-size: 12px;
    text-transform: none;
  }

  .matrix-head span {
    overflow: hidden;
    color: #687363;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-transform: none;
  }

  .matrix-survey {
    display: flex;
    align-items: center;
    padding: 0 7px;
    color: #52604d;
    font-size: 11px;
    font-weight: 850;
  }

  .matrix-cell {
    display: grid;
    grid-template-columns: 44px 6px 30px 6px 16px 6px 16px 16px;
    gap: 3px;
    align-items: center;
    width: 100%;
    border-width: 0 0 1px;
    border-radius: 0;
    background: #fff;
    padding: 0 6px;
    color: #172018;
    text-align: left;
    font-size: 11px;
  }

  .matrix-cell:hover,
  .matrix-cell.expanded {
    background: #f3f8f1;
  }

  .matrix-cell.flagged {
    background: #fff9ef;
    box-shadow: inset 3px 0 0 #c9824d;
  }

  .matrix-cell.flagged.expanded {
    background: #fff4df;
  }

  .matrix-cell.placeholder {
    background: #fbfbf7;
    color: #7a8176;
    font-style: italic;
  }

  .matrix-cell:disabled {
    cursor: default;
  }

  .matrix-cell span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .matrix-value {
    font-variant-numeric: tabular-nums;
  }

  .matrix-value.dbh,
  .matrix-value.health {
    text-align: right;
  }

  .matrix-value.state,
  .matrix-sep {
    color: #52604d;
    text-align: center;
  }

  .matrix-sep {
    opacity: 0.65;
  }

  .note-icon {
    display: inline-flex;
    justify-content: end;
    color: #344d82;
  }

  .note-icon.muted {
    color: #b4bcb0;
  }

  .matrix-popout {
    border: 1px solid #d9ded4;
    border-radius: 6px;
    padding: 8px;
  }

  .evidence-popout {
    display: grid;
    gap: 8px;
    border-bottom: 1px solid #d9ded4;
    background: #f8faf5;
    padding: 10px 12px 12px 28px;
  }

  .popout-title {
    gap: 7px;
  }

  .popout-title span {
    margin-left: auto;
    color: #687363;
    font-size: 12px;
  }

  .evidence-row {
    display: grid;
    grid-template-columns: 120px 100px 80px 90px 120px minmax(180px, 1fr);
    gap: 8px;
    align-items: start;
    border: 1px solid #e0e5dc;
    border-radius: 6px;
    background: #fff;
    padding: 8px;
  }

  .evidence-row p {
    grid-column: 1 / -1;
    color: #4d5b4c;
    font-size: 12px;
  }

  .pad {
    padding: 10px 12px;
  }

  .table-wrap {
    overflow: auto;
    max-height: 560px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  th,
  td {
    border-bottom: 1px solid #edf0ea;
    max-width: 420px;
    padding: 8px 9px;
    text-align: left;
    vertical-align: top;
  }

  th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f8faf5;
    color: #596553;
    font-size: 11px;
    text-transform: uppercase;
  }

  .origin-list {
    display: grid;
    gap: 4px;
  }

  .origin-list span {
    overflow-wrap: anywhere;
  }

  @media (max-width: 1180px) {
    .workbench {
      grid-template-columns: 1fr;
    }

    .entity-list,
    .mission {
      height: auto;
      min-height: 0;
    }

    .mission-head,
    .summary-strip,
    .decision-flow-grid,
    .worklist-grid,
    .evidence-row {
      grid-template-columns: 1fr;
    }
  }
</style>
