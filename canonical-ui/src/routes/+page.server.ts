import { fail } from '@sveltejs/kit';
import { appendDecision, loadCanonicalData } from '$lib/server/canonical-data';

export function load({ url }) {
  return loadCanonicalData(url);
}

export const actions = {
  decide: async ({ request }) => {
    const data = await request.formData();
    const tree_uid = String(data.get('tree_uid') ?? '');
    const plot = String(data.get('plot') ?? '');
    const identity_tag = String(data.get('identity_tag') ?? '');
    const action_type = String(data.get('action_type') ?? '');
    if (!tree_uid || !plot || !identity_tag || !action_type) {
      return fail(400, { ok: false, message: 'Missing decision fields.' });
    }
    appendDecision({
      tree_uid,
      plot,
      identity_tag,
      action_type,
      target_identity: String(data.get('target_identity') ?? ''),
      target_taxon: String(data.get('target_taxon') ?? ''),
      note: String(data.get('note') ?? '')
    });
    return { ok: true };
  }
};
