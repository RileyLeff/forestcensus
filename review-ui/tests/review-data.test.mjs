import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { loadReviewRows, removeDecision } from '../src/lib/server/review-data.ts';

const box = (y) => ({ x: 100, y, width: 2000, height: 55 });
const columns = (names) => names.map((name, index) => ({ index, name, box: box(0) }));

async function withRun(files, check) {
  const run = await mkdtemp(path.join(tmpdir(), 'forest-review-test-'));
  const previous = process.env.REVIEW_RUN_DIR;
  try {
    for (const [name, contents] of Object.entries(files)) {
      await writeFile(path.join(run, name), typeof contents === 'string' ? contents : JSON.stringify(contents));
    }
    process.env.REVIEW_RUN_DIR = run;
    await check(await loadReviewRows());
  } finally {
    if (previous === undefined) delete process.env.REVIEW_RUN_DIR;
    else process.env.REVIEW_RUN_DIR = previous;
    await rm(run, { recursive: true, force: true });
  }
}

test('mixed sections match physical labels without shifting blank recruit slots', async () => {
  await withRun({
    'transcription.csv': [
      'source_page,source_row,source_row_label,source_id_text,section',
      '1,1,41,main-tree,main',
      '1,2,N2,new-tree-2,newly_tracked',
      '1,3,N6,new-tree-6,newly_tracked'
    ].join('\n'),
    'layout_manifest.json': { pages: [{
      source_page: 1, page_image_width: 2550, page_image_height: 3300,
      columns: [], rows: [], tables: [
        { section: 'main', columns: columns(['health', 'printed_dbh']), rows: [{ source_row_label: '41', box: box(600) }] },
        { section: 'newly_tracked', columns: columns(['dbh_mm', 'health']), rows: Array.from({ length: 6 }, (_, i) => ({ source_row_label: `N${i + 1}`, box: box(1200 + i * 60) })) }
      ]
    }] }
  }, ({ rows }) => {
    assert.deepEqual(rows.map((r) => r.row_box.y), [600, 1260, 1500]);
    assert.deepEqual(rows[0].page_columns.map((c) => c.name), ['health', 'printed_dbh']);
    assert.deepEqual(rows[1].page_columns.map((c) => c.name), ['dbh_mm', 'health']);
    assert.equal(new Set(rows.map((r) => r.key)).size, 3);
  });
});

test('legacy one-table manifests still align their rows', async () => {
  await withRun({
    'transcription.csv': 'source_page,source_row,source_id_text\n1,1,old-tree\n',
    'layout_manifest.json': { pages: [{
      source_page: 1, page_image_width: 2550, page_image_height: 3300,
      columns: columns(['id_text', 'dbh_mm']), rows: [{ box: box(600) }, { box: box(655) }]
    }] }
  }, ({ rows }) => {
    assert.equal(rows[0].row_box.y, 655);
  });
});

test('rowless rematerialized pages use the original scan path from metadata', async () => {
  await withRun({
    'transcription.csv': 'source_page,source_row\n',
    'page_metadata.csv': 'source_page,source_image,plot\n2,output/original/pages/page_002.png,R1\n',
    'layout_manifest.json': { pages: [{
      source_page: 2, page_image_width: 2550, page_image_height: 3300, columns: [], rows: []
    }] }
  }, ({ rows, pages }) => {
    assert.equal(rows.length, 0);
    assert.equal(pages[0].source_image, 'output/original/pages/page_002.png');
  });
});

test('October page evidence preserves independent feedback without inventing rows', async () => {
  const answer = [{ question_number: 1, question: 'Standing?', answer: 'Leaning', flags: [] }];
  const feedback = [{ note_number: 1, helpful: true, confusing: null, incorrect: true, handwritten_notes: 'Alias', flags: [] }];
  const csvJson = (value) => `"${JSON.stringify(value).replaceAll('"', '""')}"`;
  await withRun({
    'transcription.csv': 'source_page,source_row\n',
    'page_metadata.csv': `source_page,plot,observer,recheck_answers,field_note_feedback,other_handwriting\n11,R4,Riley,${csvJson(answer)},${csvJson(feedback)},Margin note\n`
  }, ({ rows, pages }) => {
    assert.equal(rows.length, 0);
    assert.deepEqual(pages[0].recheck_answers, answer);
    assert.deepEqual(pages[0].field_note_feedback, feedback);
    assert.equal(pages[0].other_handwriting, 'Margin note');
    assert.equal(pages[0].observer, 'Riley');
  });
});

test('batch decisions sharing a timestamp remain separate and undo is field-specific', async () => {
  const base = { key: '8:1:tree', action: 'edit', decided_at: '2026-10-03T19:39:12Z' };
  const entries = [
    { ...base, chosen_field: 'genus', chosen_value: 'Vac' },
    { ...base, chosen_field: 'spp', chosen_value: 'spp' },
    { ...base, key: '8:2:other', chosen_field: 'health', chosen_value: '8' }
  ];
  await withRun({
    'transcription.csv': 'source_page,source_row,source_id_text\n8,1,tree\n8,2,other\n',
    'review_decisions.jsonl': entries.map((entry) => JSON.stringify(entry)).join('\n') + '\n'
  }, async ({ runDir, decisionHistory }) => {
    assert.equal(decisionHistory.length, 3);
    assert.equal(new Set(decisionHistory).size, 3);
    await removeDecision(runDir, entries[0]);
    const after = await loadReviewRows();
    assert.deepEqual(after.decisionHistory.map((d) => [d.key, d.chosen_field]), [
      ['8:1:tree', 'spp'], ['8:2:other', 'health']
    ]);
  });
});
