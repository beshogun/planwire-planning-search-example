import { pathToFileURL } from 'node:url';

export async function searchCouncil({ key, council = 'richmond-thames', limit = 5, fetchImpl = fetch }) {
  if (typeof key !== 'string' || !key.trim() || /[\r\n]/.test(key)) throw new Error('Set PLANWIRE_API_KEY to your API key.');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(council)) throw new Error('Use a council ID from the PlanWire coverage directory.');
  if (!Number.isInteger(limit) || limit < 1 || limit > 5) throw new Error('This evaluation example supports limits from 1 to 5.');
  const url = new URL('https://api.planwire.io/v1/applications');
  url.search = new URLSearchParams({ council, limit: String(limit) }).toString();
  let response;
  try {
    response = await fetchImpl(url, {
      headers: { 'X-API-Key': key.trim(), Accept: 'application/json' },
      signal: AbortSignal.timeout(15_000),
      redirect: 'error',
    });
  } catch {
    throw new Error('Request failed or timed out. Check connectivity before retrying.');
  }
  if (!response.ok) {
    const advice = response.status === 401 ? 'Check your API key.'
      : response.status === 429 ? 'Wait before retrying and check your allowance.'
      : response.status === 403 ? 'Check the coverage and access included in your plan.'
      : 'Check the API status and request parameters.';
    throw new Error(`PlanWire returned HTTP ${response.status}. ${advice}`);
  }
  let body;
  try { body = await response.json(); } catch { throw new Error('Expected a JSON response.'); }
  if (!body || !Array.isArray(body.data)) throw new Error('Expected a response with a data array.');
  return body;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const response = await searchCouncil({ key: process.env.PLANWIRE_API_KEY, council: process.argv[2] || 'richmond-thames' });
    console.log(JSON.stringify(response, null, 2));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
