# {{NAME}}

{{GOAL}}

This is the project's English manual — one page, read it and you're oriented. Chinese version: `README_zh.md`. The rules file `AGENTS.md` is for the AI; you don't need it, though its "Never violate" section is a quick way to check what the AI won't do.

## Layout

```text
├── AIWORK —— the AI's workspace, it works freely here
│   ├── Prototype —— pristine baseline repos; copied in once, never modified, the basis of all later work
│   ├── Experiment —— one directory per experiment; you confirm directions, the AI branches freely inside them
│   │   ├── data —— heavily reused inputs (fitting targets, datasets); referenced by path, never copied per experiment
│   │   └── environ —— reproducibility substrate: environment/hardware records, cross-experiment frozen protocols, shared defaults
│   └── Status —— state records
│       ├── status_global —— confirmed milestones, one row each; only you confirm, the AI never adds rows on its own
│       ├── agent_status_<stamp>_current —— rolling handoff window; the AI reads it at session start, writes it at close
│       ├── inter.html —— your one-page overview: directions / experiments / conclusions / stats + your own notes (double-click, AI refreshes data on close)
│       └── archive —— rolled-out old windows, append-only
├── REVIEW —— your confirmed milestones: the AI snapshots the necessary code and results here, and you examine them here (sometimes together with the AI)
└── HUMAN —— the highest-value residue that survives review; copied in from REVIEW only on your promotion order, after which the AI never touches it
```

Naming: ALL-CAPS = zone (AIWORK / REVIEW / HUMAN); Capitalized = layer inside a zone (Prototype / Experiment / Status); everything below is lowercase. `AGENTS.md` and files prefixed `agent_` are the AI's protocol files, written in English (LLMs are native in English; instructions land better). Docs for you are bilingual.

## The only four places you look

| You want to know | Look at |
|---|---|
| Where the project stands, what's next | the `_current` window in `AIWORK/Status/` |
| What experiments exist, how they went | double-click `AIWORK/Status/inter.html` (one-page overview with stats panels and your own note boxes) |
| Which milestones you confirmed | `AIWORK/Status/status_global.md` and the snapshots under `REVIEW/` |
| The final high-value residue | `HUMAN/` |

## The only four things you do

1. **Open a direction**: when the AI wants a new top-level experiment direction (`e###`), you sign off the number. If you haven't asked for a new direction, the AI won't open one.
2. **Confirm milestones**: after the AI reports, you say "confirmed" — only then does it append to `status_global` and snapshot the necessary code and results into REVIEW.
3. **Review and promote**: you examine what's in REVIEW (you may have the AI review alongside); when you say "this goes into HUMAN", the AI copies it from REVIEW unchanged. HUMAN holds the final, highest-value content — not casual notes.
4. **Vet Prototype**: before the AI copies a baseline repo in, you approve the source and version.

Everything else is the AI's call.

## Lines that don't move

- REVIEW holds review material: snapshots with sha256 manifests, untouched after landing. To check one, recompute hashes against the manifest.
- HUMAN receives content only on your order; afterwards the AI never modifies, deletes, or "tidies" it. It may check completeness on request — findings in conversation only.
- The AI's self-report is not evidence. Evidence is snapshot manifests and git history.
- Shared data lives in `AIWORK/Experiment/data/`; frozen protocols and environment records live in `AIWORK/Experiment/environ/`. Experiments reference both by path instead of copying.

## Starting a new agent session

Open any agent in the project directory and say "read AGENTS.md and begin". It picks up from the window — no import, no setup.

## About the inter page

- Double-click `AIWORK/Status/inter.html`; pick a direction or experiment from the dropdown, or click a row on the overview.
- Notes live in the browser's localStorage on this machine — they don't travel. Treat them as scratch; conclusions that matter go into `HUMAN/` directly.
- While experiments run, a live marker appears and the page auto-refreshes; progress cards are written by the watcher. That's transient info — durable results go through README / REVIEW.
