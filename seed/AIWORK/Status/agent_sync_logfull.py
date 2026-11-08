"""Synchronize inter.html logs and independent per-device live runs.

Every watcher writes one Status/live/<run_id>.json file and calls this script.
The script merges those files by run_id; no watcher replaces another device's
live entry. It also preserves legacy DATA.live entries without per-run files.

Run immediately after every durable status-log or live-run write. Log arrays are
built in chronological order: window files are append-only but their line order
is not guaranteed chronological, so entries are sorted (stably) by the timestamp
embedded in each line; inter.html renders both recent and full views newest-first.
Full history is never trimmed: archive windows are prepended to the current one.
"""

import contextlib
from datetime import datetime
import json
import os
from pathlib import Path
import re
import time


STATUS = Path(__file__).resolve().parent
INTER = STATUS / 'inter.html'
LIVE = STATUS / 'live'
LOCK = STATUS / 'agent_sync_logfull.lock'
LOG_RE = re.compile(
    r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2} '
    r'\| [^|]+ \| [NRFMPX] \| .+$'
)
RUN_ID_RE = re.compile(r'^[A-Za-z0-9._-]+$')
LIVE_STATUSES = {'running', 'completed', 'failed'}


@contextlib.contextmanager
def synchronized(timeout=30):
    """Serialize inter.html replacement across independent devices/processes."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - LOCK.stat().st_mtime > 300:
                    LOCK.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f'Could not acquire {LOCK}')
            time.sleep(0.1)
    try:
        yield
    finally:
        os.close(fd)
        try:
            LOCK.unlink()
        except FileNotFoundError:
            pass


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    os.replace(tmp, path)


def normalize_live_entry(payload):
    """Validate and normalize one independent run record."""
    if not isinstance(payload, dict):
        raise TypeError('Live run must be a JSON object')
    run_id = payload.get('run_id') or payload.get('name') or payload.get('run')
    if not run_id or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f'run_id must match {RUN_ID_RE.pattern}: {run_id!r}')
    name = payload.get('name') or payload.get('run') or run_id
    device = payload.get('device') or {'id': 'unspecified', 'label': 'unspecified'}
    if isinstance(device, str):
        device = {'id': device, 'label': device}
    if not isinstance(device, dict) or not device.get('id'):
        raise ValueError(f'device.id is required for new run {run_id}')
    device = dict(device)
    device.setdefault('label', device['id'])
    status = payload.get('status')
    if status not in LIVE_STATUSES:
        raise ValueError(f'Invalid live status for {run_id}: {status!r}')
    updated = payload.get('updated') or payload.get('timestamp')
    if not updated:
        raise ValueError(f'updated/timestamp is required for {run_id}')
    return {
        'run_id': run_id,
        'name': name,
        'device': device,
        'alloc': payload.get('alloc') or '',
        'dir': payload.get('dir') or payload.get('queue') or '',
        'status': status,
        'done': int(payload.get('done', 0)),
        'total': payload.get('total'),
        'failed': int(payload.get('failed', 0)),
        'current': payload.get('current') or '',
        'elapsed': payload.get('elapsed'),
        'eta': payload.get('eta'),
        'note': payload.get('note') or '',
        'updated': updated,
    }


def write_live_entry(payload):
    """Atomically persist one run, then merge all live runs into inter.html."""
    entry = normalize_live_entry(payload)
    atomic_json(LIVE / f'{entry["run_id"]}.json', entry)
    main()


TS_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ([+-])(\d{2}):(\d{2})')


def entry_key(entry):
    """Sort key from the timestamp embedded in each log line.

    Window files only guarantee append-only text, not chronological line
    order (different agents have appended newest-first as well as
    oldest-first within one window). The embedded timestamp is the only
    reliable ordering, so parse it including its UTC offset. Mixed
    offsets are compared as absolute times; an unparseable line (which
    LOG_RE should have rejected already) sorts as empty.
    """
    match = TS_RE.match(entry)
    if not match:
        return (1, '', 0)
    stamp = match.group(1)
    sign = -1 if match.group(2) == '-' else 1
    offset = sign * (int(match.group(3)) * 60 + int(match.group(4)))
    return (0, stamp, -offset)


def window_entries(path):
    text = path.read_text(encoding='utf-8')
    if '## Log' not in text:
        raise ValueError(f'Missing Log section: {path}')
    section = text.split('## Log', 1)[1].split('\n## ', 1)[0]
    lines = []
    in_comment = False
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if in_comment:
            if '-->' in stripped:
                in_comment = False
            continue
        if stripped.startswith('<!--'):
            if '-->' not in stripped:
                in_comment = True
            continue
        lines.append(line)
    invalid = [line for line in lines if not LOG_RE.match(line)]
    if invalid:
        raise ValueError(f'Unrecognized durable log line in {path}: {invalid[0]}')
    return list(reversed(lines))


def array_text(name, entries, trailing_comma):
    body = ',\n'.join('    ' + json.dumps(entry, ensure_ascii=False)
                      for entry in entries)
    comma = ',' if trailing_comma else ''
    return f'  {name}: [\n{body}\n  ]{comma}'


def legacy_watch_entry():
    """Recover a legacy run from the watcher's own valid JSON record."""
    path = STATUS / 'agent_watch.json'
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding='utf-8'))
    name = payload.get('name') or payload.get('run')
    if not name:
        return None
    return {
        'name': name,
        'device': {'id': 'unspecified', 'label': 'unspecified'},
        'alloc': payload.get('alloc') or '',
        'dir': payload.get('dir') or payload.get('queue') or '',
        'status': payload.get('status', 'running'),
        'done': payload.get('done', 0),
        'total': payload.get('total'),
        'failed': payload.get('failed', 0),
        'current': payload.get('current') or '',
        'elapsed': payload.get('elapsed'),
        'eta': payload.get('eta'),
        'note': payload.get('note') or '',
        'updated': payload.get('updated') or payload.get('timestamp') or '',
    }


