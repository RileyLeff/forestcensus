import { error } from '@sveltejs/kit';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { getRepoRoot, isAllowedImagePath } from '$lib/server/review-data';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
  const imagePath = url.searchParams.get('path');
  if (!imagePath || !isAllowedImagePath(imagePath)) {
    throw error(400, 'Image path is not allowed');
  }

  const resolved = path.resolve(getRepoRoot(), imagePath);
  const bytes = await readFile(resolved);
  return new Response(new Uint8Array(bytes), {
    headers: {
      'content-type': contentType(resolved),
      'cache-control': 'no-store'
    }
  });
};

function contentType(filePath: string) {
  if (filePath.endsWith('.jpg') || filePath.endsWith('.jpeg')) return 'image/jpeg';
  if (filePath.endsWith('.webp')) return 'image/webp';
  return 'image/png';
}
