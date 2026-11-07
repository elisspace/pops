"""Real Unix HTTP integration tests; no external dependencies."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def test_cli_exposes_only_explicit_unix_configuration(self):
        result = subprocess.run([sys.executable, str(ROOT / 'server/visibility.py'), '--help'],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        for option in ('--socket', '--state-dir', '--origin'):
            self.assertIn(option, result.stdout)
        self.assertNotIn('--port', result.stdout)


import concurrent.futures
import importlib.util
import json
import os
import socket
import stat
import tempfile
import threading
import time
from unittest.mock import patch
from typing import Any

spec = importlib.util.spec_from_file_location('visibility', ROOT / 'server/visibility.py')
assert spec is not None and spec.loader is not None
visibility = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visibility)
ORIGIN = 'https://rentals.example.test'
KEYS = {'b', 'barn', 'cottage', 'cotton', 'd', 'e', 'firethorn',
        'rocksprings-a', 'rocksprings-b', 'shankle'}


class UnixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.root = Path(self.temp.name)
        self.path = self.root / 'http.sock'
        self.directory = self.root / 'state'
        self.start()

    def start(self):
        self.server = visibility.Server(self.path, self.directory, ORIGIN, request_timeout=0.4)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.01})
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)
        self.assertFalse(self.thread.is_alive())

    def tearDown(self):
        self.stop()
        self.temp.cleanup()

    def raw(self, request, half_close=False) -> tuple[int, Any]:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2)
            client.connect(str(self.path))
            client.sendall(request)
            if half_close:
                client.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                block = client.recv(8192)
                if not block:
                    break
                chunks.append(block)
        response = b''.join(chunks)
        head, body = response.split(b'\r\n\r\n', 1)
        status = int(head.split(b' ', 2)[1])
        headers = dict(line.lower().split(b': ', 1) for line in head.split(b'\r\n')[1:])
        self.assertEqual(headers[b'cache-control'], b'no-store')
        self.assertEqual(headers[b'x-content-type-options'], b'nosniff')
        self.assertIn(b'content-security-policy', headers)
        self.assertNotIn(b'access-control-allow-origin', headers)
        self.assertNotIn(str(self.root).encode(), response)
        return status, json.loads(body) if body else None

    def request(self, method='GET', path='/api/visibility', value=None, headers=None):
        body = b'' if value is None else json.dumps(value).encode()
        fields = {'Host': 'rentals.example.test', 'Content-Length': str(len(body))}
        if method == 'PUT':
            fields.update({'Origin': ORIGIN, 'Content-Type': 'application/json', 'X-Pops-Admin': '1'})
        for key, val in (headers or {}).items():
            if val is None:
                fields.pop(key, None)
            else:
                fields[key] = val
        wire = f'{method} {path} HTTP/1.1\r\n'.encode()
        wire += ''.join(f'{k}: {v}\r\n' for k, v in fields.items()).encode() + b'\r\n' + body
        return self.raw(wire)

    def put(self, revision=0, property='b', visible=True, **kwargs):
        return self.request('PUT', '/api/admin/visibility',
                            {'revision': revision, 'property': property, 'visible': visible}, **kwargs)

    def test_fresh_defaults_are_persisted_and_socket_is_private(self):
        status, data = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(data['revision'], 0)
        self.assertEqual(set(data['visibility']), KEYS)
        self.assertEqual({k for k, v in data['visibility'].items() if v},
                         {'firethorn', 'rocksprings-b'})
        self.assertTrue(all(type(v) is bool for v in data['visibility'].values()))
        self.assertEqual(json.loads((self.directory / 'visibility.json').read_text()), data)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o660)
        self.assertEqual(self.server.socket.family, socket.AF_UNIX)

    def test_persistence_restart_and_stale_revision(self):
        self.assertEqual(self.put()[0], 200)
        self.stop()
        self.start()
        status, data = self.request()
        self.assertEqual((status, data['revision'], data['visibility']['b']), (200, 1, True))
        status, stale = self.put(property='barn')
        self.assertEqual((status, stale), (409, data))
        self.assertEqual(self.put(1, 'barn')[1]['revision'], 2)

    def test_concurrent_writes_have_one_winner(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda _: self.put(), range(6)))
        self.assertEqual(sorted(status for status, _ in results), [200] + [409] * 5)
        self.assertEqual(self.request()[1]['revision'], 1)

    def test_csrf_checks_and_media_type_do_not_write(self):
        for headers, expected in [({'Origin': None}, 403), ({'Origin': 'null'}, 403),
                                  ({'Origin': 'https://evil.test'}, 403),
                                  ({'Origin': ORIGIN + '/'}, 403),
                                  ({'X-Pops-Admin': None}, 403),
                                  ({'X-Pops-Admin': '0'}, 403),
                                  ({'Content-Type': 'text/plain'}, 415),
                                  ({'Content-Type': None}, 415)]:
            with self.subTest(headers=headers):
                self.assertEqual(self.put(headers=headers)[0], expected)
        self.assertEqual(self.request()[1]['revision'], 0)

    def test_strict_schema_and_injection_inputs(self):
        good = {'revision': 0, 'property': 'b', 'visible': True}
        bad = [[], None, {}, dict(good, extra='x'), dict(good, revision=True),
               dict(good, revision=-1), dict(good, revision=0.0),
               dict(good, visible=1), dict(good, visible='true'),
               dict(good, property=[]), dict(good, property='../visibility.json'),
               dict(good, property='<script>alert(1)</script>'),
               dict(good, property="b'; DROP TABLE visibility;--"),
               dict(good, property='$(touch /tmp/pwned)'), dict(good, property='unknown')]
        before = (self.directory / 'visibility.json').read_bytes()
        for value in bad:
            with self.subTest(value=value):
                self.assertEqual(self.request('PUT', '/api/admin/visibility', value)[0], 400)
        self.assertEqual((self.directory / 'visibility.json').read_bytes(), before)

    def test_framing_and_duplicate_json_are_rejected(self):
        prefix = (f'PUT /api/admin/visibility HTTP/1.1\r\nOrigin: {ORIGIN}\r\n'
                  'X-Pops-Admin: 1\r\nContent-Type: application/json\r\n').encode()
        cases = [(b'Content-Length: 1025\r\n\r\n', 413),
                 (b'Content-Length: -1\r\n\r\n', 400),
                 (b'Content-Length: +1\r\n\r\n', 400),
                 (b'Content-Length: 1,1\r\n\r\n', 400),
                 (b'Content-Length: 2\r\nContent-Length: 2\r\n\r\n{}', 400),
                 (b'Origin: https://evil.test\r\nContent-Length: 2\r\n\r\n{}', 400),
                 (b'Expect: 100-continue\r\nContent-Length: 2\r\n\r\n{}', 400),
                 (b'Transfer-Encoding: chunked\r\n\r\n0\r\n\r\n', 400),
                 (b'Content-Length: 100\r\n\r\n{}', 400),
                 (b'\r\n', 400)]
        for tail, expected in cases:
            with self.subTest(tail=tail):
                self.assertEqual(self.raw(prefix + tail, half_close=True)[0], expected)
        body = b'{"revision":0,"property":"b","visible":true,"visible":false}'
        self.assertEqual(self.raw(prefix + f'Content-Length: {len(body)}\r\n\r\n'.encode() + body)[0], 400)
        self.assertEqual(self.request()[1]['revision'], 0)

    def test_fixed_routes_methods_and_no_files(self):
        for method, path in [('POST', '/api/admin/visibility'), ('DELETE', '/api/visibility'),
                             ('OPTIONS', '/api/visibility'), ('HEAD', '/api/visibility'),
                             ('GET', '/api/admin/visibility'), ('GET', '/visibility.json'),
                             ('GET', '//api/visibility'),
                             ('GET', '/api/visibility?x=1'), ('GET', '/../server/visibility.py'),
                             ('PUT', '/api/admin/visibility/../x')]:
            with self.subTest(method=method, path=path):
                self.assertIn(self.request(method, path)[0], (404, 405, 501))

    def test_rate_limit_is_bounded(self):
        for revision in range(60):
            self.assertEqual(self.put(revision)[0], 200)
        self.assertEqual(self.put(60)[0], 429)
        self.assertEqual(self.request()[1]['revision'], 60)
        self.assertEqual(len(self.server.state.writes), 60)

    def test_worker_bound_and_absolute_deadline(self):
        clients = []
        try:
            for _ in range(visibility.MAX_CONNECTIONS):
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.settimeout(2)
                client.connect(str(self.path))
                client.sendall(b'GET /api/visibility HTTP/1.1\r\nX-Slow: ')
                clients.append(client)
            time.sleep(0.08)
            self.assertEqual(self.server.slots._value, 0)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as excess:
                excess.settimeout(1)
                excess.connect(str(self.path))
                self.assertEqual(excess.recv(1), b'')
            time.sleep(0.5)
            self.assertEqual(self.server.slots._value, visibility.MAX_CONNECTIONS)
            self.assertEqual(self.request()[0], 200)
        finally:
            for client in clients:
                client.close()

    def test_trickle_header_cannot_extend_absolute_deadline(self):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(1)
            client.connect(str(self.path))
            client.sendall(b'GET /api/visibility HTTP/1.1\r\nX-Slow: ')
            for _ in range(3):
                time.sleep(0.1)
                client.sendall(b'x')
            time.sleep(0.2)
            self.assertEqual(client.recv(1), b'')
        self.assertEqual(self.request()[1]['revision'], 0)

    def test_corrupt_state_fails_closed_without_overwrite(self):
        self.stop()
        target = self.directory / 'visibility.json'
        valid = target.read_bytes()
        for raw in (b'{broken', b'{}', b'{"revision":true,"visibility":{}}',
                    b'x' * 4097):
            target.write_bytes(raw)
            with self.assertRaises((ValueError, OSError)):
                visibility.Server(self.path, self.directory, ORIGIN)
            self.assertEqual(target.read_bytes(), raw)
            self.assertFalse(self.path.exists())
        target.write_bytes(valid)
        self.start()

    def test_second_process_state_owner_is_refused(self):
        with self.assertRaises(OSError):
            visibility.Server(self.root / 'other.sock', self.directory, ORIGIN)
        self.assertEqual(self.request()[0], 200)

    def test_noncanonical_origin_is_refused_before_initialization(self):
        for origin in ('http://rentals.example.test', ORIGIN + '/', ORIGIN + '/path',
                       'https://user:pass@rentals.example.test', 'null',
                       ORIGIN + '?query=1', ORIGIN + ':invalid'):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                visibility.Server(self.root / 'unused.sock', self.root / 'unused', origin)
        self.assertFalse((self.root / 'unused').exists())

    def test_existing_socket_is_never_silently_unlinked(self):
        with self.assertRaises(OSError):
            visibility.Server(self.path, self.root / 'other-state', ORIGIN)
        self.assertEqual(self.request()[0], 200)

    def test_cli_runs_real_unix_http_and_cleans_up_on_sigterm(self):
        self.stop()
        child = subprocess.Popen([sys.executable, str(ROOT / 'server/visibility.py'),
                                  '--socket', str(self.path), '--state-dir', str(self.directory),
                                  '--origin', ORIGIN], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 3
            while not self.path.exists() and time.monotonic() < deadline:
                if child.poll() is not None:
                    self.fail('CLI exited before socket creation')
                time.sleep(0.01)
            self.assertEqual(self.request()[0], 200)
        finally:
            child.terminate()
            stdout, stderr = child.communicate(timeout=7)
            self.assertEqual((child.returncode, stdout, stderr), (0, b'', b''))
            self.assertFalse(self.path.exists())
            self.start()

    def test_get_queued_behind_failed_write_does_not_publish_stale_state(self):
        state = self.server.state
        self.server.request_timeout = 2
        persisted = threading.Event()
        get_queued = threading.Event()
        release_write = threading.Event()
        persist = state.persist
        snapshot = state.snapshot

        def fail_after_replace(value):
            persist(value)
            persisted.set()
            if not release_write.wait(1):
                raise AssertionError('GET did not reach the snapshot boundary')
            raise OSError('controlled post-replace failure')

        def queued_snapshot():
            get_queued.set()
            return snapshot()

        with patch.object(state, 'persist', side_effect=fail_after_replace), \
                patch.object(state, 'snapshot', side_effect=queued_snapshot), \
                concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            writer = pool.submit(self.put)
            self.assertTrue(persisted.wait(1))
            reader = pool.submit(self.request)
            try:
                self.assertTrue(get_queued.wait(1))
            finally:
                release_write.set()
            self.assertEqual(writer.result()[0], 503)
            self.assertEqual(reader.result()[0], 503)
        self.assertEqual(json.loads((self.directory / 'visibility.json').read_text())['revision'], 1)

    def test_persistence_failure_stops_queued_updates(self):
        state = self.server.state
        with patch.object(state, 'persist', side_effect=OSError('private path')):
            self.assertEqual(self.put()[0], 503)
        self.assertEqual(self.request()[0], 503)
        # A handler may already have passed its availability check and be waiting
        # on State.lock when the first persistence fails. State must recheck.
        self.assertEqual(state.update({'revision': 0, 'property': 'b', 'visible': True})[0], 503)


if __name__ == '__main__':
    unittest.main()
