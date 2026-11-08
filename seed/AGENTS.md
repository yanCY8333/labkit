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

Long-running training or queue jobs are never left unwatched. **Multiple independent devices and multiple queues may be active at once.** Every independent run has a stable `run_id` (unique across the project, preserved on resume), a `device` record (see below), and an `alloc` record (what the run occupies). One device may own several runs, and one run may never overwrite another run's live state.

Three identifiers with three different lifetimes — never conflate them:

- `device_id` (the `device.id` field): **always one machine, one host.** A device is a host — never a card, never a queue, never a node inside a distributed job. One machine = one device, exactly, no matter how many GPUs it has, how many queues it runs, or how the cluster is wired. The only test that decides it: the machine whose state file (`batch.json` / progress file) the run's watcher reads is that run's device. That answer is a physical fact, so it never drifts when the deployment changes. `device` also carries the machine's own attributes (`label`, `host`, `accelerator`).
- `run_id`: one launched execution — a command / queue / training / analysis you actually started. One run = one watcher = one `live/<run_id>.json`. A **global monotonic counter**: `r0001`, `r0002`, … — never reused, and the same run keeps its number across resume. To mint a new one, scan the existing `AIWORK/Status/live/r*.json` files plus every `r*` reference in the current window and log, then take max+1.
- `task_id`: one unit of work inside a run's queue — one job, one subject, one batch element. **Globally unique, named by namespace plus sequence**: `<direction>-<branch>-<seq>`, e.g. `e002-b01-0007`. A task has no watcher and no live file of its own. The run's progress fields are all task-level counts: `total` (tasks in the queue), `done`, `failed`, and `current` — which is the global `task_id` of the task running now, not a per-run index. The full task list lives in the queue's own files (e.g. `batch.json`); labkit mirrors the counts and the current `task_id`, it never enumerates tasks.

What a run occupies is not a device — it is `alloc`, a run-level field. `alloc` records the resources this run holds (`gpu:8`, `gpu:0..3`, `nodes:4`). It is deployment metadata that lives on the run, so it may change between runs even on one machine, and it must never be confused with `device.accelerator` (what the machine is) or with the device id (where the state file lives). Single node with N GPUs is still one device with `alloc: gpu:N`; N independent single-GPU jobs on one node are one device, each run carrying its own `alloc`; a run spanning four nodes has one device (the coordinator whose state file the watcher reads) and `alloc: nodes:4`.

The observer/execution split is absolute. A run, once launched, runs to completion on its own: the execution script (queue / training / analysis) never reads the watcher, the live file, or the status page, and nothing they produce can change its course. The watcher is a pure observer — it only reads queue state and writes the run's live file; there is no control channel from watcher back to execution. So when you write the execution script: never poll the watcher, never wait on a live file, never take input from the status layer. And when you write the watcher: never signal, restart, or modify the queue — on stall or failure it only reports; recovery is always the queue's own `--resume` under a human's call.

When you launch one:

1. **Start a watcher.** A detached process that periodically (e.g. every 60s) reads queue state (`batch.json` / progress files). Each tick writes `AIWORK/Status/live/<run_id>.json` with: `run_id`, `name`, `device`, `alloc`, `dir`, `status` (`running`/`completed`/`failed`), `done`, `total`, `failed`, `current`, `elapsed`, `eta`, `note`, `updated`. Use a real wall-clock timestamp with UTC offset. The per-run file is the only cross-device live contract; remote watchers must deliver it to this shared path (transport is outside labkit).
2. **Merge through the existing syncer.** After writing the per-run file, run `uv run python AIWORK/Status/agent_sync_logfull.py`. New watchers may instead call its `write_live_entry(payload)` helper to perform both steps. The syncer merges all per-run files by `run_id`, preserves legacy entries without one, and writes `DATA.live` atomically under a process lock. Watchers must never rewrite the whole `live` field or another device's entry. The page auto-reloads every 30s while any run is `running`.
3. **Allow several Running entries.** The current status window's "Now" section may contain repeated `### Running — <run_id>` subsections with `device`, `alloc`, `status`, `run`, `doing`, `next`, `blocked`, and `watch: AIWORK/Status/live/<run_id>.json`. Keep the global goal/doing/next/blocked summary as well. At close, remove completed subsections individually; active subsections remain untouched.
4. **Report anomalies.** The watcher is passive: it reports first failure, stall (no progress for 3+ ticks), and completion. It does not restart or modify the queue. Findings go into the conversation and log; recovery uses the queue's own `--resume` semantics.
5. **Close runs independently.** Each watcher writes its final state and exits. Completed per-run files are removed only at the next session close, and only for that completed run; other devices' Running entries stay live. If no live entries remain, `DATA.live.runs` becomes empty. Durable results always use the normal README/panel/milestone path.

Watcher implementations live inside the experiment's own code/ directory (project property, not labkit property). A loop of `--monitor`/`--once` output parsing, or a tiny Python script, both qualify. Legacy `agent_watch.json` files are records only, not the authoritative multi-device interface.

