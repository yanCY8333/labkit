# {{NAME}}

{{GOAL}}

Chinese manual: `README_zh.md`. The rules file `AGENTS.md` is the AI's; scan its "Never violate" section if you want to check what the AI won't do.

## Layout

```text
AIWORK/      the AI's workspace, free rein
  Prototype/   pristine baseline repos, never modified once copied in
  Experiment/  experiments; you confirm directions, the AI branches freely inside
    data/      heavily reused inputs, referenced by path, never copied
    environ/   machine/hardware records, frozen protocols, shared defaults
  Status/      handoff window + milestone table + inter overview page + archive
REVIEW/      your confirmed milestones; the AI snapshots code and results here, you review them here
HUMAN/       the high-value residue that survives review; enters only when you say so
```

Naming: zones ALL-CAPS, layers Capitalized, deeper levels lowercase. The AI's protocol files (AGENTS.md, agent_ prefix) are in English.

## Where you look

- Where things stand: the `_current` window in `AIWORK/Status/`
- What experiments exist and how they went: `AIWORK/Status/inter.html` (double-click)
- Confirmed milestones: `status_global.md` + snapshots under `REVIEW/`
- Your content: `HUMAN/`

## The four things you do

1. Approve directions: a new top-level `e###` needs your sign-off; if you haven't asked, the AI won't open one
2. Confirm milestones: only on your word does the AI add to status_global and snapshot code + results into REVIEW
3. Review and promote: you examine REVIEW (alone or with the AI); on your word the content is copied into HUMAN
4. Vet Prototype: before a baseline repo is copied in, you approve source and version

Everything else is the AI's call.

## Lines

- REVIEW contents are immutable after landing; sha256 manifests detect any tampering
- HUMAN contents are never modified by the AI
- The AI's self-report is not evidence; evidence is the hash manifests and git history

## New session

Open any agent in the project directory and say "read AGENTS.md and begin".

## inter page

- Notes live in this browser's localStorage; they don't travel. Conclusions that matter go into HUMAN/ directly.
- While runs are active the page auto-refreshes with watcher-written progress; durable results go through README / REVIEW.
