import { mkdir, readFile, readdir, stat, appendFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { parse } from 'csv-parse/sync';
import type { ReviewDecision, ReviewPage, ReviewRow } from '$lib/types';

const repoRoot = path.resolve('..');
const outputRoot = path.join(repoRoot, 'output', 'llm_transcription');
const reviewSelectionPath = path.join(outputRoot, 'review_selection.json');

export function getRepoRoot() {
  return repoRoot;
}

export function isAllowedImagePath(candidate: string) {
  const resolved = path.resolve(repoRoot, candidate);
  return (
    resolved.startsWith(path.join(repoRoot, 'output') + path.sep) ||
    resolved.startsWith(path.join(repoRoot, 'assets') + path.sep)
  );
}

export async function latestRunDir() {
  const configured = process.env.REVIEW_RUN_DIR;
  if (configured) {
    return path.resolve(repoRoot, configured);
  }

  const entries = await readdir(outputRoot, { withFileTypes: true });
  const candidates = await Promise.all(
    entries
      .filter((entry) => entry.isDirectory())
      .map(async (entry) => {
        const dir = path.join(outputRoot, entry.name);
        const reviewCsv = path.join(dir, 'review_rows.csv');
        try {
          const info = await stat(reviewCsv);
          return { dir, mtime: info.mtimeMs };
        } catch {
          return null;
        }
      })
  );
  const available = candidates
    .filter((item): item is { dir: string; mtime: number } => item !== null)
    .sort((a, b) => b.mtime - a.mtime);

  if (!available[0]) {
    throw new Error(`No review_rows.csv files found under ${outputRoot}`);
  }
  return available[0].dir;
}

export async function loadReviewRows() {
  if (process.env.REVIEW_RUN_DIR) {
    return await loadSingleReviewRows(await latestRunDir());
  }
  const selection = await loadReviewSelection();
  if (selection) return await loadCombinedReviewRows(selection);

  const runDir = await latestRunDir();
  return await loadSingleReviewRows(runDir);
}

async function loadSingleReviewRows(runDir: string) {
  const csvPath = await preferredRowsCsv(runDir);
  const text = await readFile(csvPath, 'utf-8');
  const records = parse(text, {
    columns: true,
    skip_empty_lines: true
  }) as Record<string, string>[];

  const layout = await loadLayoutManifest(runDir);
  const metadata = await loadPageMetadata(runDir);
  const rowLayouts = alignRowLayouts(records, layout);
  const rows = records.map((record, index) => normalizeRow(record, index, runDir, layout, rowLayouts));
  const pages = mergePages(layout, metadata, runDir);
  const decisionHistory = await loadDecisionHistory(runDir);
  const decisions = latestDecisions(decisionHistory);
  return { runDir, rows, pages, decisions, decisionHistory };
}

function normalizePage(page: LayoutPage, metadata: PageMetadata | undefined, runDir: string): ReviewPage {
  return {
    source_page: page.source_page,
    source_run_dir: runDir,
    source_image:
      metadata?.source_image ||
      page.image_path ||
      path.join(runDir, 'pages', `page_${page.source_page.toString().padStart(3, '0')}.png`),
    page_image_width: page.page_image_width,
    page_image_height: page.page_image_height,
    source_page_title: metadata?.source_page_title ?? '',
    plot: metadata?.plot ?? '',
    field_date: metadata?.field_date ?? '',
    crew: metadata?.crew ?? '',
    problems_and_info: metadata?.problems_and_info ?? '',
    difficulty: metadata?.difficulty ?? '',
    page_flags: metadata?.page_flags ?? '',
    observer: metadata?.observer ?? '',
    recorder: metadata?.recorder ?? '',
    bonus_person: metadata?.bonus_person ?? '',
    recheck_answers: JSON.parse(metadata?.recheck_answers || '[]'),
    field_note_feedback: JSON.parse(metadata?.field_note_feedback || '[]'),
    other_handwriting: metadata?.other_handwriting ?? ''
  };
}

async function loadCombinedReviewRows(selection: ReviewSelection) {
  const rows: ReviewRow[] = [];
  const pageMap = new Map<number, ReviewPage>();
  const decisionHistory: ReviewDecision[] = [];

  for (const configuredDir of selection.dirs) {
    const runDir = path.resolve(repoRoot, configuredDir);
    const csvPath = await preferredRowsCsv(runDir);
    const text = await readFile(csvPath, 'utf-8');
    const records = parse(text, {
      columns: true,
      skip_empty_lines: true
    }) as Record<string, string>[];
    const layout = await loadLayoutManifest(runDir);
    const metadata = await loadPageMetadata(runDir);
    const rowLayouts = alignRowLayouts(records, layout);
    rows.push(...records.map((record, index) => normalizeRow(record, index, runDir, layout, rowLayouts)));
    for (const page of mergePages(layout, metadata, runDir)) {
      pageMap.set(page.source_page, page);
    }
    decisionHistory.push(...(await loadDecisionHistory(runDir)));
  }

  rows.sort((a, b) => a.source_page - b.source_page || a.source_row - b.source_row);
  const pages = [...pageMap.values()].sort((a, b) => a.source_page - b.source_page);
  const decisions = latestDecisions(decisionHistory);
  return {
    runDir: selection.name,
    rows,
    pages,
    decisions,
    decisionHistory
  };
}

async function loadReviewSelection() {
  try {
    const text = await readFile(reviewSelectionPath, 'utf-8');
    const selection = JSON.parse(text) as ReviewSelection;
    if (!selection.dirs?.length) return null;
    return selection;
  } catch {
    return null;
  }
}

async function preferredRowsCsv(runDir: string) {
  const transcriptionCsv = path.join(runDir, 'transcription.csv');
  try {
    await stat(transcriptionCsv);
    return transcriptionCsv;
  } catch {
    return path.join(runDir, 'review_rows.csv');
  }
}

export async function appendDecision(runDir: string, decision: ReviewDecision) {
  const decisionsPath = path.join(runDir, 'review_decisions.jsonl');
  await mkdir(path.dirname(decisionsPath), { recursive: true });
  await appendFile(decisionsPath, JSON.stringify(decision) + '\n', 'utf-8');
}

export async function removeDecision(runDir: string, target: Pick<ReviewDecision, 'key' | 'decided_at' | 'chosen_field'>) {
  const decisionsPath = path.join(runDir, 'review_decisions.jsonl');
  const decisions = await loadDecisionHistory(runDir);
  const kept = decisions.filter((decision) => !(
    decision.key === target.key && decision.decided_at === target.decided_at
    && (decision.chosen_field ?? '') === (target.chosen_field ?? '')
  ));
  const text = kept.map((decision) => JSON.stringify(decision)).join('\n');
  await writeFile(decisionsPath, text ? text + '\n' : '', 'utf-8');
}

async function loadDecisionHistory(runDir: string) {
  const decisionsPath = path.join(runDir, 'review_decisions.jsonl');
  try {
    const text = await readFile(decisionsPath, 'utf-8');
    return text
      .split('\n')
      .filter(Boolean)
      .map((line) => ({ ...JSON.parse(line), source_run_dir: runDir }) as ReviewDecision);
  } catch {
    return [];
  }
}

function latestDecisions(decisions: ReviewDecision[]) {
  return Object.fromEntries(decisions.map((decision) => [decision.key, decision]));
}

async function loadLayoutManifest(runDir: string) {
  try {
    const text = await readFile(path.join(runDir, 'layout_manifest.json'), 'utf-8');
    return JSON.parse(text) as LayoutManifest;
  } catch {
    return { pages: [] } satisfies LayoutManifest;
  }
}

async function loadPageMetadata(runDir: string) {
  try {
    const text = await readFile(path.join(runDir, 'page_metadata.csv'), 'utf-8');
    return parse(text, {
      columns: true,
      skip_empty_lines: true
    }) as PageMetadata[];
  } catch {
    return [];
  }
}

function mergePages(layout: LayoutManifest, metadata: PageMetadata[], runDir: string) {
  const pageNumbers = new Set([
    ...layout.pages.map((page) => page.source_page),
    ...metadata.map((page) => Number(page.source_page || 0)).filter(Boolean)
  ]);
  return [...pageNumbers]
    .sort((a, b) => a - b)
    .map((sourcePage) => {
      const pageLayout = layout.pages.find((page) => page.source_page === sourcePage) ?? {
        source_page: sourcePage,
        page_image_width: 0,
        page_image_height: 0,
        columns: [],
        rows: []
      };
      return normalizePage(
        pageLayout,
        metadata.find((page) => Number(page.source_page || 0) === sourcePage),
        runDir
      );
    });
}

function normalizeRow(
  record: Record<string, string>,
  index: number,
  runDir: string,
  layout: LayoutManifest,
  rowLayouts: Map<string, AlignedRowLayout>
): ReviewRow {
  const sourcePage = Number(record.source_page || 0);
  const sourceRow = Number(record.source_row || 0);
  const pageLayout = layout.pages.find((page) => page.source_page === sourcePage);
  const alignment = rowLayouts.get(layoutKey(sourcePage, sourceRow));
  const rowLayout = alignment?.row;
  const rowCropPath = rowLayout?.crop_path
    ? path.resolve(repoRoot, rowLayout.crop_path)
    : path.join(
        runDir,
        'crops',
        `page_${sourcePage.toString().padStart(3, '0')}`,
        'rows',
        `row_${sourceRow.toString().padStart(3, '0')}.png`
      );

  return {
    key: `${record.source_page}:${record.source_row}:${record.source_id_text || index}`,
    source_run_dir: runDir,
    survey_id: record.survey_id ?? '',
    date: record.date ?? '',
    site: record.site ?? '',
    zone: record.zone ?? '',
    plot: record.plot ?? '',
    tree_number: record.tree_number ?? '',
    trunk_number: record.trunk_number ?? '',
    genus: record.genus ?? '',
    spp: record.spp ?? '',
    dbh_mm: normalizeNumericText(record.dbh_mm),
    health: normalizeNumericText(record.health),
    standing: record.standing ?? '',
    poison_ivy: record.poison_ivy ?? '',
    notes: record.notes ?? '',
    section: record.section ?? 'legacy',
    species_update: record.species_update ?? '',
    identity_source: record.identity_source ?? '',
    field_date: record.field_date ?? '',
    source_page: sourcePage,
    source_row: sourceRow,
    source_row_label: record.source_row_label ?? '',
    source_id_text: record.source_id_text ?? '',
    source_page_title: record.source_page_title ?? '',
    source_image: record.source_image ?? '',
    source_json: record.source_json ?? '',
    transcription_flags: record.transcription_flags ?? '',
    review_flags: record.review_flags ?? '',
    row_crop_path: path.relative(repoRoot, rowCropPath),
    page_image_width: pageLayout?.page_image_width ?? 0,
    page_image_height: pageLayout?.page_image_height ?? 0,
    row_box: rowLayout?.box ?? null,
    page_columns: alignment?.columns ?? pageLayout?.columns ?? []
  };
}

function alignRowLayouts(records: Record<string, string>[], layout: LayoutManifest) {
  const rowLayouts = new Map<string, AlignedRowLayout>();
  for (const pageLayout of layout.pages) {
    for (const table of pageLayout.tables ?? [pageLayout]) {
      const columnNames = new Set(table.columns.map((column) => column.name));
      const layoutSection = table.section ?? (columnNames.has('printed_dbh')
        ? 'main'
        : columnNames.has('tag_text') && columnNames.has('dbh_mm')
          ? 'newly_tracked'
          : '');
      const pageRecords = records
        .filter((record) => Number(record.source_page || 0) === pageLayout.source_page)
        .filter((record) => !layoutSection || (record.section || 'legacy') === layoutSection)
        .sort((a, b) => Number(a.source_row || 0) - Number(b.source_row || 0));
      const hasLabels = table.rows.some((row) => row.source_row_label !== undefined);
      const firstDataIndex = layoutSection ? 0 : firstDataRowIndex(table.rows);

      pageRecords.forEach((record, recordIndex) => {
        const sourceRow = Number(record.source_row || 0);
        const rowLayout = hasLabels
          ? table.rows.find((row) => row.source_row_label === record.source_row_label)
          : table.rows[firstDataIndex + recordIndex];
        if (rowLayout) rowLayouts.set(layoutKey(pageLayout.source_page, sourceRow), { row: rowLayout, columns: table.columns });
      });
    }
  }
  return rowLayouts;
}

function firstDataRowIndex(rows: LayoutRow[]) {
  if (!rows.length) return 0;
  const heights = rows.map((row) => row.box.height).sort((a, b) => a - b);
  const medianHeight = heights[Math.floor(heights.length / 2)] || 1;
  const tallLeadIndex = rows.slice(0, 16).findLastIndex((row) => row.box.height > medianHeight * 1.8);
  if (tallLeadIndex >= 0) {
    const candidateIndex = firstNormalHeightRow(rows, medianHeight, tallLeadIndex + 1);
    const nextRow = rows[candidateIndex + 1];
    if (candidateIndex === tallLeadIndex + 1 && nextRow && nextRow.box.height >= medianHeight * 0.75) {
      return candidateIndex + 1;
    }
    return candidateIndex;
  }

  const shortLeadCount = rows.findIndex((row) => row.box.height >= medianHeight * 0.75);
  if (shortLeadCount > 0) return Math.min(shortLeadCount, rows.length);
  return Math.min(1, rows.length);
}

function firstNormalHeightRow(rows: LayoutRow[], medianHeight: number, startIndex: number) {
  const index = rows.findIndex((row, rowIndex) => rowIndex >= startIndex && row.box.height >= medianHeight * 0.75);
  return index >= 0 ? index : Math.min(startIndex, rows.length);
}

function layoutKey(sourcePage: number, sourceRow: number) {
  return `${sourcePage}:${sourceRow}`;
}

function normalizeNumericText(value: string | undefined) {
  const text = value ?? '';
  if (!/^-?\d+\.0$/.test(text)) return text;
  return text.slice(0, -2);
}

type LayoutManifest = {
  pages: LayoutPage[];
};

type LayoutPage = LayoutTable & {
  source_page: number;
  image_path?: string;
  page_image_width: number;
  page_image_height: number;
  tables?: LayoutTable[];
};

type LayoutTable = {
  section?: string;
  columns: Array<{
    index: number;
    name: string;
    box: LayoutBox;
  }>;
  rows: LayoutRow[];
};

type LayoutRow = {
  source_row?: number;
  source_row_label?: string;
  crop_path?: string;
  box: LayoutBox;
};

type LayoutBox = {
  x: number;
  y: number;
  width: number;
  height: number;
  skew_y?: number;
};

type AlignedRowLayout = { row: LayoutRow; columns: LayoutTable['columns'] };

type ReviewSelection = {
  name: string;
  dirs: string[];
};

type PageMetadata = {
  source_page: string;
  source_image?: string;
  source_page_title: string;
  plot: string;
  field_date: string;
  crew: string;
  problems_and_info: string;
  difficulty: string;
  page_flags: string;
  observer?: string;
  recorder?: string;
  bonus_person?: string;
  recheck_answers?: string;
  field_note_feedback?: string;
  other_handwriting?: string;
};
