# Status — current

- window_start: {{DATETIME}}
- updated: {{DATETIME}}

## Environment

Ask the human once at the first work session, then record here.

## Now

- goal: {{GOAL}}
- doing: none
- next: read AGENTS.md, create the first experiment
- blocked: none

## Log

<!-- One entry per line, max 40 entries, newest first; on archive roll the log is emptied into the archive window.
     Format: YYYY-MM-DD HH:MM:SS ±HH:MM | agent/model | TYPE | one sentence  out=<relative path>
     agent/model = driving agent first, then model name (e.g. opencode/deepseek-v4-pro), never cite/… or a bare model id
     TYPE (actions only): N new · R run · F fix (append correction, never overwrite) · M milestone · P promote · X fail
     Every loggable operation writes a start entry immediately before it begins and an end entry immediately after checked
     completion (same TYPE, started/completed stated); errors/interruptions write X immediately at detection; a resume is a
     new R start/end pair. Event-time only — never batch at session close, never synthesize missing history.
     No "update" type exists: records are append-only; overturned conclusions are struck through, appended — never rewritten.
     Discussions/reasoning/questions are never logged — only actions.
     After every durable status-log write, run agent_sync_logfull.py to mirror the log into inter.html. -->
