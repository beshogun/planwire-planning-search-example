# PlanWire Planning Search Example

## Python and Postman

Python 3.10+ needs no dependencies. Set `PLANWIRE_API_KEY` in your local/server
environment, then run `python3 search.py richmond-thames`. Avoid pasting real keys
into shell history, source files or public workspaces. Run the synthetic tests
with `python3 -m unittest discover -p 'test_*.py'`.

The Python example makes one request, returns at most five records, rejects
redirects, uses a 15-second socket timeout and limits the response body to 2 MB.
It does not retry or paginate automatically. Keep returned data private unless
your licence permits sharing it. This is a reference example, not a maintained SDK.

[Read the Python tutorial](https://planwire.io/blog/search-uk-planning-applications-python).

Open the [public Postman collection](https://www.postman.com/bennroyys-team/planwire-uk-planning-api/collection/e8nwkju/planwire-uk-planning-api)
or import `planwire.postman_collection.json` into your own Postman workspace.
Set `apiKey` as a **local, unshared environment variable**, leaving its shared
value empty. Do not save real response examples to a public collection.
Set Postman's request timeout to 15000 ms and run requests individually.
Search and coverage accept sample keys; record lookup is subject to plan access.
For webhook recovery, supply an existing webhook ID owned by your paid key.
The collection does not create subscriptions, retry, paginate or update cursors.
Publish only this placeholder collection in a new dedicated public workspace,
never an existing private workspace containing credentials or internal work.

Next: [signed webhooks and durable recovery](https://planwire.io/planning-webhooks)
and the [monitoring-cache example](https://planwire.io/examples/monitoring-cache/README.md).

## Node.js

A small, dependency-free Node.js example for evaluating one council through the
[PlanWire planning applications API](https://planwire.io/planning-applications-api).
It makes one authenticated GET request and prints the JSON response, including
source links where supplied. It does not create a CRM, harvest contacts or send email.

## Run

Requires Node.js 22 or later. No package installation is needed.

1. Obtain a key at [PlanWire](https://planwire.io/#signup).
2. Set `PLANWIRE_API_KEY` in your local shell or secret manager. Never commit it,
   paste it into a public issue, or put it in browser JavaScript.
3. Run `node search.mjs richmond-thames`.

Choose another council ID from the [coverage directory](https://planwire.io/uk-planning-data).
The example returns at most five records. Free keys provide limited evaluation
samples, not proof of complete territory coverage. Responses and limits depend on
your plan. A successful empty array does not prove there are no applications.

## What To Inspect

- Compare references, source links and dates against known official records.
- Treat missing coordinates, decisions, UPRNs and documents as unavailable data,
  not as evidence that a condition is absent.
- Keep application dates separate from source-check dates and construction starts.
- Check the [response schema and pagination](https://planwire.io/docs#list-applications)
  before extending this one-request evaluation into an import job.
- Review [licence terms](https://planwire.io/terms) and plan limits before storing
  or redistributing data. This code's MIT licence does not license the API data.

## Test

Run `node --test search.test.mjs`. Tests use synthetic fixtures and make no network
requests. They cover authentication, bounded queries, empty results, HTTP failures,
invalid JSON and timeouts/transport failures. They do not establish live coverage.

The client has a 15-second timeout, does not follow redirects with credentials,
and does not print error response bodies. It makes no automatic retries or bulk
exports. Keep generated JSON private if your product's data terms require it.

## Integration Evidence

This is a PlanWire-maintained reference example, not a customer implementation or
a claim of measured customer results. Customer case studies require separate
permission and evidence.
