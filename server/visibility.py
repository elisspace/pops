#!/usr/bin/env python3
"""Private Unix HTTP visibility service (Python standard library only).

SECURITY BOUNDARY: Caddy is the sole frontend and MUST authenticate /admin*
AND /api/admin/* with its existing basicauth/basic_auth. This service does not
handle passwords or cookies. X-Pops-Admin is a CSRF intent header, NOT auth.
Never expose this socket via an unauthenticated proxy or TCP bridge. Run as a
single unprivileged service process, with a private runtime directory and trusted
Caddy service group; the socket is 0660. Set the service's effective group or a
setgid runtime directory so Caddy owns the socket group. The state directory must
be outside Git, owned by the service and not group writable.
Only one process may own a state directory (enforced with flock on Linux).

Responses never contain paths, exception details, credentials, or request bodies.
No CORS, static files, forwarding headers, or arbitrary filesystem routes exist.
"""
import argparse
import collections
import fcntl
import http.server
import json
import os
from pathlib import Path
import signal
import socketserver
import stat
import tempfile
import threading
import time
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

PROPERTIES = ('b', 'barn', 'cottage', 'cotton', 'd', 'e', 'firethorn',
              'rocksprings-a', 'rocksprings-b', 'shankle')
MAX_BODY = 1024
MAX_STATE = 4096
REQUEST_TIMEOUT = 5.0
MAX_CONNECTIONS = 8
WRITE_LIMIT = 60