def read_live_runs(block):
    match = re.search(r'(?m)^  live: (.*),?$', block)
    if not match:
        return {'updated': '', 'runs': []}, []
    raw = match.group(1).rstrip(',')
    try:
        live = json.loads(raw)
        legacy = [run for run in live.get('runs', []) if not run.get('run_id')]
        return live, legacy
    except (json.JSONDecodeError, UnicodeDecodeError):
        # A legacy writer may have produced malformed/multiline JSON entirely.
        fallback = legacy_watch_entry()
        if fallback is None:
            return {'updated': '', 'runs': []}, []
        return {'updated': fallback['updated'], 'runs': [fallback]}, [fallback]


def merged_live(block):
    live, legacy = read_live_runs(block)
    files = sorted(LIVE.glob('*.json')) if LIVE.exists() else []
    if not files:
        # A legacy watcher may still be active; never clear it during migration.
        return live
    runs = list(legacy)
    for path in files:
        runs.append(normalize_live_entry(json.loads(path.read_text(encoding='utf-8'))))
    by_id = {}
    for run in runs:
        # A migrated run and its legacy card share name; the per-run file wins.
        key = run.get('run_id') or f'legacy-{run.get("name", "run")}'
        by_id[key] = run
    ordered = sorted(
        by_id.values(),
        key=lambda run: (
            (run.get('device') or {}).get('id', 'unspecified')
            if isinstance(run.get('device'), dict) else 'unspecified',
            run.get('run_id') or run.get('name') or '',
        ),
    )
    timestamps = [str(run.get('updated') or run.get('timestamp') or '')
                  for run in ordered]
    return {'updated': max(timestamps, default=''), 'runs': ordered}


def main():
    with synchronized():
        current = sorted(STATUS.glob('agent_status_*_current.md'))
        if not current:
            current = sorted(STATUS.glob('agent_status_current.md'))  # seed-time name
        if len(current) != 1:
            raise ValueError(f'Expected one current status window, got {len(current)}')
        windows = sorted((STATUS / 'archive').glob('agent_status_*.md')) + current
        entries = []
        for window in windows:
            entries.extend(window_entries(window))
        if not entries:
            raise ValueError('Refusing to build an empty full log')
        # Window files are append-only, not ordered: agents have written
        # newest-first and oldest-first sections inside one window. Sort by
        # each line's own timestamp (stable, so equal timestamps keep their
        # file order and the start/end pair of one operation stays adjacent).
        entries.sort(key=entry_key)
        recent = entries[-10:]
        text = INTER.read_text(encoding='utf-8')
        data_start = text.index('const DATA = {')
        data_end = text.index('/* ===================== code below', data_start)
        block = text[data_start:data_end]
        live = merged_live(block)
        # Match only a whole-line `live: {...},` object literal. If an agent ever
        # merges another field onto the same line (e.g. `live: {...}, directions: [`),
        # this no longer matches and raises instead of silently eating that field.
        block, count = re.subn(
            r'(?m)^  live: \{.*\},\s*$',
            lambda _: '  live: ' + json.dumps(live, ensure_ascii=False, separators=(',', ':')) + ',',
            block,
            count=1,
        )
        if count != 1:
            raise ValueError('DATA.live replacement failed')
        updated = entries[-1].split(' | ', 1)[0]
        block, count = re.subn(
            r'(?m)^  updated: ".*",$', f'  updated: "{updated}",', block, count=1,
        )
        if count != 1:
            raise ValueError('DATA.updated replacement failed')
        replacement = (
            array_text('log', recent, True) + '\n' +
            array_text('logFull', entries, False) + '\n};'
        )
        pattern = re.compile(
            r'  log: \[\n.*?\n  \](?:,\n  logFull: \[\n.*?\n  \])?\n\};'
            r'|  log: \[\](?:,\n  logFull: \[\])?\n\};',
            re.DOTALL,
        )
        block, count = pattern.subn(lambda _: replacement, block, count=1)
        if count != 1:
            raise ValueError('DATA log/logFull replacement failed')
        text = text[:data_start] + block + text[data_end:]
        tmp = INTER.with_suffix('.html.tmp')
        tmp.write_text(text, encoding='utf-8')
        os.replace(tmp, INTER)
        print(
            f'Synchronized {len(windows)} window(s): recent={len(recent)}, '
            f'full={len(entries)}, live={len(live["runs"])}'
        )


if __name__ == '__main__':
    main()
