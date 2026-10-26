<script lang="ts">
  import { tick, untrack } from 'svelte';
  import {
    Check,
    ChevronLeft,
    ChevronRight,
    Edit3,
    Filter,
    History,
    Search,
    SkipForward,
    Trash2,
    X,
    ZoomIn,
    ZoomOut
  } from 'lucide-svelte';
  import type { PageData } from './$types';
  import type { ReviewDecision, ReviewPage, ReviewRow } from '$lib/types';

  const { data }: { data: PageData } = $props();
  const editableFields = [
    'tree_number',
    'genus',
    'spp',
    'trunk_number',
    'dbh_mm',
    'health',
    'standing',
    'poison_ivy',
    'species_update',
    'notes'
  ] as const;

  let rows = $derived(data.rows as ReviewRow[]);
  let processedPages = $derived((data.pages as ReviewPage[]) ?? []);
  let currentPage = $state(0);
  let selectedKey = $state('');
  let index = $state(0);
  let selectedField = $state('health');
  let note = $state('');
  let status = $state('');
  let hoveredKey = $state('');
  let enabledFlags: Record<string, boolean> = $state({});
  let filtersTouched = $state(false);
  let queueMode = $state<'review' | 'all'>('review');
  let queueSearch = $state('');
  let decisionSearch = $state('');
  let zoom = $state(1);
  let draftRowKey = $state('');
  let rowDraft: Partial<Record<EditableField, string>> = $state({});
  let viewerElement: HTMLElement | undefined = $state();
  let documentElement: HTMLElement | undefined = $state();
  let decisionHistory: ReviewDecision[] = $state(untrack(() => [...(data.decisionHistory as ReviewDecision[])]));
  let decisions = $derived.by(() => Object.fromEntries(decisionHistory.map((decision) => [decision.key, decision])));
  let fieldDecisions = $derived.by(() => {
    const byRow: Record<string, Record<string, ReviewDecision>> = {};
    for (const decision of decisionHistory) {
      if (decision.action !== 'edit' || !decision.chosen_field) continue;
      byRow[decision.key] ??= {};
      byRow[decision.key][decision.chosen_field] = decision;
    }
    return byRow;
  });

  let pages = $derived.by(() => {
    const pageNumbers: number[] = [];
    for (const page of processedPages) {
      if (!pageNumbers.includes(page.source_page)) pageNumbers.push(page.source_page);
    }
    for (const row of rows) {
      if (!pageNumbers.includes(row.source_page)) pageNumbers.push(row.source_page);
    }
    return pageNumbers.sort((a, b) => a - b);
  });
  let activePage = $derived(currentPage || pages[0] || 0);
  let pageIndex = $derived(Math.max(pages.indexOf(activePage), 0));
  let reviewRows = $derived(rows.filter((row) => flagsFor(row).length > 0));
  let queueBaseRows = $derived(queueMode === 'all' ? rows : reviewRows);
  let allFlags = $derived.by(() => {
    const flags: string[] = [];
    for (const row of reviewRows) {
      for (const flag of flagsFor(row)) {
        if (!flags.includes(flag)) flags.push(flag);
      }
    }
    return flags.sort();
  });
  let visibleRows = $derived.by(() => {
    const query = queueSearch.trim().toLowerCase();
    const filteredByFlags = queueMode === 'review' && filtersTouched ? queueBaseRows.filter(rowIsVisible) : queueBaseRows;
    if (!query) return filteredByFlags;
    return filteredByFlags.filter((row) => queueSearchText(row).includes(query));
  });
  let total = $derived(visibleRows.length);
  let selectedRow = $derived(rows.find((row) => row.key === selectedKey));
  let current = $derived(selectedRow ?? (visibleRows[index]?.source_page === activePage ? visibleRows[index] : undefined));
  let currentDecision = $derived(current ? decisions[current.key] : undefined);
  let fieldChoices = $derived(choicesFor(current, selectedField));
  let isNotesField = $derived(selectedField === 'notes');
  let isChoiceField = $derived(['health', 'standing', 'poison_ivy'].includes(selectedField));
  let draftChangedFields = $derived.by(() => {
    if (!current) return [];
    return editableFieldsFor(current).filter((field) => draftValue(field) !== effectiveFieldValue(current, field));
  });
  let draftChangedCount = $derived(draftChangedFields.length);
  let pageRows = $derived(rows.filter((row) => row.source_page === activePage && row.row_box));
  let pageInfo = $derived(processedPages.find((page) => page.source_page === activePage));
  let pageImageSource = $derived(pageRows[0]?.source_image ?? rows.find((row) => row.source_page === activePage)?.source_image ?? pageInfo?.source_image);
  let hoveredRow = $derived(rows.find((row) => row.key === hoveredKey));
  let overlayRow = $derived(hoveredRow ?? (current?.source_page === activePage ? current : undefined));
  let reviewedCount = $derived(queueBaseRows.filter((row) => Boolean(decisions[row.key])).length);
  let reviewProgress = $derived(queueBaseRows.length ? Math.min((reviewedCount / queueBaseRows.length) * 100, 100) : 0);
  let recentDecisions = $derived([...decisionHistory].reverse());
  let visibleDecisions = $derived.by(() => {
    const query = decisionSearch.trim().toLowerCase();
    if (!query) return recentDecisions;
    return recentDecisions.filter((decision) => decisionSearchText(decision).includes(query));
  });

  function imageUrl(path: string) {
    return `/api/image?path=${encodeURIComponent(path)}`;
  }

  function go(delta: number) {
    if (!total) return;
    index = Math.min(Math.max(index + delta, 0), total - 1);
    selectRow(visibleRows[index]);
  }

  function goPage(delta: number) {
    if (!pages.length) return;
    const nextPage = pages[Math.min(Math.max(pageIndex + delta, 0), pages.length - 1)];
    currentPage = nextPage;
    const firstWarning = visibleRows.find((row) => row.source_page === nextPage);
    const firstPageRow = rows.find((row) => row.source_page === nextPage);
    if (firstWarning ?? firstPageRow) {
      selectRow(firstWarning ?? firstPageRow);
    } else {
      selectedKey = '';
      hoveredKey = '';
      note = '';
      status = '';
    }
  }

  async function selectRow(row: ReviewRow | undefined, preferredField?: string, reveal = true) {
    if (!row) return;
    const isSameRow = row.key === selectedKey;
    selectedKey = row.key;
    currentPage = row.source_page;
    const queueIndex = visibleRows.findIndex((item) => item.key === row.key);
    if (queueIndex >= 0) index = queueIndex;
    selectedField = preferredField && isEditableField(preferredField) ? preferredField : defaultField(row);
    if (!isSameRow) resetDraft(row);
    note = '';
    status = '';
    hoveredKey = '';
    if (reveal) {
      await tick();
      revealRow(row);
    }
  }

  function chooseField(field: string) {
    selectedField = field;
  }

  function selectRowFromPage(row: ReviewRow, event: MouseEvent) {
    selectRow(row, clickedColumnField(row, event), false);
  }

  function revealRow(row: ReviewRow) {
    if (!row.row_box || !row.page_image_height || !viewerElement || !documentElement) return;
    const rowTop = documentElement.offsetTop + (row.row_box.y / row.page_image_height) * documentElement.offsetHeight;
    viewerElement.scrollTo({
      top: Math.max(0, rowTop - viewerElement.clientHeight * 0.32),
      behavior: 'smooth'
    });
  }

  function setZoom(nextZoom: number) {
    zoom = Math.min(Math.max(nextZoom, 0.75), 1.5);
  }

  function clickedColumnField(row: ReviewRow, event: MouseEvent) {
    if (!row.row_box) return undefined;
    const target = event.currentTarget as HTMLElement;
    const targetBox = target.getBoundingClientRect();
    const xWithinRow = ((event.clientX - targetBox.left) / targetBox.width) * row.row_box.width;
    const xOnPage = row.row_box.x + xWithinRow;
    const column = row.page_columns.find((item) => xOnPage >= item.box.x && xOnPage <= item.box.x + item.box.width);
    return column ? editableFieldForColumn(column.name) : undefined;
  }

  async function saveDecisions(decisionsToSave: ReviewDecision[], successMessage: string) {
    if (!decisionsToSave.length) return false;
    const body = new URLSearchParams({
      runDir: data.runDir,
      decisions: JSON.stringify(decisionsToSave)
    });
    const response = await fetch('?/decideBatch', {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body
    });
    if (!response.ok) {
      status = 'Decision failed to save';
      return false;
    }
    decisionHistory = [...decisionHistory, ...decisionsToSave];
    status = successMessage;
    note = '';
    return true;
  }

  async function acceptRow() {
    if (!current) return;
    if (draftChangedCount > 0) {
      status = 'Save row edits before marking OK as is';
      return;
    }
    const decidedAt = new Date().toISOString();
    const saved = await saveDecisions(
      [
        {
          key: current.key,
          source_run_dir: current.source_run_dir,
          action: 'accept',
          chosen_field: '',
          chosen_value: '',
          note,
          decided_at: decidedAt
        }
      ],
      'Row marked OK as is'
    );
    if (saved) resetDraft(current);
  }

  async function saveRowEdits() {
    if (!current) return;
    if (draftChangedCount === 0) {
      status = 'No row edits to save';
      return;
    }
    const timestamp = Date.now();
    const decisionsToSave = draftChangedFields.map((field, fieldIndex) => ({
      key: current.key,
      source_run_dir: current.source_run_dir,
      action: 'edit' as const,
      chosen_field: field,
      chosen_value: draftValue(field),
      note,
      decided_at: new Date(timestamp + fieldIndex).toISOString()
    }));
    const saved = await saveDecisions(
      decisionsToSave,
      `Saved ${decisionsToSave.length} row ${decisionsToSave.length === 1 ? 'edit' : 'edits'}`
    );
    if (saved) resetDraft(current);
  }

  async function skipRow() {
    if (!current) return;
    const saved = await saveDecisions(
      [
        {
          key: current.key,
          source_run_dir: current.source_run_dir,
          action: 'skip',
          chosen_field: '',
          chosen_value: '',
          note,
          decided_at: new Date().toISOString()
        }
      ],
      'Row skipped'
    );
    if (saved) resetDraft(current);
  }

  function resetDraft(row: ReviewRow) {
    draftRowKey = row.key;
    rowDraft = Object.fromEntries(editableFields.map((field) => [field, effectiveFieldValue(row, field)])) as Record<
      EditableField,
      string
    >;
  }

  function draftValue(field: string) {
    if (!isEditableField(field)) return '';
    if (current && current.key !== draftRowKey) return effectiveFieldValue(current, field);
    return rowDraft[field] ?? '';
  }

  function setDraftValue(field: string, value: string) {
    if (!isEditableField(field)) return;
    if (current && current.key !== draftRowKey) resetDraft(current);
    rowDraft = {
      ...rowDraft,
      [field]: value
    };
  }

  function effectiveFieldValue(row: ReviewRow, field: EditableField) {
    return fieldDecisions[row.key]?.[field]?.chosen_value ?? valueFor(row, field);
  }

  function isEditableField(field: string): field is EditableField {
    return editableFields.includes(field as EditableField);
  }

  function selectedDraftValue() {
    return draftValue(selectedField);
  }

  function fieldIsDirty(field: string) {
    if (!current || !isEditableField(field)) return false;
    return draftValue(field) !== effectiveFieldValue(current, field);
  }

  function handleDraftInput(event: Event) {
    const target = event.currentTarget as HTMLInputElement | HTMLTextAreaElement;
    setDraftValue(selectedField, target.value);
  }

  async function deleteDecision(decision: ReviewDecision) {
    const body = new URLSearchParams({
      runDir: decision.source_run_dir || data.runDir,
      key: decision.key,
      chosen_field: decision.chosen_field ?? '',
      decided_at: decision.decided_at
    });
    const response = await fetch('?/deleteDecision', {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body
    });
    if (!response.ok) {
      status = 'Decision delete failed';
      return;
    }
    decisionHistory = decisionHistory.filter(
      (item) => !(
        item.key === decision.key && item.decided_at === decision.decided_at
        && (item.chosen_field ?? '') === (decision.chosen_field ?? '')
      )
    );
    status = 'Decision removed';
  }

  function handleKeydown(event: KeyboardEvent) {
    const target = event.target as HTMLElement | null;
    if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA') return;
    if (event.key === 'ArrowRight' || event.key === 'n') {
      event.preventDefault();
      go(1);
    } else if (event.key === 'ArrowLeft' || event.key === 'p') {
      event.preventDefault();
      go(-1);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (draftChangedCount > 0) {
        saveRowEdits();
      } else {
        acceptRow();
      }
    } else if (event.key === 'e') {
      event.preventDefault();
      saveRowEdits();
    } else if (event.key === 's') {
      event.preventDefault();
      skipRow();
    } else if (/^[0-9]$/.test(event.key) || event.key === '-' || event.key === '=') {
      const choice = fieldChoices.find((item) => item.shortcut === event.key);
      if (choice) {
        event.preventDefault();
        setDraftValue(selectedField, choice.value);
      }
    }
  }

  function defaultField(row: ReviewRow | undefined) {
    if (!row) return 'health';
    const flags = row.review_flags || row.transcription_flags;
    if (flags.includes('health')) return 'health';
    if (flags.includes('standing')) return 'standing';
    if (flags.includes('species') || row.species_update) return 'species_update';
    if (flags.includes('identity')) return row.section === 'newly_tracked' ? 'tree_number' : 'health';
    if (row.notes) return 'notes';
    if (flags.includes('dbh')) return 'dbh_mm';
    return 'health';
  }

  function valueFor(row: ReviewRow | undefined, field: string) {
    if (!row) return '';
    const value = String(row[field as keyof ReviewRow] ?? '');
    if (['health', 'standing', 'poison_ivy'].includes(field) && /^-?\d+\.0+$/.test(value)) {
      return value.slice(0, value.indexOf('.'));
    }
    return value;
  }

  function choicesFor(row: ReviewRow | undefined, field: string) {
    const currentValue = row && isEditableField(field) ? effectiveFieldValue(row, field) : valueFor(row, field);
    if (field === 'health') {
      return [
        ...Array.from({ length: 10 }, (_, value) => ({
          label: String(value),
          value: String(value),
          shortcut: String(value)
        })),
        { label: '10', value: '10', shortcut: '-' },
        { label: 'blank', value: '', shortcut: '=' },
        currentValue && !/^(?:[0-9]|10)$/.test(currentValue)
          ? { label: currentValue, value: currentValue, shortcut: '' }
          : null
      ].filter((choice): choice is Choice => choice !== null).filter(uniqueChoice);
    }
    if (field === 'standing' || field === 'poison_ivy') {
      return [
        { label: '1', value: '1', shortcut: '1' },
        { label: '0', value: '0', shortcut: '0' },
        { label: 'blank', value: '', shortcut: '=' }
      ].filter(uniqueChoice);
    }
    return [
      { label: currentValue || 'blank', value: currentValue, shortcut: '' },
      { label: 'blank', value: '', shortcut: '=' }
    ].filter(uniqueChoice);
  }

  function uniqueChoice(choice: Choice, index: number, choices: Choice[]) {
    return choices.findIndex((item) => item.value === choice.value) === index;
  }

  function choiceLabel(choice: Choice) {
    if (choice.value === '') return 'Clear';
    return choice.label;
  }

  function boxStyle(row: ReviewRow) {
    if (!row.row_box || !row.page_image_width || !row.page_image_height) return '';
    const box = row.row_box;
    return [
      `left: ${(box.x / row.page_image_width) * 100}%`,
      `top: ${(box.y / row.page_image_height) * 100}%`,
      `width: ${(box.width / row.page_image_width) * 100}%`,
      `height: ${(box.height / row.page_image_height) * 100}%`,
      `transform: skewY(${Math.atan(box.skew_y ?? 0)}rad)`,
      'transform-origin: left top'
    ].join('; ');
  }

  function syntheticRowStyle(row: ReviewRow) {
    if (!row.row_box || !row.page_image_width || !row.page_image_height) return '';
    const columns = usableColumns(row);
    const firstColumn = columns[0];
    const lastColumn = columns[columns.length - 1];
    const box = row.row_box;
    const x = firstColumn ? firstColumn.box.x : box.x;
    const width = firstColumn && lastColumn ? lastColumn.box.x + lastColumn.box.width - firstColumn.box.x : box.width;
    const height = Math.max(box.height * 1.15, 24);
    const rowY = box.y + (box.skew_y ?? 0) * (x - box.x);
    const y = rowY - height - 2 >= 0 ? rowY - height - 2 : rowY + box.height + 2;
    return [
      `left: ${(x / row.page_image_width) * 100}%`,
      `top: ${(y / row.page_image_height) * 100}%`,
      `width: ${(width / row.page_image_width) * 100}%`,
      `height: ${(height / row.page_image_height) * 100}%`,
      `grid-template-columns: ${gridColumns(row)}`,
      `transform: skewY(${Math.atan(box.skew_y ?? 0)}rad)`,
      'transform-origin: left top'
    ].join('; ');
  }

  function gridColumns(row: ReviewRow) {
    const columns = usableColumns(row);
    if (!columns.length) return '1fr';
    return columns.map((column) => `${column.box.width}fr`).join(' ');
  }

  function usableColumns(row: ReviewRow) {
    return row.page_columns.filter((column) =>
      [
        'row_label',
        'id_text',
        'tag_text',
        'species_text',
        'stem_text',
        'dbh_mm',
        'health',
        'standing',
        'poison_ivy',
        'printed_dbh',
        'dhas_1',
        'dhas_2',
        'hsp_1',
        'hsp_2',
        'species_update',
        'notes'
      ].includes(column.name)
    );
  }

  function columnValue(row: ReviewRow, column: string) {
    if (column === 'species_text') {
      const genus = row.key === draftRowKey ? draftValue('genus') : effectiveFieldValue(row, 'genus');
      const species = row.key === draftRowKey ? draftValue('spp') : effectiveFieldValue(row, 'spp');
      return `${genus.slice(0, 3)}${species.slice(0, 3)}`.toUpperCase();
    }
    const editableField = editableFieldForColumn(column);
    if (row.key === draftRowKey && editableField) {
      return draftValue(editableField);
    }
    const decision = editableField ? fieldDecisions[row.key]?.[editableField] : undefined;
    if (decision) {
      return decision.chosen_value ?? '';
    }
    return rawColumnValue(row, column);
  }

  function rawColumnValue(row: ReviewRow, column: string) {
    if (column === 'row_label') return row.source_row_label;
    if (column === 'id_text') return row.source_id_text;
    if (column === 'tag_text') return row.tree_number;
    if (column === 'species_text') return `${row.genus.slice(0, 3)}${row.spp.slice(0, 3)}`.toUpperCase();
    if (column === 'stem_text') return row.trunk_number;
    if (column === 'health') return valueFor(row, 'health');
    if (column === 'standing') return valueFor(row, 'standing');
    if (column === 'poison_ivy') return valueFor(row, 'poison_ivy');
    if (['printed_dbh', 'dhas_1', 'dhas_2', 'hsp_1', 'hsp_2'].includes(column)) return '';
    if (column === 'species_update') return row.species_update;
    if (column === 'notes') return row.notes;
    return valueFor(row, column);
  }

  function flagsFor(row: ReviewRow) {
    return (row.review_flags || row.transcription_flags || '').split('; ').filter(Boolean);
  }

  function formatFlag(flag: string) {
    const labels: Record<string, string> = {
      model_flagged_ambiguity: 'Model uncertainty',
      newly_tracked_row: 'Newly tracked',
      notes_present: 'Has notes',
      species_update_present: 'Species update'
    };
    return labels[flag] ?? flag.replaceAll('_', ' ');
  }

  function queueSearchText(row: ReviewRow) {
    return [
      row.plot,
      row.tree_number,
      row.source_id_text,
      row.genus,
      row.spp,
      row.trunk_number,
      row.source_page,
      row.source_row_label,
      ...flagsFor(row).map(formatFlag)
    ]
      .join(' ')
      .toLowerCase();
  }

  function clearQueueSearch() {
    queueSearch = '';
  }

  async function setQueueMode(mode: 'review' | 'all') {
    queueMode = mode;
    queueSearch = '';
    await tick();
    const currentIndex = current ? visibleRows.findIndex((row) => row.key === current?.key) : -1;
    if (currentIndex >= 0) {
      index = currentIndex;
    } else {
      index = 0;
      selectRow(visibleRows[0]);
    }
  }

  function runLabel(runDir: string) {
    const name = runDir.split('/').filter(Boolean).at(-1) ?? runDir;
    return name.replace(/^_dev_/, '').replaceAll('_', ' ');
  }

  function rowForDecision(decision: ReviewDecision) {
    return rows.find((row) => row.key === decision.key);
  }

  function decisionValue(decision: ReviewDecision) {
    if (decision.action === 'accept') return 'row ok';
    if (decision.action === 'skip') return 'skip';
    return `${decision.chosen_field || 'field'}=${decision.chosen_value || 'blank'}`;
  }

  function decisionSearchText(decision: ReviewDecision) {
    const row = rowForDecision(decision);
    return [
      row?.source_page,
      row?.source_row_label,
      row?.source_id_text,
      decision.key,
      decision.action,
      decision.chosen_field,
      decision.chosen_value,
      decision.note
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
  }

  function rowIsVisible(row: ReviewRow) {
    const flags = flagsFor(row);
    if (!flags.length) return true;
    return flags.some((flag) => enabledFlags[flag] !== false);
  }

  function toggleFlag(flag: string) {
    filtersTouched = true;
    enabledFlags[flag] = enabledFlags[flag] === false;
    const visibleCount = reviewRows.filter(rowIsVisible).length;
    index = Math.min(index, Math.max(visibleCount - 1, 0));
  }

  function editableFieldsFor(row: ReviewRow | undefined): EditableField[] {
    if (!row || row.section === 'legacy') {
      return ['dbh_mm', 'health', 'standing', 'poison_ivy', 'notes'];
    }
    if (row.section === 'newly_tracked') {
      return [
        'tree_number',
        'genus',
        'spp',
        'trunk_number',
        'dbh_mm',
        'health',
        'standing',
        'poison_ivy',
        'notes'
      ];
    }
    return ['health', 'standing', 'poison_ivy', 'species_update', 'notes'];
  }

  function editableFieldForColumn(column: string): EditableField | undefined {
    const mapped = {
      tag_text: 'tree_number',
      species_text: 'spp',
      stem_text: 'trunk_number'
    }[column] ?? column;
    return isEditableField(mapped) ? mapped : undefined;
  }

  function fieldLabel(field: EditableField) {
    const labels: Partial<Record<EditableField, string>> = {
      tree_number: 'tag',
      trunk_number: 'stem',
      dbh_mm: 'dbh',
      poison_ivy: 'poison ivy',
      species_update: 'species update'
    };
    return labels[field] ?? field;
  }

  type Choice = {
    label: string;
    value: string;
    shortcut: string;
  };
  type EditableField = (typeof editableFields)[number];
</script>

<svelte:window onkeydown={handleKeydown} />
<svelte:head>
  <title>Forest Census Review</title>
</svelte:head>

<main class="shell">
  <header class="topbar">
    <div class="run-title">
      <h1>Transcription review</h1>
      <span title={data.runDir}>{runLabel(data.runDir)}</span>
    </div>
    <div class="progress" aria-label="review progress">
      <div>
        <strong>{reviewedCount}</strong>
        <span>of {queueBaseRows.length} decided</span>
      </div>
      <div class="progress-track"><span style:width={`${reviewProgress}%`}></span></div>
    </div>
  </header>

  {#if rows.length || processedPages.length}
    <section class="workspace">
      <aside class="queue" aria-label="review queue">
        <div class="queue-header">
          <div class="queue-heading">
            <div>
              <h2>Review queue</h2>
              <span>{total} shown</span>
            </div>
            {#if current}<span class="queue-position">{Math.min(index + 1, total)} / {total}</span>{/if}
          </div>

          <div class="queue-modes" aria-label="Queue scope">
            <button class:active={queueMode === 'review'} onclick={() => setQueueMode('review')}>
              Needs review <span>{reviewRows.length}</span>
            </button>
            <button class:active={queueMode === 'all'} onclick={() => setQueueMode('all')}>
              All rows <span>{rows.length}</span>
            </button>
          </div>

          <label class="queue-search">
            <Search size={15} />
            <input bind:value={queueSearch} aria-label="Search review queue" placeholder="Tag, plot, species…" />
            {#if queueSearch}
              <button type="button" onclick={clearQueueSearch} title="Clear search"><X size={14} /></button>
            {/if}
          </label>

          {#if queueMode === 'review'}
            <details class="filter-panel">
              <summary><Filter size={14} /> Review reasons</summary>
              <div class="filters" aria-label="flag filters">
                {#each allFlags as flag (flag)}
                  <button
                    class="flag-filter"
                    class:off={filtersTouched && enabledFlags[flag] === false}
                    onclick={() => toggleFlag(flag)}
                  >
                    {formatFlag(flag)}
                  </button>
                {/each}
              </div>
            </details>
          {/if}
        </div>

        <div class="queue-items">
          {#each visibleRows as row (row.key)}
            <button
              class="queue-row"
              class:active={row.key === current?.key}
              class:done={Boolean(decisions[row.key])}
              onclick={() => selectRow(row)}
            >
              <span class="queue-identity">
                <strong>{row.plot}/{row.tree_number || 'unknown'}</strong>
                <em>stem {row.trunk_number || '?'}</em>
              </span>
              <span class="queue-context">{row.genus} {row.spp} · page {row.source_page}, row {row.source_row_label}</span>
              {#if flagsFor(row)[0]}<span class="queue-reason">{formatFlag(flagsFor(row)[0])}</span>{/if}
            </button>
          {:else}
            <p class="queue-empty">No review items match.</p>
          {/each}
        </div>
      </aside>

      <section class="viewer" bind:this={viewerElement}>
        <div class="page-tools">
          <div class="page-nav">
            <button type="button" onclick={() => goPage(-1)} disabled={pageIndex === 0} title="Previous page">
              <ChevronLeft size={16} />
            </button>
            <strong>Page {activePage}</strong>
            <span title="Position in this run">{pageIndex + 1} / {pages.length}</span>
            <button type="button" onclick={() => goPage(1)} disabled={pageIndex === pages.length - 1} title="Next page">
              <ChevronRight size={16} />
            </button>
          </div>
          <div class="page-summary">
            {#if pageInfo?.plot}<strong>{pageInfo.plot}</strong>{/if}
            {#if pageInfo?.field_date}<span>{pageInfo.field_date}</span>{/if}
            {#if pageInfo?.crew}<span>{pageInfo.crew}</span>{/if}
            <span>{pageRows.length} rows</span>
          </div>
          <div class="zoom-tools">
            <button type="button" onclick={() => setZoom(zoom - 0.25)} disabled={zoom <= 0.75} title="Zoom out">
              <ZoomOut size={16} />
            </button>
            <span>{Math.round(zoom * 100)}%</span>
            <button type="button" onclick={() => setZoom(zoom + 0.25)} disabled={zoom >= 1.5} title="Zoom in">
              <ZoomIn size={16} />
            </button>
          </div>
        </div>
        {#if pageInfo?.problems_and_info || pageInfo?.page_flags}
          <div class="page-alert">
            {#if pageInfo.problems_and_info}<span><strong>Field note:</strong> {pageInfo.problems_and_info}</span>{/if}
            {#if pageInfo.page_flags}<span>{pageInfo.page_flags}</span>{/if}
          </div>
        {/if}
        {#if pageInfo && (pageInfo.recheck_answers.length || pageInfo.field_note_feedback.length || pageInfo.other_handwriting)}
          <details class="page-evidence">
            <summary>Page notes · {pageInfo.recheck_answers.length} rechecks · {pageInfo.field_note_feedback.length} field notes</summary>
            {#each pageInfo.recheck_answers as answer (answer.question_number)}
              <div class="page-evidence-item">
                <strong>Q{answer.question_number}{answer.tags?.length ? ` · ${answer.tags.join(', ')}` : ''}</strong>
                {#if answer.question}<p>{answer.question}</p>{/if}
                <p class:unanswered={!answer.answer}>{answer.answer || 'No answer recorded'}</p>
                {#if answer.flags.length}<small>{answer.flags.join('; ')}</small>{/if}
              </div>
            {/each}
            {#each pageInfo.field_note_feedback as note (note.note_number)}
              <div class="page-evidence-item">
                <strong>Field note {note.note_number}</strong>
                {#if note.text}<p>{note.text}</p>{/if}
                <div class="note-feedback">
                  {#each ['helpful', 'confusing', 'incorrect'] as field (field)}
                    <span class:marked={note[field as 'helpful' | 'confusing' | 'incorrect'] === true}>{field}: {note[field as 'helpful' | 'confusing' | 'incorrect'] === true ? 'marked' : note[field as 'helpful' | 'confusing' | 'incorrect'] === false ? 'no' : 'blank'}</span>
                  {/each}
                </div>
                {#if note.handwritten_notes}<p>{note.handwritten_notes}</p>{/if}
                {#if note.flags.length}<small>{note.flags.join('; ')}</small>{/if}
              </div>
            {/each}
            {#if pageInfo.other_handwriting}<div class="page-evidence-item"><strong>Other handwriting</strong><p>{pageInfo.other_handwriting}</p></div>{/if}
          </details>
        {/if}
        {#if pageImageSource}
          <div class="document-stage">
            <div class="context-image" bind:this={documentElement} style:width={`${zoom * 100}%`}>
              <img src={imageUrl(pageImageSource)} alt={`Page ${activePage}`} />
              {#each pageRows as row (row.key)}
                <button
                  type="button"
                  class="row-overlay"
                  class:active={row.key === current?.key}
                  class:review={flagsFor(row).length > 0}
                  class:done={Boolean(decisions[row.key])}
                  style={boxStyle(row)}
                  aria-label={`Select ${row.source_id_text}`}
                  onmouseenter={() => (hoveredKey = row.key)}
                  onmouseleave={() => (hoveredKey = '')}
                  onclick={(event) => selectRowFromPage(row, event)}
                ></button>
              {/each}
              {#if overlayRow && overlayRow.row_box && usableColumns(overlayRow).length}
                <div class="synthetic-row" style={syntheticRowStyle(overlayRow)}>
                  {#each usableColumns(overlayRow) as column (column.index)}
                    <span class={`col-${column.name}`}>{columnValue(overlayRow, column.name)}</span>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </section>

      <aside class="inspector">
        <div class="inspector-scroll">
          {#if current}
            <div class="identity">
              <span>Page {current.source_page} · row {current.source_row_label} · {current.section.replaceAll('_', ' ')}</span>
              <h2>{current.plot}/{current.tree_number || 'unknown'} <em>stem {current.trunk_number || '?'}</em></h2>
              <p>{current.genus} {current.spp}</p>
              {#if current.identity_source}<small>{current.identity_source.replaceAll('_', ' ')}</small>{/if}
            </div>

            <div class="review-callout">
              <strong>Review because</strong>
              <div class="flags">
                {#each flagsFor(current) as flag (flag)}
                  <span>{formatFlag(flag)}</span>
                {:else}
                  <span>Selected from page</span>
                {/each}
              </div>
            </div>

            <section class="field-section">
              <div class="section-heading">
                <h3>Transcribed values</h3>
                {#if draftChangedCount}<span>{draftChangedCount} changed</span>{/if}
              </div>
              <div class="fields">
                {#each editableFieldsFor(current) as field (field)}
                  <button
                    class:active={selectedField === field}
                    class:dirty={fieldIsDirty(field)}
                    onclick={() => chooseField(field)}
                  >
                    <span>{fieldLabel(field)}</span>
                    <strong>{draftValue(field) || 'blank'}</strong>
                  </button>
                {/each}
              </div>
            </section>

            <section class="field-editor">
              <div class="section-heading">
                <h3>Edit {fieldLabel(selectedField as EditableField)}</h3>
                {#if fieldIsDirty(selectedField)}<span>modified</span>{/if}
              </div>
              {#if isNotesField}
                <div class="note-review">
                  <p class:blank={!current.notes}>{current.notes || 'No note extracted'}</p>
                  <label class="edit-box">
                    <span>Corrected note</span>
                    <textarea value={selectedDraftValue()} rows="3" oninput={handleDraftInput}></textarea>
                  </label>
                  <button class="clear-value" type="button" onclick={() => setDraftValue(selectedField, '')}>
                    <X size={14} /> Clear
                  </button>
                </div>
              {:else if isChoiceField}
                <div class="choices">
                  {#each fieldChoices as choice (`${selectedField}-${choice.value}`)}
                    <button class:chosen={selectedDraftValue() === choice.value} onclick={() => setDraftValue(selectedField, choice.value)}>
                      <strong>{choiceLabel(choice)}</strong>
                    </button>
                  {/each}
                </div>
              {:else}
                <label class="edit-box compact-edit">
                  <span>Corrected value</span>
                  <input value={selectedDraftValue()} oninput={handleDraftInput} />
                </label>
              {/if}
            </section>

            <details class="reviewer-note">
              <summary>Add reviewer note</summary>
              <textarea bind:value={note} rows="3" aria-label="Reviewer note"></textarea>
            </details>
          {:else}
            <div class="identity empty-selection">
              <span>Page {activePage}</span>
              <h2>No row selected</h2>
              <p>Choose a queue item or a row on the sheet.</p>
            </div>
          {/if}

          <details class="decision-log" aria-label="decision log">
            <summary><History size={15} /> Decision history <span>{decisionHistory.length}</span></summary>
            <div class="decision-log-body">
              <label class="decision-search">
                <Search size={14} />
                <input bind:value={decisionSearch} aria-label="Search decisions" placeholder="Search decisions" />
              </label>
              <div class="decision-items">
                {#each visibleDecisions as decision (decision)}
                  {@const row = rowForDecision(decision)}
                  <article class="decision-item">
                    <button
                      type="button"
                      class="decision-main"
                      onclick={() => selectRow(row)}
                      disabled={!row}
                      title={row ? `Select ${row.source_id_text}` : decision.key}
                    >
                      <span>{row ? `P${row.source_page} R${row.source_row_label}` : decision.key}</span>
                      <strong>{row?.source_id_text ?? decision.key}</strong>
                      <em>{decision.action} {decisionValue(decision)}</em>
                    </button>
                    <button type="button" class="decision-delete" onclick={() => deleteDecision(decision)} title="Delete decision">
                      <Trash2 size={15} />
                    </button>
                  </article>
                {:else}
                  <p class="decision-empty">{decisionHistory.length ? 'No decisions match.' : 'No decisions yet.'}</p>
                {/each}
              </div>
            </div>
          </details>
        </div>

        <footer class="review-footer">
          <div class="review-status">
            {#if draftChangedCount > 0}
              <span class="unsaved">Unsaved changes</span>
            {:else if status}
              <span>{status}</span>
            {:else if currentDecision}
              <span>Saved · {currentDecision.action}</span>
            {:else}
              <span>{current ? 'Ready for decision' : 'Select a row to begin'}</span>
            {/if}
          </div>
          <div class="actions">
            <button class="icon-action" type="button" onclick={() => go(-1)} disabled={index === 0 || total === 0} title="Previous row">
              <ChevronLeft size={18} />
            </button>
            <button
              type="button"
              class="accept"
              onclick={acceptRow}
              disabled={!current || draftChangedCount > 0}
              title={draftChangedCount > 0 ? 'Save row edits first' : 'Mark row OK as is'}
            >
              <Check size={17} /> OK as is
            </button>
            <button type="button" class="edit" onclick={saveRowEdits} disabled={!current || draftChangedCount === 0}>
              <Edit3 size={17} /> Save
            </button>
            <button type="button" class="skip" onclick={skipRow} disabled={!current} title="Skip row">
              <SkipForward size={17} />
            </button>
            <button class="icon-action" type="button" onclick={() => go(1)} disabled={index === total - 1 || total === 0} title="Next row">
              <ChevronRight size={18} />
            </button>
          </div>
        </footer>
      </aside>
    </section>
  {:else}
    <section class="empty">
      <h2>No review rows found</h2>
      <p>Run the transcription pipeline and make sure a review_rows.csv file exists.</p>
    </section>
  {/if}
</main>

<style>
  .shell {
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr;
    color: #17201a;
  }

  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 16px 20px;
    border-bottom: 1px solid #d8ded2;
    background: #ffffff;
  }

  .topbar > div:first-child {
    min-width: 0;
  }

  h1,
  h2,
  p {
    margin: 0;
  }

  h1 {
    font-size: 18px;
    font-weight: 760;
  }

  .progress {
    display: flex;
    align-items: baseline;
    gap: 8px;
    color: #5a6757;
    white-space: nowrap;
  }

  .progress strong {
    color: #17201a;
    font-size: 22px;
  }

  .workspace {
    min-height: 0;
    display: grid;
    grid-template-columns: 250px minmax(0, 1fr) minmax(320px, 360px);
    width: 100%;
    overflow: hidden;
  }

  .queue {
    min-height: 0;
    overflow: auto;
    border-right: 1px solid #d8ded2;
    background: #edf1e9;
    padding: 10px;
  }

  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #d8ded2;
  }

  .flag-filter {
    min-height: 28px;
    padding: 0 8px;
    border: 1px solid #b9c5b1;
    border-radius: 999px;
    background: #ffffff;
    color: #33402f;
    font-size: 11px;
  }

  .flag-filter.off {
    border-color: #cfd8ca;
    background: transparent;
    color: #7b8677;
    text-decoration: line-through;
  }

  .queue-row {
    width: 100%;
    min-height: 56px;
    display: grid;
    gap: 3px;
    margin-bottom: 6px;
    padding: 9px 10px;
    border: 1px solid transparent;
    border-radius: 7px;
    background: transparent;
    color: #293326;
    text-align: left;
  }

  .queue-row:hover,
  .queue-row.active {
    background: #ffffff;
    border-color: #b7c4af;
  }

  .queue-row.done {
    box-shadow: inset 3px 0 0 #4d7f52;
  }

  .queue span {
    color: #667262;
    font-size: 12px;
  }

  .queue strong {
    font-size: 13px;
  }

  .queue-empty {
    padding: 10px 2px;
    color: #6f7a6a;
    font-size: 12px;
  }

  .viewer {
    min-width: 0;
    min-height: 0;
    padding: 16px;
    overflow: auto;
  }

  .page-tools {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }

  .page-tools button {
    width: 30px;
    height: 30px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #cbd5c5;
    border-radius: 7px;
    background: #f8faf6;
    color: #1f2a1c;
  }

  .page-tools strong {
    font-size: 13px;
  }

  .page-tools span {
    color: #667262;
    font-size: 12px;
  }

  .page-metadata {
    display: grid;
    gap: 6px;
    margin-bottom: 10px;
    padding: 9px 10px;
    border: 1px solid #d5dccf;
    border-radius: 7px;
    background: #f8faf6;
    color: #34402f;
    font-size: 12px;
  }

  .page-evidence { margin-bottom: 10px; padding-inline: 12px; border-block: 1px solid #cbd5c5; font-size: 13px; }
  .page-evidence summary { cursor: pointer; padding: 10px 0; font-weight: 600; }
  .page-evidence[open] { max-height: 45vh; overflow: auto; }
  .page-evidence-item { padding: 10px 0; border-top: 1px solid #e0e4de; }
  .page-evidence-item p { margin: 5px 0; white-space: pre-wrap; overflow-wrap: anywhere; }
  .page-evidence-item small, .unanswered { color: #667262; }
  .note-feedback { display: flex; flex-wrap: wrap; gap: 12px; color: #667262; }
  .note-feedback .marked { color: #215b39; font-weight: 600; }

  .context-image {
    position: relative;
    min-width: 0;
    overflow: auto;
    border: 1px solid #cad2c4;
    border-radius: 7px;
    background: #ffffff;
  }

  .context-image img {
    width: 100%;
    min-width: 0;
    display: block;
  }

  .row-overlay {
    position: absolute;
    z-index: 2;
    border: 1px solid rgba(82, 108, 79, 0.18);
    background: rgba(94, 142, 88, 0.08);
    border-radius: 2px;
    padding: 0;
  }

  .row-overlay.review {
    border: 2px solid rgba(142, 108, 36, 0.9);
    background: rgba(238, 188, 75, 0.24);
  }

  .row-overlay:hover,
  .row-overlay.active {
    border-color: rgba(70, 119, 73, 0.95);
    background: rgba(94, 142, 88, 0.34);
  }

  .row-overlay.done {
    border-color: rgba(54, 115, 145, 0.95);
    background: rgba(90, 151, 184, 0.22);
  }

  .synthetic-row {
    position: absolute;
    z-index: 4;
    display: grid;
    border: 1px solid rgba(54, 93, 57, 0.88);
    background: rgba(255, 255, 255, 0.94);
    box-shadow: 0 5px 16px rgba(29, 37, 25, 0.22);
    pointer-events: none;
    font-size: 10px;
    line-height: 1.05;
    font-weight: 700;
    color: #17201a;
  }

  .synthetic-row span {
    min-width: 0;
    display: flex;
    align-items: center;
    overflow: hidden;
    padding: 0 3px;
    border-right: 1px solid rgba(92, 111, 84, 0.38);
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .synthetic-row span:last-child {
    border-right: 0;
  }

  .synthetic-row .col-id_text {
    font-size: 9px;
  }

  .synthetic-row .col-dbh_mm,
  .synthetic-row .col-health,
  .synthetic-row .col-standing,
  .synthetic-row .col-poison_ivy {
    justify-content: center;
  }

  .synthetic-row .col-notes {
    color: #765016;
    font-weight: 650;
  }

  .inspector {
    min-height: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-left: 1px solid #d8ded2;
    background: #ffffff;
    padding: 16px;
  }

  .inspector > :not(.decision-log) {
    flex: 0 0 auto;
  }

  .identity {
    display: grid;
    gap: 4px;
  }

  .identity span,
  .identity p {
    color: #667262;
    font-size: 12px;
  }

  .identity h2 {
    font-size: 20px;
  }

  .identity small {
    color: #778171;
    font-size: 11px;
    text-transform: uppercase;
  }

  .flags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 14px 0;
  }

  .flags span {
    padding: 4px 7px;
    border-radius: 6px;
    background: #f3ead8;
    color: #694d1f;
    font-size: 12px;
  }

  .fields,
  .choices {
    display: grid;
    gap: 8px;
  }

  .fields {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .fields button,
  .choices button {
    min-height: 44px;
    border: 1px solid #ced8c8;
    border-radius: 7px;
    background: #f8faf6;
    color: #1f2a1c;
  }

  .fields button {
    display: grid;
    gap: 4px;
    padding: 8px;
    text-align: left;
  }

  .fields strong {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .fields button.active,
  .choices button.chosen {
    border-color: #537b55;
    background: #e8f1e3;
  }

  .fields button.dirty {
    border-color: #a9792a;
    background: #fbf4df;
    box-shadow: inset 3px 0 0 #c5963f;
  }

  .fields span {
    color: #667262;
    font-size: 12px;
  }

  .choices {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin-top: 14px;
  }

  .choices button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px;
  }

  .choices strong {
    font-size: 13px;
    font-weight: 720;
  }

  .note-review {
    display: grid;
    gap: 8px;
    margin-top: 14px;
  }

  .note-review p {
    min-height: 76px;
    max-height: 150px;
    overflow: auto;
    margin: 0;
    padding: 10px;
    border: 1px solid #ced8c8;
    border-radius: 7px;
    background: #fbfcfa;
    color: #17201a;
    font-size: 13px;
    line-height: 1.35;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  .note-review p.blank {
    color: #7b8677;
  }

  .note-review button {
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 0 10px;
    border: 1px solid #ced8c8;
    border-radius: 7px;
    background: #f8faf6;
    color: #1f2a1c;
  }

  .edit-box {
    display: grid;
    gap: 6px;
    margin-top: 14px;
    color: #667262;
    font-size: 12px;
  }

  input,
  textarea {
    width: 100%;
    border: 1px solid #ced8c8;
    border-radius: 7px;
    padding: 9px 10px;
    color: #17201a;
    background: #fbfcfa;
    font: inherit;
    line-height: 1.35;
  }

  textarea {
    min-height: 76px;
    max-height: 180px;
    resize: vertical;
  }

  .actions {
    display: flex;
    flex-wrap: nowrap;
    gap: 6px;
    margin-top: 16px;
  }

  .actions button {
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    padding: 0 8px;
    border: 1px solid #cbd5c5;
    border-radius: 7px;
    background: #f8faf6;
    color: #1f2a1c;
    font-size: 12px;
    white-space: nowrap;
  }

  .actions button:disabled {
    opacity: 0.52;
    cursor: default;
  }

  .actions button:first-child,
  .actions button:last-child {
    flex: 0 0 36px;
    padding: 0;
  }

  .actions .accept {
    flex: 1 1 86px;
    background: #fbf0cf;
    border-color: #d2a743;
    color: #563f0f;
  }

  .actions .edit {
    flex: 1 1 76px;
    background: #e7edf4;
    border-color: #8ba7c3;
  }

  .saved {
    margin-top: 12px;
    color: #537b55;
    font-size: 13px;
  }

  .decision-log {
    min-height: 0;
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid #d8ded2;
  }

  .decision-log-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
  }

  .decision-search {
    display: grid;
    gap: 5px;
    margin-bottom: 8px;
    color: #667262;
    font-size: 11px;
  }

  .decision-search input {
    min-height: 32px;
    padding: 7px 9px;
    font-size: 12px;
  }

  .decision-items {
    min-height: 0;
    display: grid;
    align-content: start;
    gap: 6px;
    overflow-y: auto;
    padding-right: 2px;
  }

  .decision-item {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 32px;
    gap: 6px;
  }

  .decision-main,
  .decision-delete {
    border: 1px solid #ced8c8;
    border-radius: 7px;
    background: #f8faf6;
    color: #1f2a1c;
  }

  .decision-main {
    min-width: 0;
    min-height: 48px;
    display: grid;
    gap: 2px;
    padding: 7px 9px;
    text-align: left;
  }

  .decision-main span,
  .decision-main em,
  .decision-empty {
    color: #667262;
    font-size: 11px;
  }

  .decision-main strong,
  .decision-main em {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .decision-main strong {
    font-size: 12px;
  }

  .decision-main em {
    font-style: normal;
  }

  .decision-delete {
    width: 32px;
    min-height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #8b3f38;
  }

  .decision-delete:hover {
    border-color: #b7655d;
    background: #fbefed;
  }

  .empty {
    padding: 32px;
  }

  @media (max-width: 1100px) {
    .workspace {
      grid-template-columns: 190px minmax(0, 1fr);
    }

    .inspector {
      grid-column: 1 / -1;
      border-left: 0;
      border-top: 1px solid #d8ded2;
    }
  }

  @media (max-width: 700px) {
    .topbar {
      width: 100vw;
      align-items: flex-start;
      flex-direction: column;
      gap: 10px;
    }

    .workspace {
      width: 100vw;
      display: block;
    }

    .queue {
      width: 100vw;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      border-right: 0;
      border-bottom: 1px solid #d8ded2;
    }

    .filters {
      flex: 0 0 180px;
      align-content: flex-start;
      margin-bottom: 0;
      padding-bottom: 0;
      border-bottom: 0;
    }

    .queue-row {
      flex: 0 0 160px;
      margin-bottom: 0;
    }

    .viewer {
      width: 100vw;
      padding: 12px;
    }

    .inspector {
      width: 100vw;
      padding: 14px;
    }
  }

  /* Keep the review loop visible as three independently scrolling work areas. */
  .shell {
    height: 100dvh;
    min-height: 640px;
    overflow: hidden;
    background: #ecefeb;
  }

  .topbar {
    min-height: 58px;
    padding: 10px 16px;
    border-color: #d9deda;
    box-shadow: 0 1px 0 rgba(31, 38, 33, 0.03);
  }

  .run-title {
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .run-title h1 {
    font-size: 17px;
    letter-spacing: 0;
  }

  .run-title > span {
    max-width: 360px;
    overflow: hidden;
    padding: 4px 7px;
    border: 1px solid #d8ddd9;
    border-radius: 5px;
    background: #f5f6f4;
    color: #657068;
    font-size: 11px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .progress {
    min-width: 190px;
    display: grid;
    gap: 5px;
  }

  .progress > div:first-child {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 5px;
  }

  .progress strong {
    font-size: 16px;
  }

  .progress span {
    font-size: 11px;
  }

  .progress-track {
    width: 100%;
    height: 4px;
    overflow: hidden;
    border-radius: 2px;
    background: #e4e8e4;
  }

  .progress-track span {
    height: 100%;
    display: block;
    background: #39734f;
    transition: width 180ms ease;
  }

  .workspace {
    height: 100%;
    grid-template-columns: 220px minmax(420px, 1fr) 360px;
    background: #ecefeb;
  }

  .queue {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
    border-color: #d6dcd7;
    background: #f6f7f5;
  }

  .queue-header {
    flex: 0 0 auto;
    display: grid;
    gap: 9px;
    padding: 13px 11px 10px;
    border-bottom: 1px solid #dfe3df;
    background: #fbfcfb;
  }

  .queue-heading,
  .queue-heading > div {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 7px;
  }

  .queue-heading > div {
    min-width: 0;
    justify-content: flex-start;
  }

  .queue-heading h2 {
    margin: 0;
    font-size: 13px;
  }

  .queue-heading span,
  .queue-position {
    color: #6f7872;
    font-size: 10px;
    white-space: nowrap;
  }

  .queue-search,
  .decision-search {
    min-height: 32px;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 8px;
    border: 1px solid #cfd6d0;
    border-radius: 6px;
    background: #ffffff;
    color: #778078;
  }

  .queue-modes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding: 2px;
    border: 1px solid #d5dbd6;
    border-radius: 6px;
    background: #eef1ee;
  }

  .queue-modes button {
    min-width: 0;
    min-height: 27px;
    padding: 0 5px;
    border: 0;
    border-radius: 4px;
    background: transparent;
    color: #626d65;
    font-size: 10px;
    white-space: nowrap;
  }

  .queue-modes button.active {
    background: #ffffff;
    color: #253029;
    box-shadow: 0 1px 3px rgba(30, 39, 33, 0.12);
    font-weight: 650;
  }

  .queue-modes span {
    color: #7a847d;
  }

  .queue-search:focus-within,
  .decision-search:focus-within {
    border-color: #55826a;
    box-shadow: 0 0 0 2px rgba(73, 123, 94, 0.12);
  }

  .queue-search input,
  .decision-search input {
    min-width: 0;
    min-height: 0;
    flex: 1;
    padding: 0;
    border: 0;
    border-radius: 0;
    outline: 0;
    background: transparent;
    font-size: 11px;
  }

  .queue-search button {
    width: 22px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    border: 0;
    background: transparent;
    color: #69736b;
  }

  .filter-panel,
  .reviewer-note,
  .decision-log {
    margin: 0;
  }

  .filter-panel summary,
  .reviewer-note summary,
  .decision-log summary {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #5d6860;
    cursor: pointer;
    font-size: 11px;
    list-style: none;
  }

  .filter-panel summary::-webkit-details-marker,
  .reviewer-note summary::-webkit-details-marker,
  .decision-log summary::-webkit-details-marker {
    display: none;
  }

  .filters {
    margin: 8px 0 0;
    padding: 0;
    border: 0;
  }

  .flag-filter {
    min-height: 25px;
    padding: 0 7px;
    border-radius: 6px;
    font-size: 10px;
  }

  .queue-items {
    min-height: 0;
    flex: 1 1 auto;
    overflow-y: auto;
    padding: 6px;
  }

  .queue-row {
    min-height: 66px;
    gap: 4px;
    margin: 0 0 3px;
    padding: 9px;
    border-radius: 6px;
    color: #253029;
  }

  .queue-row:hover {
    border-color: #d6ddd7;
    background: #ffffff;
  }

  .queue-row.active {
    border-color: #5b8168;
    background: #ffffff;
    box-shadow: inset 3px 0 0 #3d7452;
  }

  .queue-row.done:not(.active) {
    opacity: 0.64;
    box-shadow: inset 3px 0 0 #7aa087;
  }

  .queue-identity {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 6px;
  }

  .queue-identity strong {
    color: #202a23;
    font-size: 13px;
  }

  .queue-identity em {
    color: #69746c;
    font-size: 10px;
    font-style: normal;
    white-space: nowrap;
  }

  .queue-context {
    overflow: hidden;
    color: #69746c;
    font-size: 10px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .queue-reason {
    width: fit-content;
    max-width: 100%;
    overflow: hidden;
    padding: 2px 5px;
    border-radius: 4px;
    background: #f4ead7;
    color: #71501d;
    font-size: 9px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .viewer {
    position: relative;
    padding: 0;
    background: #e9ece9;
    scrollbar-gutter: stable;
  }

  .page-tools {
    position: sticky;
    z-index: 12;
    top: 0;
    min-height: 48px;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 12px;
    margin: 0;
    padding: 8px 12px;
    border-bottom: 1px solid #d2d8d3;
    background: rgba(250, 251, 250, 0.96);
    backdrop-filter: blur(8px);
  }

  .page-nav,
  .zoom-tools,
  .page-summary {
    display: flex;
    align-items: center;
    gap: 7px;
  }

  .page-tools button {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: #ffffff;
  }

  .page-nav strong,
  .page-summary strong {
    font-size: 12px;
  }

  .page-nav span,
  .page-summary span,
  .zoom-tools span {
    color: #6b756e;
    font-size: 10px;
  }

  .page-summary {
    min-width: 0;
    justify-content: center;
    overflow: hidden;
  }

  .page-summary span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .zoom-tools span {
    width: 32px;
    text-align: center;
  }

  .page-alert {
    position: sticky;
    z-index: 11;
    top: 48px;
    display: flex;
    gap: 14px;
    padding: 7px 13px;
    border-bottom: 1px solid #dfd3b9;
    background: #fff7e7;
    color: #654b20;
    font-size: 10px;
  }

  .document-stage {
    min-width: 100%;
    padding: 18px;
  }

  .context-image {
    min-width: 540px;
    margin: 0 auto;
    overflow: visible;
    border-color: #c7cdc8;
    border-radius: 3px;
    box-shadow: 0 3px 14px rgba(34, 41, 36, 0.12);
    transform-origin: top center;
  }

  .row-overlay.review {
    border-color: rgba(177, 127, 28, 0.92);
    background: rgba(238, 183, 67, 0.16);
  }

  .row-overlay:hover,
  .row-overlay.active {
    border-color: #2f7650;
    background: rgba(64, 143, 92, 0.25);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.9);
  }

  .synthetic-row {
    border-color: #2e6846;
    box-shadow: 0 4px 13px rgba(29, 37, 31, 0.2);
  }

  .inspector {
    height: 100%;
    padding: 0;
    border-color: #d6dcd7;
    background: #ffffff;
  }

  .inspector-scroll {
    min-height: 0;
    flex: 1 1 auto;
    overflow-y: auto;
    padding: 15px 15px 20px;
  }

  .identity {
    gap: 3px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e1e5e2;
  }

  .identity > span {
    color: #778078;
    font-size: 10px;
    text-transform: uppercase;
  }

  .identity h2 {
    font-size: 19px;
    letter-spacing: 0;
  }

  .identity h2 em {
    color: #6c766f;
    font-size: 13px;
    font-style: normal;
    font-weight: 560;
  }

  .identity p {
    color: #4d5951;
    font-size: 12px;
  }

  .identity small {
    margin-top: 2px;
    font-size: 9px;
  }

  .review-callout {
    display: grid;
    gap: 6px;
    margin: 12px 0 14px;
    padding: 9px 10px;
    border-left: 3px solid #c28c2c;
    background: #fff8e9;
  }

  .review-callout > strong {
    color: #64491c;
    font-size: 10px;
    text-transform: uppercase;
  }

  .flags {
    margin: 0;
  }

  .flags span {
    padding: 0;
    background: transparent;
    color: #60481f;
    font-size: 11px;
  }

  .flags span:not(:last-child)::after {
    content: ' ·';
    color: #a18657;
  }

  .field-section,
  .field-editor {
    display: grid;
    gap: 8px;
  }

  .field-editor {
    margin-top: 14px;
    padding-top: 13px;
    border-top: 1px solid #e1e5e2;
  }

  .section-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
  }

  .section-heading h3 {
    margin: 0;
    color: #303a33;
    font-size: 11px;
    text-transform: uppercase;
  }

  .section-heading span {
    color: #9a681a;
    font-size: 10px;
  }

  .fields {
    gap: 6px;
  }

  .fields button {
    min-height: 50px;
    gap: 2px;
    padding: 7px 8px;
    border-radius: 6px;
    background: #f8f9f8;
  }

  .fields span {
    font-size: 10px;
  }

  .fields strong {
    font-size: 13px;
  }

  .fields button.active {
    border-color: #4f7f63;
    background: #edf5f0;
    box-shadow: inset 3px 0 0 #39734f;
  }

  .choices {
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 5px;
    margin: 0;
  }

  .choices button {
    min-height: 34px;
    padding: 5px 3px;
    border-radius: 5px;
    background: #f7f9f7;
  }

  .choices button.chosen {
    border-color: #4f7f63;
    background: #e5f0e9;
  }

  .note-review {
    margin: 0;
  }

  .note-review p {
    min-height: 0;
    max-height: 90px;
    padding: 8px;
    border-radius: 6px;
    font-size: 11px;
  }

  .edit-box {
    margin-top: 8px;
    font-size: 10px;
  }

  .edit-box input,
  .edit-box textarea,
  .reviewer-note textarea {
    border-radius: 6px;
    font-size: 12px;
  }

  .compact-edit {
    margin: 0;
  }

  .note-review .clear-value {
    min-height: 28px;
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-top: 7px;
    padding: 0 8px;
    border: 1px solid #d3d9d4;
    border-radius: 5px;
    background: #f7f8f7;
    color: #4d5850;
    font-size: 10px;
  }

  .reviewer-note {
    margin-top: 15px;
    padding-top: 13px;
    border-top: 1px solid #e1e5e2;
  }

  .reviewer-note textarea {
    min-height: 64px;
    margin-top: 8px;
  }

  .decision-log {
    margin-top: 15px;
    padding-top: 13px;
    border-top: 1px solid #e1e5e2;
  }

  .decision-log summary span {
    margin-left: auto;
    color: #7a837c;
  }

  .decision-log-body {
    display: grid;
    gap: 8px;
    margin-top: 9px;
  }

  .decision-items {
    max-height: 220px;
  }

  .decision-main,
  .decision-delete {
    border-radius: 6px;
  }

  .review-footer {
    flex: 0 0 auto;
    padding: 8px 10px 10px;
    border-top: 1px solid #d6dcd7;
    background: #fbfcfb;
    box-shadow: 0 -4px 12px rgba(32, 40, 34, 0.05);
  }

  .review-status {
    min-height: 20px;
    display: flex;
    align-items: center;
    padding: 0 2px;
    color: #647068;
    font-size: 10px;
  }

  .review-status .unsaved {
    color: #9a681a;
    font-weight: 650;
  }

  .actions {
    gap: 5px;
    margin: 0;
  }

  .actions button {
    min-height: 34px;
    padding: 0 8px;
    border-radius: 6px;
    font-size: 11px;
  }

  .actions .icon-action,
  .actions .skip {
    width: 34px;
    flex: 0 0 34px;
    padding: 0;
  }

  .actions .accept {
    flex: 1 1 auto;
    border-color: #59806a;
    background: #e8f2ec;
    color: #27513a;
  }

  .actions .edit {
    flex: 1 1 auto;
    border-color: #6989a7;
    background: #e9f0f6;
    color: #2d506e;
  }

  .actions .skip {
    color: #6c756f;
  }

  .empty-selection {
    border: 0;
  }

  @media (max-width: 1050px) {
    .workspace {
      grid-template-columns: 190px minmax(360px, 1fr) 330px;
    }

    .page-summary span:nth-last-child(-n + 2) {
      display: none;
    }
  }

  @media (max-width: 850px) {
    .shell {
      height: auto;
      min-height: 100dvh;
      overflow: visible;
    }

    .topbar {
      width: auto;
      align-items: center;
      flex-direction: row;
      gap: 24px;
    }

    .workspace {
      height: auto;
      grid-template-columns: 190px minmax(0, 1fr);
      overflow: visible;
    }

    .queue {
      width: auto;
      height: 68dvh;
      display: flex;
      flex-direction: column;
      gap: 0;
      overflow: hidden;
      border-right: 1px solid #d6dcd7;
      border-bottom: 0;
    }

    .queue-row {
      flex: initial;
      margin: 0 0 3px;
    }

    .viewer {
      width: auto;
      height: 68dvh;
      padding: 0;
    }

    .inspector {
      width: auto;
      grid-column: 1 / -1;
      height: auto;
      min-height: 520px;
      padding: 0;
      border-top: 1px solid #d6dcd7;
      border-left: 0;
    }

    .inspector-scroll {
      overflow: visible;
    }

    .review-footer {
      position: sticky;
      bottom: 0;
    }
  }

  @media (max-width: 620px) {
    .topbar {
      align-items: stretch;
    }

    .run-title {
      align-items: flex-start;
      flex-direction: column;
    }

    .progress {
      min-width: 0;
    }

    .workspace {
      display: block;
    }

    .queue {
      width: 100%;
      height: 260px;
      display: flex;
      border-bottom: 1px solid #d6dcd7;
    }

    .queue-items {
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: 180px;
      overflow-x: auto;
      overflow-y: hidden;
    }

    .queue-row {
      margin: 0 3px 0 0;
    }

    .viewer {
      width: 100%;
      height: 62dvh;
    }

    .page-tools {
      grid-template-columns: auto 1fr;
    }

    .page-summary {
      display: none;
    }

    .zoom-tools {
      justify-self: end;
    }

    .document-stage {
      padding: 10px;
    }

    .inspector {
      width: 100%;
    }
  }
</style>
