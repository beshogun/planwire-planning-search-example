import io
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

from search import NoRedirects, search_council, main


class SearchTests(unittest.TestCase):
    def client(self, body):
        client = Mock()
        client.open.return_value = io.BytesIO(body)
        return client

    def test_sample_and_empty_response(self):
        for data in [[], [{"id": "synthetic-record", "description": "Synthetic test only"}]]:
            body = {"data": data, "meta": {"total": len(data)}}
            client = self.client(json.dumps(body).encode())
            self.assertEqual(search_council("test-placeholder", opener=client), body)
            request = client.open.call_args.args[0]
            self.assertEqual(request.full_url, "https://api.planwire.io/v1/applications?council=richmond-thames&limit=5")
            self.assertEqual(request.get_header("X-api-key"), "test-placeholder")
            self.assertEqual(client.open.call_args.kwargs, {"timeout": 15})

    def test_invalid_inputs_never_send(self):
        for key, council, limit in [(None, "adur", 5), ("", "adur", 5), ("x\r\ny", "adur", 5),
                                    ("x", "../other", 5), ("x", "adur", 6), ("x", "adur", True)]:
            client = Mock()
            with self.assertRaises(ValueError):
                search_council(key, council, limit, opener=client)
            client.open.assert_not_called()

    def test_http_errors_do_not_expose_body_or_retry(self):
        for status in [301, 302, 307, 308, 401, 403, 429, 500]:
            client = Mock()
            client.open.side_effect = HTTPError("https://api.planwire.io", status, "private details", {}, io.BytesIO(b"secret"))
            with self.assertRaisesRegex(RuntimeError, f"HTTP {status}") as caught:
                search_council("test-placeholder", opener=client)
            self.assertNotIn("secret", str(caught.exception))
            self.assertNotIn("private details", str(caught.exception))
            client.open.assert_called_once()

    def test_transport_errors_are_sanitized(self):
        for error in [URLError("secret"), TimeoutError("secret"), OSError("secret")]:
            client = Mock()
            client.open.side_effect = error
            with self.assertRaisesRegex(RuntimeError, "Request failed or timed out"):
                search_council("test-placeholder", opener=client)

    def test_invalid_json_shape_and_size(self):
        for raw in [b"<html>private</html>", b"\xff", b"null", b"[]", b'{"data":{}}', b"x" * 2_000_001]:
            with self.assertRaises(RuntimeError):
                search_council("test-placeholder", opener=self.client(raw))

    def test_redirect_handler_refuses_credential_forwarding(self):
        request = Request("https://api.planwire.io/v1/applications", headers={"X-API-Key": "test-placeholder"})
        for status in [301, 302, 303, 307, 308]:
            self.assertIsNone(NoRedirects().redirect_request(request, None, status, "redirect", {}, "https://other.example/"))

    def test_default_opener_installs_redirect_guard(self):
        client = self.client(b'{"data":[]}')
        with patch("search.build_opener", return_value=client) as factory:
            search_council("test-placeholder")
        self.assertIsInstance(factory.call_args.args[0], NoRedirects)

    def test_cli_missing_key(self):
        with patch.dict("os.environ", {}, clear=True), patch("sys.argv", ["search.py"]), patch("sys.stderr", new_callable=io.StringIO) as stderr:
            self.assertEqual(main(), 1)
            self.assertIn("PLANWIRE_API_KEY", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
