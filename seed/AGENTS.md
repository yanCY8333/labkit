# {{NAME}}

Conversations die; the repo doesn't. This is the only rules file in the project — read it once and you know how to work.

Naming: zones are ALL-CAPS (AIWORK / REVIEW / HUMAN), layers inside a zone are Capitalized (Prototype / Experiment / Status), everything below is lowercase. Files prefixed `agent_` are your protocol files: read them, write them, follow them. The human's manuals are `README_zh.md` / `README_en.md` at the root; you don't need them.

## How the repo is divided

AIWORK is your workspace — write freely inside it; the restrictions that exist come below. REVIEW is the review zone: when the human confirms a milestone, you put the necessary code and results there as snapshots; the human examines them there, sometimes together with you. HUMAN is the project's residue of record — the final, highest-value content: things are copied in from REVIEW only when the human says to promote them, and what has already landed there you never touch. Objections go into the conversation, never into files.

## Starting a session

Read `AIWORK/Status/agent_status_<stamp>_current.md` first (at seed time it's `agent_status_current.md`; afterwards it carries a timestamp). It tells you where the project stands, what's next, what's blocked. Then skim the header fields of the READMEs under `AIWORK/Experiment/` — that's the full experiment inventory. Stop there. Don't read history end-to-end; open a single experiment's README only when you need its details.

If HUMAN has a section relevant to your current task, you may read it.

## Creating an experiment

Create a directory under `AIWORK/Experiment/`. A direction is `e###-YYYYMMDD-<slug>`; a branch inside a direction is `b##-YYYYMMDD-<slug>` (all lowercase). Opening a new direction (its `e###` number) requires the human's explicit sign-off — if the human hasn't asked for a new direction, don't open one. Branches are yours to number freely. List sibling directories first; never reuse a number.

`data/` and `environ/` inside Experiment are the two directories there that are not experiments.

`data/` is the shared pool for heavily reused inputs (fitting targets, datasets and the like). Reference its contents by relative path — never copy them into experiment directories. Treat them as read-only: if you need a variant, derive it inside your own experiment directory. Subdivide by data type as the project needs, and note the source when adding a new dataset. The pool is not tracked by git — integrity comes from the path+hash references you write in experiment READMEs.

`environ/` is the shared reproducibility substrate: machine and runtime records (GPU, driver, CUDA, environment versions), protocols frozen after human approval that span experiments, and shared default configs. Experiments reference entries here instead of restating them. It grows by accretion; frozen entries are never rewritten — a changed protocol is a new entry plus a note in the referencing experiment.

Copy the README from `AIWORK/Experiment/agent_template.md` and fill the header. The critical rule: **criteria must be fixed before the first run.** Writing the yardstick after the run is fabricating the standard retroactively — such an experiment's conclusion can only be recorded as `inconclusive`.

## After running

Fill the README header's `artifacts` and `conclusion`, add a results section in the body. If a conclusion is later overturned, don't delete the old one — append the new and strike through the old. How conclusions changed is itself information.

## While a run is active

Long-running training or queue jobs are never left unwatched. When you launch one:

1. **Start a watcher.** A detached process (separate terminal, background task — whatever survives your session) that periodically (e.g. every 60s) reads the queue's state (`batch.json` / progress files) and writes a small `agent_watch.json` next to the current status window in `AIWORK/Status/`, containing: run name, direction/branch, status (running/completed/failed), done/total/failed counts, current item, elapsed, ETA, timestamp.
2. **Mirror into inter.** Each watcher tick also rewrites the `live` field of `AIWORK/Status/inter.html`'s DATA block: `{ updated, runs: [...] }` — one entry per active queue. The page auto-reloads every 30s while any run is `running`, so the human sees live progress by keeping the page open. Never touch the code below the DATA block for this.
3. **Report anomalies.** The watcher is passive: it reports (first failure, stall: no progress for 3+ ticks, completion), it does not restart or modify anything. When something fails, the finding goes into the conversation and the log line; the queue's own `--resume` semantics handle recovery.
4. **Close it out.** When all runs complete or stop, the watcher writes final state, exits, and the `live` block is emptied at your next session close. Live info is transient — durable results go through the normal README/panel/milestone path.

Watcher implementations live inside the experiment's own code/ directory (project property, not labkit property). A loop of `--monitor`/`--once` output parsing, or a tiny Python script, both qualify.

## When the human confirms a milestone

The human says "this milestone is confirmed". You then do two things: append one row to `AIWORK/Status/status_global.md` (only ever on the human's word), and snapshot the necessary code and results into REVIEW:

1. Create `REVIEW/<name>/files/` and copy the content from AIWORK there, byte-for-byte.
2. Compute sha256 per file and write `MANIFEST.sha256`, one per line, `<hash>  files/<relative path>`.
3. Write `SOURCE.md`: source path, commit, time, file count.
4. Small, immutable things only: scripts, configs, tables and figures the human actually looked at. No weights, no raw logs, no bulk data — reference them (including `data/` entries) by path plus hash.

Once copied, the snapshot is dead. Never "fix" it afterwards.

**Promotion.** The human reviews what's in REVIEW — alone or together with you. When the human says a reviewed piece "goes into HUMAN", copy exactly that content from REVIEW into `HUMAN/`, unchanged, and log the promotion. You may also be asked to check HUMAN's completeness (that everything referenced actually exists); report findings in conversation, change nothing yourself.

Also: before copying any baseline into `AIWORK/Prototype/`, report the source URL and commit to the human for approval. After approval it never changes; make variants by copying into Experiment.

## Closing a session

Rewrite the "Now" section of the current window in full: goal / doing / next / blocked. "Next" must be concrete — a command or a file, never "keep optimizing". Append one log line: `YYYY-MM-DD HH:MM:SS ±HH:MM | agent/model | TYPE | one sentence  out=<artifact path>`. The `agent/model` field is the driving agent first, then the model name — e.g. `opencode/deepseek-v4-pro` (never `cite/…` or a bare model id).

Log TYPE — six actions, nothing else (this is labkit's own system; thoughts live only insofar as they became one of these):
- `N` new (opened a direction / branch / experiment directory)
- `R` run (executed a command / queue / training / analysis)
- `F` fix (repaired a data/path/structure bug — appends a correction record; the original entry is never overwritten)
- `M` milestone (human confirmed; snapshot into REVIEW)
- `P` promote (content promoted into HUMAN)
- `X` fail (error or anomaly, left on record)

Nothing else is a loggable action. There is no "update" type and never will be: conclusions and records are append-only. An overturned conclusion is struck through in place with the new one appended — that is recording evolution, not rewriting. Anything that would "edit history" is forbidden, full stop.

Discussions, reasoning, and questions are never logged. If an idea matters, it becomes an action first — open an experiment, amend a record — and that action is what gets logged.

**Timestamps**: always real wall-clock time read from the machine at the moment of writing, seconds included, with explicit UTC offset (e.g. `2026-10-28 14:26:37 +08:00`). Never round, never fabricate neat values, never copy an old timestamp forward. If you cannot read the clock, say so instead of guessing.

Also refresh the DATA block in `AIWORK/Status/inter.html` — that block is the page's only maintenance point; do not touch the code below it. Refresh on close:
- `updated`, `now`, last ~10 `log` lines;
- structural fields of directions/branches: `status`, `conclusion`, `goal` (only when they changed).

Statistics panels are filled **on demand, not by default**: when the human asks for a table/figure, or when a milestone summary warrants one. The panel contract (documented above the DATA block): `type:"table"` with columns/rows copied verbatim from result files, or `type:"html"` with inline SVG/table (no external libraries, no fetch, no CDN), or `type:"placeholder"` reserving an empty patch. Every table/html panel must carry `source` (relative path). Never fabricate numbers. Two kinds of tables, both legitimate: **aggregate tables** (means, summaries — keep small) and **per-bench tables** (one row per image/dataset/subject with full numeric detail — expected whenever the experiment runs across many benches; the human verifies anomalies bench by bench). Prefer shipping a per-bench CSV in the branch directory alongside. Don't pool numbers across different budgets/protocols.

Log only what matters, and only as one of the six TYPEs above. Don't log reading, searching, or thinking; conclusion evolution is recorded in the README itself (strike + append), not as a log entry. When the log exceeds 40 entries, or the window is older than 7 days, move it into `archive/` (renamed `agent_status_<start>_<end>.md`) and create a fresh window (`agent_status_<stamp>_current.md`), carrying over the "Environment" and "Now" sections, log emptied.

At the first work session, ask the human once: environment, how to run, where artifacts go, what's forbidden — write it into the window's "Environment" section; update only on change.

## Never violate

- `Prototype/` holds pristine baseline repos. Never modify. Copy into Experiment to vary.
- REVIEW only ever receives snapshots from AIWORK via the procedure above; afterwards nobody edits, including you.
- HUMAN only ever receives content on the human's promotion order; existing content you never modify, delete, or reorganize.
- Only these need the human's sign-off: new direction numbers · rows in `status_global.md` · snapshots into REVIEW · promotions into HUMAN (plus the source vetting before copying into Prototype). Everything else is your call.
