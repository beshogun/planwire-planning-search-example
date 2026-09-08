import { test } from 'node:test';
import assert from 'node:assert/strict';
import { searchCouncil } from './search.mjs';

test('uses a server-side header, bounded request and source-linked response', async () => {
  const fixture = {data: [{reference: 'EXAMPLE/26', url: 'https://example.invalid/planning/26'}], meta: {total: null}};
  const result = await searchCouncil({key: 'test-not-a-real-key', fetchImpl: async (url, options) => {
    assert.equal(url.origin, 'https://api.planwire.io');
    assert.equal(url.searchParams.get('council'), 'richmond-thames');
    assert.equal(url.searchParams.get('limit'), '5');
    assert.equal(url.toString().includes('test-not-a-real-key'), false);
    assert.equal(options.headers['X-API-Key'], 'test-not-a-real-key');
    assert.equal(options.redirect, 'error');
    assert.ok(options.signal instanceof AbortSignal);
    return Response.json(fixture);
  }});
  assert.deepEqual(result, fixture);
});
test('a successful empty sample is not a request failure', async () => {
  assert.deepEqual(await searchCouncil({key:'test',fetchImpl:async()=>Response.json({data:[]})}),{data:[]});
});
for (const status of [401,403,429,500]) test(`handles HTTP ${status} without leaking response text or credentials`, async()=>{
  await assert.rejects(searchCouncil({key:'secret-fixture',fetchImpl:async()=>new Response('secret-fixture',{status})}), e => e.message.includes(String(status)) && !e.message.includes('secret-fixture'));
});
test('rejects missing credentials before sending', async()=>{
  await assert.rejects(searchCouncil({key:'',fetchImpl:()=>{throw new Error('must not send')}}),/PLANWIRE_API_KEY/);
});
test('rejects invalid councils and unsafe limits', async()=>{
  await assert.rejects(searchCouncil({key:'test',council:'x&limit=100'}),/council ID/);
  await assert.rejects(searchCouncil({key:'test',limit:100}),/1 to 5/);
});
test('handles transport and malformed response errors', async()=>{
  await assert.rejects(searchCouncil({key:'test',fetchImpl:async()=>{throw new Error('secret transport details')}}),/failed or timed out/);
  await assert.rejects(searchCouncil({key:'test',fetchImpl:async()=>new Response('not json')}),/JSON/);
  await assert.rejects(searchCouncil({key:'test',fetchImpl:async()=>Response.json({error:'bad'})}),/data array/);
});
