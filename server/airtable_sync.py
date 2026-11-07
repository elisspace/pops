#!/usr/bin/env python3
"""Publish public-safe visibility from a fixed, read-only Airtable view.

Only view membership matters. No field values are published or logged. The output
parent must already exist; keep it outside the checkout and expose only the JSON.
"""
import argparse
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT = 'https://api.airtable.com/v0/appSUPtDVGlCyTitK/tblxo4bMBslwsHb6F'
VIEW = 'viwAl6iMsxqvAxg8w'
RECORDS = {
    'b': 'recNdTnB1NjQi0OJe',
    'barn': 'rec5RF1bKiPp7R4Sz',
    'cottage': 'recpjSIpCvkwlLu60',
    'cotton': 'recnijvpwH9xOh5hr',
    'd': 'rec1a390ovD9RiYEK',
    'e': 'rechE31TjtFteoNdv',
    'firethorn': 'recOP3frAF52eE4rU',
    'rocksprings-a': 'recyvJ0wnw2Xqo7R5',
    'rocksprings-b': 'rec49VNWOZN7kwzfM',
    'shankle': 'recrlKjH402BT7VGg',
}
MAX_PAGES = 20
MAX_RESPONSE_BYTES = 256 * 1024
REQUEST_TIMEOUT = 10
TOTAL_TIMEOUT = 120
MAX_TOKEN_BYTES = 8192


class SyncError(Exception):
    """A fixed, public-safe diagnostic (never a remote exception or body)."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SyncError('Airtable redirect refused; check the fixed endpoint.')


def _token(path):
    try:
        with Path(path).open('rb') as source:
            raw = source.read(MAX_TOKEN_BYTES + 1)
        if len(raw) > MAX_TOKEN_BYTES:
            raise ValueError
        value = raw.decode('ascii').strip('\r\n')
        if not value or any(not 33 <= ord(char) <= 126 for char in value):
            raise ValueError
        return value
    except (OSError, ValueError):
        raise SyncError('Cannot read a valid token file; check the credential.') from None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError


def _check_deadline(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise SyncError('Airtable sync time limit exceeded; prior output retained.')
    return min(REQUEST_TIMEOUT, remaining)


def _page(opener, token, offset, deadline):
    params = [('view', VIEW), ('fields[]', 'Name'), ('pageSize', '100')]
    if offset is not None:
        params.append(('offset', offset))
    request = Request(ENDPOINT + '?' + urlencode(params), method='GET', headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'Accept-Encoding': 'identity',
    })
    try:
        with opener.open(request, timeout=_check_deadline(deadline)) as response:
            if response.status != 200:
                raise SyncError('Airtable returned a non-200 response; prior output retained.')
            data = bytearray()
            while True:
                _check_deadline(deadline)
                # HTTPResponse.read1 performs at most one underlying read, so
                # slow trickles cannot indefinitely bypass the total deadline.
                block = response.read1(min(65536, MAX_RESPONSE_BYTES + 1 - len(data)))
                if not block:
                    break
                data.extend(block)
                if len(data) > MAX_RESPONSE_BYTES:
                    raise SyncError('Airtable response size limit exceeded; prior output retained.')
            _check_deadline(deadline)
        page = json.loads(data.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=_invalid_constant)
    except HTTPError as error:
        error.close()
        raise SyncError('Airtable HTTP request failed; check PAT read access and view configuration.') from None
    except (URLError, OSError, http.client.HTTPException):
        raise SyncError('Airtable network request failed; prior output retained.') from None
    except (ValueError, RecursionError):
        raise SyncError('Malformed Airtable JSON; prior output retained.') from None
    if not isinstance(page, dict) or not isinstance(page.get('records'), list):
        raise SyncError('Malformed Airtable records; prior output retained.')
    if 'offset' in page and (not isinstance(page['offset'], str)
                             or not 1 <= len(page['offset']) <= 1024):
        raise SyncError('Malformed Airtable pagination; prior output retained.')
    return page


def _visibility(token, opener):
    deadline = time.monotonic() + TOTAL_TIMEOUT
    seen, offsets = set(), set()
    known = set(RECORDS.values())
    offset = None
    for _ in range(MAX_PAGES):
        page = _page(opener, token, offset, deadline)
        for record in page['records']:
            if (not isinstance(record, dict) or not isinstance(record.get('id'), str)
                    or re.fullmatch(r'rec[A-Za-z0-9]{14}', record['id']) is None
                    or not isinstance(record.get('fields'), dict)):
                raise SyncError('Malformed Airtable record; prior output retained.')
            identifier = record['id']
            if identifier in seen:
                raise SyncError('Duplicate Airtable record; prior output retained.')
            if identifier not in known:
                raise SyncError('Unknown Airtable record ' + identifier
                                + '; add an explicit unit mapping before retrying. Prior output retained.')
            seen.add(identifier)
        if 'offset' not in page:
            return {key: identifier in seen for key, identifier in RECORDS.items()}
        offset = page['offset']
        if offset in offsets:
            raise SyncError('Repeated Airtable pagination offset; prior output retained.')
        offsets.add(offset)
    raise SyncError('Airtable page limit exceeded; prior output retained.')


def _publish(output, visibility):
    """Same-directory replace; failures before replace leave the old file intact.

    A directory-fsync error after replace cannot undo publication and is reported
    distinctly. Do not roll back with a second, non-atomic write.
    """
    output = Path(output)
    temporary = None
    directory = None
    replaced = False
    try:
        payload = (json.dumps({'revision': int(time.time()), 'visibility': visibility},
                              separators=(',', ':')) + '\n').encode('utf-8')
        directory = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
        with tempfile.NamedTemporaryFile(mode='wb', dir=output.parent,
                                         prefix='.visibility-', delete=False) as target:
            temporary = target.name
            target.write(payload)
            target.flush()
            os.fchmod(target.fileno(), 0o644)
            os.fsync(target.fileno())
        os.replace(temporary, output)
        replaced = True
        os.fsync(directory)
    except OSError:
        if replaced:
            raise SyncError('Visibility published, but directory durability could not be confirmed.') from None
        raise SyncError('Cannot atomically publish visibility; prior output retained. Check output permissions.') from None
    finally:
        if directory is not None:
            os.close(directory)
        if temporary is not None and not replaced:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def synchronize(token_file, output, *, opener=None):
    """Read fixed Airtable view and atomically publish; raise safe SyncError.

    opener is an injectable urllib-compatible transport for offline tests only.
    No credentials are read from the environment or any implicit file.
    """
    token = _token(token_file)
    if opener is None:
        opener = build_opener(NoRedirect())
    visibility = _visibility(token, opener)
    _publish(output, visibility)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token-file', type=Path, required=True,
                        help='Plain PAT file (for example a systemd credential)')
    parser.add_argument('--output', type=Path, required=True,
                        help='Public-safe JSON file in an existing private state directory')
    args = parser.parse_args(argv)
    try:
        synchronize(args.token_file, args.output)
    except SyncError as error:
        print('Availability sync failed: ' + str(error), file=sys.stderr)
        return 1
    except Exception:
        # Never let transport, filesystem, or unexpected library diagnostics
        # disclose request headers, response bodies, or credential paths.
        print('Availability sync failed: unexpected internal error.', file=sys.stderr)
        return 1
    print('Availability visibility published.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
