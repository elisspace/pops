"""Availability sync tests: no credentials or external network required."""
import contextlib
from email.message import Message
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('airtable_sync', ROOT / 'server/airtable_sync.py')
assert spec is not None and spec.loader is not None
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
KEYS = {'b', 'barn', 'cottage', 'cotton', 'd', 'e', 'firethorn',
        'rocksprings-a', 'rocksprings-b', 'shankle'}
B = 'recNdTnB1NjQi0OJe'
BARN = 'rec5RF1bKiPp7R4Sz'
SECRET = 'test-token-not-real'
PRIVATE = 'private tenant details'


def record(identifier=B):
    return {'id': identifier, 'fields': {'Name': PRIVATE, 'Available': False}}


class Response(io.BytesIO):
    status = 200


class FakeAPI:
    def __init__(self, *pages):
        self.pages = list(pages)
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        page = self.pages.pop(0)
        if isinstance(page, Exception):
            raise page
        return Response(page if isinstance(page, bytes) else json.dumps(page).encode())


class CLITests(unittest.TestCase):
    def test_explicit_required_paths(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'server/airtable_sync.py'), '--help'],
            capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--token-file', result.stdout)
        self.assertIn('--output', result.stdout)
        result = subprocess.run([sys.executable, str(ROOT / 'server/airtable_sync.py')],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.token = self.root / 'token'
        self.token.write_text(SECRET + '\n')
        self.output = self.root / 'visibility.json'
        self.prior = b'{"prior":"unchanged"}\n'
        self.output.write_bytes(self.prior)

    def run_sync(self, *pages):
        api = FakeAPI(*pages)
        sync.synchronize(self.token, self.output, opener=api)
        return api

    def rejects(self, *pages):
        before = set(p.name for p in self.root.iterdir())
        with self.assertRaises(sync.SyncError) as caught:
            self.run_sync(*pages)
        self.assertEqual(self.output.read_bytes(), self.prior)
        self.assertEqual(set(p.name for p in self.root.iterdir()), before)
        for private in (SECRET, PRIVATE, 'https://'):
            self.assertNotIn(private, str(caught.exception))
        return str(caught.exception)

    def test_paginated_view_membership_and_public_only_output(self):
        with patch.object(sync.time, 'time', return_value=1780000000.9):
            api = self.run_sync({'records': [record()], 'offset': 'page / two'},
                                {'records': [record(BARN)]})
        result = json.loads(self.output.read_bytes())
        self.assertEqual(set(result), {'revision', 'visibility'})
        self.assertEqual(result['revision'], 1780000000)
        self.assertEqual(set(result['visibility']), KEYS)
        self.assertEqual({k for k, v in result['visibility'].items() if v}, {'b', 'barn'})
        self.assertTrue(all(type(v) is bool for v in result['visibility'].values()))
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o644)
        for request, timeout in api.calls:
            parts = urlsplit(request.full_url)
            self.assertEqual(parts.scheme, 'https')
            self.assertEqual(parts.netloc, 'api.airtable.com')
            self.assertEqual(parts.path, '/v0/appSUPtDVGlCyTitK/tblxo4bMBslwsHb6F')
            query = parse_qs(parts.query)
            self.assertEqual(query['view'], ['viwAl6iMsxqvAxg8w'])
            self.assertEqual(query['fields[]'], ['Name'])
            self.assertEqual(request.get_method(), 'GET')
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + SECRET)
            self.assertGreater(timeout, 0)
        self.assertEqual(parse_qs(urlsplit(api.calls[1][0].full_url).query)['offset'], ['page / two'])
        self.assertNotIn(PRIVATE, self.output.read_text())
        self.assertNotIn(B, self.output.read_text())
        self.assertNotIn(SECRET, self.output.read_text())

    def test_empty_view_hides_all(self):
        self.run_sync({'records': []})
        self.assertEqual(json.loads(self.output.read_text())['visibility'], dict.fromkeys(KEYS, False))

    def test_unknown_record_fails_even_when_available_field_false(self):
        message = self.rejects({'records': [record('recUnknown1234567')]})
        self.assertIn('recUnknown1234567', message)
        self.assertIn('mapping', message)

    def test_duplicate_records_and_offsets_fail(self):
        self.rejects({'records': [record(), record()]})
        self.rejects({'records': [record()], 'offset': 'next'}, {'records': [record()]})
        self.rejects({'records': [], 'offset': 'same'}, {'records': [], 'offset': 'same'})

    def test_malformed_shapes_and_json_fail(self):
        bad = [b'not JSON', b'{"records":[],"records":[]}', b'{"records":[],"x":NaN}',
               [], None, {}, {'records': {}}, {'records': [None]},
               {'records': [{'id': B}]}, {'records': [{'id': B, 'fields': []}]},
               {'records': [record('bad\n' + SECRET)]},
               {'records': [], 'offset': None}, {'records': [], 'offset': ''},
               {'records': [], 'offset': 123}, {'records': [], 'offset': 'a' * 1025}]
        for page in bad:
            with self.subTest(page=page):
                self.rejects(page)

    def test_network_errors_are_sanitized_and_keep_prior(self):
        for error in [HTTPError('https://example/' + SECRET, 403, PRIVATE, Message(), None),
                      URLError(PRIVATE + SECRET), TimeoutError(SECRET), OSError(PRIVATE)]:
            with self.subTest(error=type(error).__name__):
                self.rejects(error)

    def test_response_and_page_limits(self):
        self.rejects(b' ' * (sync.MAX_RESPONSE_BYTES + 1))
        self.rejects(*({'records': [], 'offset': str(i)} for i in range(sync.MAX_PAGES)))

    def test_last_allowed_page_can_complete(self):
        pages = [{'records': [], 'offset': str(i)} for i in range(sync.MAX_PAGES - 1)]
        pages.append({'records': [record()]})
        api = self.run_sync(*pages)
        self.assertEqual(len(api.calls), sync.MAX_PAGES)
        self.assertTrue(json.loads(self.output.read_text())['visibility']['b'])

    def test_all_fixed_mappings(self):
        expected = {
            'b': 'recNdTnB1NjQi0OJe', 'barn': 'rec5RF1bKiPp7R4Sz',
            'cottage': 'recpjSIpCvkwlLu60', 'cotton': 'recnijvpwH9xOh5hr',
            'd': 'rec1a390ovD9RiYEK', 'e': 'rechE31TjtFteoNdv',
            'firethorn': 'recOP3frAF52eE4rU', 'rocksprings-a': 'recyvJ0wnw2Xqo7R5',
            'rocksprings-b': 'rec49VNWOZN7kwzfM', 'shankle': 'recrlKjH402BT7VGg',
        }
        self.assertEqual(sync.RECORDS, expected)
        self.run_sync({'records': [record(value) for value in expected.values()]})
        self.assertEqual(json.loads(self.output.read_text())['visibility'], dict.fromkeys(KEYS, True))

    def test_total_deadline_before_request_and_during_read(self):
        for times in ([0, 121], [0, 0, 0, 121]):
            with self.subTest(times=times), patch.object(sync.time, 'monotonic', side_effect=times):
                message = self.rejects({'records': []})
                self.assertIn('time limit', message)

    def test_non_200_success_transport_is_rejected(self):
        class NotOK(FakeAPI):
            def open(self, request, timeout):
                response = Response(b'private body')
                response.status = 204
                return response
        with self.assertRaises(sync.SyncError):
            sync.synchronize(self.token, self.output, opener=NotOK())
        self.assertEqual(self.output.read_bytes(), self.prior)

    def test_directory_fsync_failure_reports_already_published(self):
        real_fsync = sync.os.fsync
        def fsync(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError(SECRET)
            real_fsync(fd)
        with patch.object(sync.os, 'fsync', side_effect=fsync):
            with self.assertRaisesRegex(sync.SyncError, 'published, but directory'):
                self.run_sync({'records': []})
        self.assertEqual(json.loads(self.output.read_text())['visibility'], dict.fromkeys(KEYS, False))

    def test_invalid_tokens_fail_without_network(self):
        for token in ('', 'a\nb', 'a\rb', 'a b', '\u2603', 'x' * 8193):
            self.token.write_text(token)
            api = FakeAPI({'records': []})
            with self.assertRaises(sync.SyncError):
                sync.synchronize(self.token, self.output, opener=api)
            self.assertEqual(api.calls, [])
            self.assertEqual(self.output.read_bytes(), self.prior)

    def test_missing_token_and_output_parent_fail_safely(self):
        self.token.unlink()
        self.rejects({'records': []})
        self.token.write_text(SECRET)
        with self.assertRaises(sync.SyncError):
            sync.synchronize(self.token, self.root / 'missing' / 'visibility.json',
                             opener=FakeAPI({'records': []}))

    def test_write_errors_before_replace_keep_prior_and_cleanup(self):
        for function in ('fsync', 'replace', 'fchmod'):
            with self.subTest(function=function), patch.object(sync.os, function, side_effect=OSError(SECRET)):
                self.rejects({'records': []})

    def test_file_fsync_replace_then_directory_fsync(self):
        events = []
        real_fsync, real_replace = sync.os.fsync, sync.os.replace
        def fsync(fd):
            events.append('directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file')
            real_fsync(fd)
        def replace(source, target):
            events.append('replace')
            self.assertEqual(Path(source).parent, self.output.parent)
            real_replace(source, target)
        with patch.object(sync.os, 'fsync', side_effect=fsync), patch.object(sync.os, 'replace', side_effect=replace):
            self.run_sync({'records': []})
        self.assertEqual(events, ['file', 'replace', 'directory'])

    def test_redirect_is_never_followed(self):
        handler = sync.NoRedirect()
        with self.assertRaises(sync.SyncError):
            handler.redirect_request(None, None, 302, 'found', {}, 'https://evil.test/')

    def test_default_transport_rejects_real_urllib_redirect_processing(self):
        calls = []
        class SyntheticHTTPS(BaseHandler):
            handler_order = 100
            def https_open(self, request):
                calls.append(request)
                headers = Message()
                headers['Location'] = 'https://evil.test/leak'
                response = addinfourl(io.BytesIO(b''), headers, request.full_url, 302)
                setattr(response, 'msg', 'Found')
                return response
        def factory(*handlers):
            return build_opener(*handlers, SyntheticHTTPS())
        with patch.object(sync, 'build_opener', side_effect=factory):
            with self.assertRaisesRegex(sync.SyncError, 'redirect refused'):
                sync.synchronize(self.token, self.output)
        self.assertEqual(len(calls), 1)
        self.assertEqual(urlsplit(calls[0].full_url).netloc, 'api.airtable.com')
        self.assertEqual(self.output.read_bytes(), self.prior)

    def test_cli_sanitizes_unexpected_errors(self):
        stderr = io.StringIO()
        with patch.object(sync, 'synchronize', side_effect=RuntimeError(SECRET + PRIVATE)), contextlib.redirect_stderr(stderr):
            result = sync.main(['--token-file', str(self.token), '--output', str(self.output)])
        self.assertEqual(result, 1)
        self.assertNotIn(SECRET, stderr.getvalue())
        self.assertNotIn(PRIVATE, stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
