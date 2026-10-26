import { fail } from '@sveltejs/kit';
import { appendDecision, loadReviewRows, removeDecision } from '$lib/server/review-data';
import type { Actions, PageServerLoad } from './$types';
import type { ReviewDecision } from '$lib/types';

export const load: PageServerLoad = async () => {
  return await loadReviewRows();
};

export const actions: Actions = {
  decide: async ({ request }) => {
    const form = await request.formData();
    const runDir = String(form.get('runDir') ?? '');
    const key = String(form.get('key') ?? '');
    const action = String(form.get('action') ?? '');
    const decidedAt = String(form.get('decided_at') ?? '') || new Date().toISOString();

    if (!runDir || !key || !['accept', 'edit', 'skip'].includes(action)) {
      return fail(400, { message: 'Missing decision fields' });
    }

    await appendDecision(runDir, {
      key,
      action: action as 'accept' | 'edit' | 'skip',
      chosen_field: String(form.get('chosen_field') ?? ''),
      chosen_value: String(form.get('chosen_value') ?? ''),
      note: String(form.get('note') ?? ''),
      decided_at: decidedAt
    });

    return { ok: true, key };
  },
  decideBatch: async ({ request }) => {
    const form = await request.formData();
    const runDir = String(form.get('runDir') ?? '');
    const decisionsText = String(form.get('decisions') ?? '');
    let decisions: ReviewDecision[];

    try {
      decisions = JSON.parse(decisionsText) as ReviewDecision[];
    } catch {
      return fail(400, { message: 'Malformed decisions' });
    }

    if (!runDir || !Array.isArray(decisions) || decisions.length === 0) {
      return fail(400, { message: 'Missing decision fields' });
    }

    for (const decision of decisions) {
      if (!decision.key || !decision.decided_at || !['accept', 'edit', 'skip'].includes(decision.action)) {
        return fail(400, { message: 'Missing decision fields' });
      }
    }

    for (const decision of decisions) {
      await appendDecision(decision.source_run_dir || runDir, decision);
    }

    return { ok: true, count: decisions.length };
  },
  deleteDecision: async ({ request }) => {
    const form = await request.formData();
    const runDir = String(form.get('runDir') ?? '');
    const key = String(form.get('key') ?? '');
    const decidedAt = String(form.get('decided_at') ?? '');

    if (!runDir || !key || !decidedAt) {
      return fail(400, { message: 'Missing decision fields' });
    }

    await removeDecision(runDir, {
      key, decided_at: decidedAt, chosen_field: String(form.get('chosen_field') ?? '')
    });

    return { ok: true, key };
  }
};