## When the human confirms a milestone

The human says "this milestone is confirmed". You then do two things: append one row to `AIWORK/Status/status_global.md` (only ever on the human's word), and snapshot the necessary code and results into REVIEW:

1. Create `REVIEW/<name>/files/` and copy the content from AIWORK there, byte-for-byte.
2. Compute sha256 per file and write `MANIFEST.sha256`, one per line, `<hash>  files/<relative path>`.
3. Write `SOURCE.md`: source path, commit, time, file count.
4. Small, immutable things only: scripts, configs, tables and figures the human actually looked at. No weights, no raw logs, no bulk data — reference them (including `data/` entries) by path plus hash.

Once copied, the snapshot is dead. Never "fix" it afterwards.

**Promotion.** The human reviews what's in REVIEW — alone or together with you. When the human says a reviewed piece "goes into HUMAN", copy exactly that content from REVIEW into `HUMAN/`, unchanged, and log the promotion. You may also be asked to check HUMAN's completeness (that everything referenced actually exists); report findings in conversation, change nothing yourself.

Also: before copying any baseline into `AIWORK/Prototype/`, report the source URL and commit to the human for approval. After approval it never changes; make variants by copying into Experiment.

## Logging and closing a session

Every loggable operation gets **two durable entries at the event**: a start entry written immediately before the operation starts and an end entry written immediately after it finishes and its output is checked. Never wait until session close to record an operation, and never batch the start and end entries afterwards. The line format is `YYYY-MM-DD HH:MM:SS ±HH:MM | agent/model | TYPE | one sentence  out=<artifact path>`. The `agent/model` field is the driving agent first, then the model name — e.g. `opencode/deepseek-v4-pro` (never `cite/…` or a bare model id).

The start and successful end use the same TYPE, with `started` / `completed` stated explicitly in the sentence. This applies even to effectively instantaneous operations; if both real timestamps fall in the same second, keep both entries. An error or interruption is recorded immediately as `X` at its actual detection time — no fabricated successful end. A later resume is a new `R` operation with its own start and end entries. Do not synthesize missing historical start/end entries: history remains append-only.

At session close, rewrite the "Now" section of the current window in full: goal / doing / next / blocked. "Next" must be concrete — a command or a file, never "keep optimizing". Closing is a consistency check, not a substitute for event-time logging: verify that every finished operation has its end entry and every active operation has only its genuine start/current state.

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

Immediately after **every** durable start/end/`X` write, run `uv run python AIWORK/Status/agent_sync_logfull.py` to mirror it into the DATA block in `AIWORK/Status/inter.html`; the watcher is not a substitute for this. The sync keeps `updated` and the last ~10 `log` entries current, and maintains `logFull` as the mandatory complete history across every current and archived status window. **Never trim, overwrite with recent-only data, or fall back to recent-only for `logFull`.** Both recent and full views render newest-first. At session close also refresh `now` and changed structural fields of directions/branches (`status`, `conclusion`, `goal`). The DATA block is the page's only routine maintenance point; do not touch the code below it except for an explicit display repair like the newest-first fix.

Statistics panels are filled **on demand, not by default**: when the human asks for a table/figure, or when a milestone summary warrants one. The panel contract (documented above the DATA block): `type:"table"` with columns/rows copied verbatim from result files, or `type:"html"` with inline SVG/table (no external libraries, no fetch, no CDN), or `type:"placeholder"` reserving an empty patch. Every table/html panel must carry `source` (relative path). Never fabricate numbers. Two kinds of tables, both legitimate: **aggregate tables** (means, summaries — keep small) and **per-bench tables** (one row per image/dataset/subject with full numeric detail — expected whenever the experiment runs across many benches; the human verifies anomalies bench by bench). Prefer shipping a per-bench CSV in the branch directory alongside. Don't pool numbers across different budgets/protocols.

Log only what matters, and only as one of the six TYPEs above. Don't log reading, searching, or thinking; conclusion evolution is recorded in the README itself (strike + append), not as a log entry. When the log exceeds 40 entries, or the window is older than 7 days, move it into `archive/` (renamed `agent_status_<start>_<end>.md`) and create a fresh window (`agent_status_<stamp>_current.md`), carrying over the "Environment" and "Now" sections, log emptied. Run the sync immediately after every archive roll: `logFull` must remain continuous across the archive and the new window.

At the first work session, ask the human once: environment, how to run, where artifacts go, what's forbidden — write it into the window's "Environment" section; update only on change.

## Never violate

- `Prototype/` holds pristine baseline repos. Never modify. Copy into Experiment to vary.
- REVIEW only ever receives snapshots from AIWORK via the procedure above; afterwards nobody edits, including you.
- HUMAN only ever receives content on the human's promotion order; existing content you never modify, delete, or reorganize.
- Only these need the human's sign-off: new direction numbers · rows in `status_global.md` · snapshots into REVIEW · promotions into HUMAN (plus the source vetting before copying into Prototype). Everything else is your call.