def decode_json(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate key')
            obj[key] = value
        return obj
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def valid_state(value):
    return (type(value) is dict and set(value) == {'revision', 'visibility'}
            and type(value['revision']) is int and 0 <= value['revision'] <= 2**53 - 1
            and type(value['visibility']) is dict
            and set(value['visibility']) == set(PROPERTIES)
            and all(type(v) is bool for v in value['visibility'].values()))


def validate_origin(origin):
    parts = urlsplit(origin)
    if (parts.scheme != 'https' or not parts.hostname or parts.username is not None
            or parts.password is not None or parts.path or parts.query or parts.fragment
            or parts.netloc != parts.netloc.lower() or origin != 'https://' + parts.netloc
            or any(c.isspace() or ord(c) < 33 for c in origin)):
        raise ValueError('origin must be a canonical HTTPS origin without a trailing slash')
    # Force port validation as urlsplit defers it.
    _ = parts.port
    return origin


class State:
    def __init__(self, directory):
        self.lock = threading.Lock()
        self.writes = collections.deque(maxlen=WRITE_LIMIT)
        self.directory = Path(directory)
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = self.directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()
                or info.st_mode & 0o022):
            raise ValueError('unsafe state directory')
        self.lock_fd = os.open(self.directory / 'visibility.lock',
                               os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.path = self.directory / 'visibility.json'
            try:
                fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            except FileNotFoundError:
                self.value = {'revision': 0, 'visibility': {
                    key: key in ('firethorn', 'rocksprings-b') for key in PROPERTIES}}
                self.persist(self.value)
            else:
                with os.fdopen(fd, 'rb') as source:
                    if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                        raise ValueError('invalid state')
                    raw = source.read(MAX_STATE + 1)
                if len(raw) > MAX_STATE:
                    raise ValueError('invalid state')
                self.value = decode_json(raw)
                if not valid_state(self.value):
                    raise ValueError('invalid state')
        except BaseException:
            os.close(self.lock_fd)
            raise

    def close(self):
        os.close(self.lock_fd)

    def persist(self, value):
        fd, name = tempfile.mkstemp(prefix='.visibility-', dir=self.directory)
        try:
            with os.fdopen(fd, 'wb') as target:
                target.write(json.dumps(value, separators=(',', ':')).encode('ascii'))
                target.flush()
                os.fsync(target.fileno())
            os.replace(name, self.path)
            directory_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def snapshot(self):
        with self.lock:
            if getattr(self, 'unavailable', False):
                return 503, {'error': 'state unavailable'}
            return 200, {'revision': self.value['revision'],
                         'visibility': dict(self.value['visibility'])}

    def update(self, update):
        with self.lock:
            if getattr(self, 'unavailable', False):
                return 503, {'error': 'state unavailable'}
            now = time.monotonic()
            while self.writes and self.writes[0] <= now - 60:
                self.writes.popleft()
            if len(self.writes) >= WRITE_LIMIT:
                return 429, {'error': 'write rate exceeded'}
            # Limit valid write attempts, including revision conflicts and I/O errors.
            self.writes.append(now)
            if update['revision'] != self.value['revision']:
                return 409, self.value
            if self.value['revision'] == 2**53 - 1:
                return 503, {'error': 'state unavailable'}
            value = {'revision': self.value['revision'] + 1,
                     'visibility': dict(self.value['visibility'])}
            value['visibility'][update['property']] = update['visible']
            try:
                self.persist(value)
            except OSError:
                # A directory fsync failure may follow a successful replace. Stop
                # accepting updates until restart verifies the on-disk state.
                self.unavailable = True
                return 503, {'error': 'state unavailable'}
            self.value = value
            return 200, value


class Handler(http.server.BaseHTTPRequestHandler):
    if TYPE_CHECKING:
        server: 'Server'  # type: ignore[assignment]  # This handler is Unix-only.
    protocol_version = 'HTTP/1.0'
    server_version = 'Pops'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(self.server.request_timeout)

    def handle(self):
        try:
            super().handle()
        except (TimeoutError, OSError, ValueError):
            pass

    def log_message(self, format, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self.respond(code, {'error': 'request rejected'})

    def respond(self, status, value):
        body = json.dumps(value, separators=(',', ':')).encode('ascii')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'")
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Connection', 'close')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)
        self.close_connection = True

    def parse_request(self):
        if not super().parse_request():
            return False
        # BaseHTTPRequestHandler normalizes //foo to /foo. Our route contract
        # must compare the original target, not a normalized alias.
        self.path = self.requestline.split()[1]
        if self.headers.get_all('Transfer-Encoding') is not None:
            self.respond(400, {'error': 'invalid framing'})
            return False
        # Reject duplicates for ALL headers; avoid proxy/parser disagreement.
        names = [key.lower() for key in self.headers.keys()]
        if len(names) != len(set(names)):
            self.respond(400, {'error': 'duplicate headers'})
            return False
        if self.headers.get('Expect') is not None:
            self.respond(400, {'error': 'invalid framing'})
            return False
        if self.headers.get('Content-Length') is not None:
            length = self.headers['Content-Length']
            if not length.isascii() or not length.isdecimal() or len(length) > 10:
                self.respond(400, {'error': 'invalid length'})
                return False
            if int(length) > MAX_BODY:
                self.respond(413, {'error': 'body too large'})
                return False
        return True

    def do_GET(self):
        if self.path != '/api/visibility':
            return self.respond(404, {'error': 'not found'})
        if int(self.headers.get('Content-Length', '0')):
            return self.respond(400, {'error': 'unexpected body'})
        status, result = self.server.state.snapshot()
        self.respond(status, result)

    def do_PUT(self):
        if self.path != '/api/admin/visibility':
            return self.respond(404, {'error': 'not found'})
        if (self.headers.get('Origin') != self.server.origin
                or self.headers.get('X-Pops-Admin') != '1'):
            return self.respond(403, {'error': 'origin or intent rejected'})
        if self.headers.get('Content-Type', '').strip().lower() != 'application/json':
            return self.respond(415, {'error': 'JSON required'})
        length = self.headers.get('Content-Length')
        if length is None or int(length) == 0:
            return self.respond(400, {'error': 'body required'})
        try:
            raw = self.rfile.read(int(length))
            if len(raw) != int(length):
                raise ValueError('truncated')
            value = decode_json(raw.decode('utf-8'))
            if (type(value) is not dict or set(value) != {'revision', 'property', 'visible'}
                    or type(value['revision']) is not int
                    or not 0 <= value['revision'] <= 2**53 - 1
                    or type(value['property']) is not str
                    or value['property'] not in PROPERTIES
                    or type(value['visible']) is not bool):
                raise ValueError('invalid update')
        except (ValueError, UnicodeError, RecursionError):
            return self.respond(400, {'error': 'invalid JSON update'})
        except TimeoutError:
            return self.respond(400, {'error': 'incomplete body'})
        if getattr(self.server.state, 'unavailable', False):
            return self.respond(503, {'error': 'state unavailable'})
        status, result = self.server.state.update(value)
        self.respond(status, result)


class Server(socketserver.ThreadingUnixStreamServer):
    """Bounded workers; absolute per-connection deadline includes headers/body."""
    daemon_threads = False
    block_on_close = True
    request_queue_size = MAX_CONNECTIONS

    def __init__(self, path, state_dir, origin, *, request_timeout=REQUEST_TIMEOUT):
        self.origin = validate_origin(origin)
        self.request_timeout = request_timeout
        self.slots = threading.BoundedSemaphore(MAX_CONNECTIONS)
        self.state = State(state_dir)
        self.socket_path = os.fspath(path)
        self.bound = False
        try:
            # Refuse existing paths, including stale sockets. systemd runtime
            # cleanup or an operator must explicitly remove a stale socket.
            super().__init__(self.socket_path, Handler, bind_and_activate=False)
            self.server_bind()
            self.bound = True
            os.chmod(self.socket_path, 0o660)
            self.server_activate()
        except BaseException:
            self.server_close()
            raise

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        # Closing the socket at an absolute deadline prevents trickle clients
        # from extending the inactivity timeout indefinitely.
        timer = threading.Timer(self.request_timeout, self.expire, args=(request,))
        timer.daemon = True
        timer.start()
        self.timers[request.fileno()] = timer
        try:
            super().process_request(request, client_address)
        except BaseException:
            timer.cancel()
            self.timers.pop(request.fileno(), None)
            self.slots.release()
            raise

    @staticmethod
    def expire(request):
        import socket
        try:
            request.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def process_request_thread(self, request, client_address):
        timer = self.timers.pop(request.fileno())
        try:
            super().process_request_thread(request, client_address)
        finally:
            timer.cancel()
            self.slots.release()

    def server_bind(self):
        self.timers = {}
        super().server_bind()

    def handle_error(self, request, client_address):
        pass  # No request data or filesystem paths in logs.

    def server_close(self):
        try:
            super().server_close()
        finally:
            if self.bound:
                os.unlink(self.socket_path)
                self.bound = False
            self.state.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--socket', required=True, help='private Unix socket path')
    parser.add_argument('--state-dir', required=True, help='persistent directory outside Git')
    parser.add_argument('--origin', required=True, help='canonical HTTPS origin, no trailing slash')
    args = parser.parse_args()
    try:
        server = Server(args.socket, args.state_dir, args.origin)
    except (OSError, ValueError, RecursionError):
        parser.exit(1, 'visibility: startup refused (check private state and runtime configuration)\n')
    # Signal handler must not call shutdown() in the serve_forever thread.
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
