// Minimal CodesJiema API client for Node.js 18+ (built-in fetch). Docs: https://codesjiema.com/apidoc
import { randomUUID } from 'node:crypto';

const BASE_URL = 'https://codesjiema.com';

export function createClient(apiKey = process.env.CODESJIEMA_API_KEY) {
  if (!apiKey) throw new Error('Set CODESJIEMA_API_KEY');
  async function call(method, path, params = {}) {
    for (let i = 0; i < 3; i++) {
      const url = new URL(BASE_URL + path);
      const init = { method, headers: { 'X-API-Key': apiKey } };
      if (method === 'GET') Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
      else {
        init.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        init.body = new URLSearchParams(params).toString();
      }
      const res = await fetch(url, init);
      if (res.status === 429) { await sleep(1000 * Number(res.headers.get('retry-after') || 5)); continue; }
      if (res.status === 401 || res.status === 403) throw new Error(`HTTP ${res.status}: check API key / access`);
      const body = await res.json();
      if (body.code !== 1) throw new Error(body.msg || 'request failed');
      return body.data || {};
    }
    throw new Error('too many requests');
  }
  return {
    get: (p, q) => call('GET', p, q),
    post: (p, d) => call('POST', p, d),
    newKey: () => randomUUID().replace(/-/g, ''), // reuse the same key when retrying a paid request
  };
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
