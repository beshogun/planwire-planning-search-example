"""One bounded PlanWire council search. Python 3.10+, standard library only."""

import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def search_council(key, council="richmond-thames", limit=5, *, opener=None):
    if not isinstance(key, str) or not key.strip() or any(ord(c) < 32 or ord(c) > 126 for c in key):
        raise ValueError("Set PLANWIRE_API_KEY to your API key.")
    if not isinstance(council, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", council):
        raise ValueError("Use a council ID from the PlanWire coverage directory.")
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError("This evaluation example supports limits from 1 to 5.")
    url = "https://api.planwire.io/v1/applications?" + urlencode({"council": council, "limit": limit})
    request = Request(url, headers={"X-API-Key": key.strip(), "Accept": "application/json"})
    client = opener if opener is not None else build_opener(NoRedirects())
    try:
        with client.open(request, timeout=15) as response:
            # Bound memory use even if an upstream returns an unexpectedly large body.
            raw = response.read(2_000_001)
    except HTTPError as error:
        advice = {401: "Check your API key.", 403: "Check the access included in your plan.",
                  429: "Wait before retrying and check your allowance."}.get(
                      error.code, "Check the API status and request parameters. Redirects are not followed.")
        raise RuntimeError(f"PlanWire returned HTTP {error.code}. {advice}") from None
    except (URLError, OSError, TimeoutError):
        raise RuntimeError("Request failed or timed out. Check connectivity before retrying.") from None
    if len(raw) > 2_000_000:
        raise RuntimeError("Response exceeded this example's size limit.")
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeError):
        raise RuntimeError("Expected a JSON response.") from None
    if not isinstance(body, dict) or not isinstance(body.get("data"), list):
        raise RuntimeError("Expected a response with a data array.")
    return body


def main():
    try:
        result = search_council(os.environ.get("PLANWIRE_API_KEY"), sys.argv[1] if len(sys.argv) > 1 else "richmond-thames")
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
