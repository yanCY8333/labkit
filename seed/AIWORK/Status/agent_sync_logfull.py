"""Synchronize inter.html recent/full logs from every durable status window.

Run immediately after every status-log write. Arrays are stored oldest-first;
inter.html renders both recent and full views newest-first. Full history is never
trimmed: archive windows are prepended to the current window.
"""

import json
import os
from pathlib import Path
import re


STATUS = Path(__file__).resolve().parent
INTER = STATUS / 'inter.html'
LOG_RE = re.compile(
    r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2} '
    r'\| [^|]+ \| [NRFMPX] \| .+$'
)


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
    # Durable status windows are newest-first; DATA arrays are oldest-first.
    return list(reversed(lines))


def array_text(name, entries, trailing_comma):
    body = ',\n'.join('    ' + json.dumps(entry, ensure_ascii=False)
                      for entry in entries)
    comma = ',' if trailing_comma else ''
    return f'  {name}: [\n{body}\n  ]{comma}'


def main():
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
    recent = entries[-10:]
    text = INTER.read_text(encoding='utf-8')
    data_start = text.index('const DATA = {')
    data_end = text.index('/* ===================== code below', data_start)
    block = text[data_start:data_end]
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
    print(f'Synchronized {len(windows)} window(s): recent={len(recent)}, full={len(entries)}')


if __name__ == '__main__':
    main()
