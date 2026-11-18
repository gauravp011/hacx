# BUILD_PLAN v2 — IncidentLens

> Companion to `HANDOVER.md`. HANDOVER says **what** to build; this file says **in what order**, **with which model**, **what to tell Kiro** and **how to know a task is done**.
> **v2 (18 Nov 2026):** re-planned for **1,000 Kiro credits** and a **26 Nov 2026** finish, building in **Kiro IDE**. Supersedes BUILD_PLAN v1 and HANDOVER §11.
> **v2.1 (18 Nov 2026):** models and credit estimates updated to the real Kiro model list and multipliers.
> **v2.2 (18 Nov 2026):** APM setup done and v0.1.0 test release published. Planning docs (`HANDOVER.md`, `BUILD_PLAN.md`, `docs/apm-notes.md`) are **private**: kept in the local workspace for Kiro `#File` references, git-ignored, never pushed. Kiro skill testing is via "Import a skill".

---

## 1. Constraints and reduced scope

| Item | v1 | v2 (now) |
|---|---|---|
| Finish date | 5 Dec | **Publish 25 Nov, 26 Nov buffer** |
| Credits | 1,500 | **1,000** |
| Scenarios | 6 + 2 hard variants | **4 + 1 hard variant** |
| Eval runs | 3 per scenario | **2 per scenario on Sonnet 5.5 + 2 on Haiku 5.5 (+ optional 1 on GPT 5.6 Luna)** |
| Prompts | 3 | **2** (`/investigate-incident`, `/quick-triage`) |
| Post-mortem templates | engineering + executive | **engineering only** (executive is optional) |
| Log formats | JSONL + plain text | **JSONL only** (plain text = documented limitation) |

**Scenarios kept:** `db-pool-exhaustion`, `bad-deploy`, `cert-expiry`, `memory-leak`, plus hard variant `loud-red-herring` (the noisiest service is not the cause).
**Never cut:** redaction, evidence check, evaluation scorecard, README sections, demo, publishing.

---

## 2. Model selection rules (actual Kiro multipliers)

### Models to use

| Model | Multiplier | Use for |
|---|---|---|
| **Claude Haiku 5.5** | **0.06x** | **The workhorse.** Boilerplate, schemas, tests, docs, prompt files, and executing spec tasks after a stronger model has written the spec. Cheap evaluation runs |
| **Claude Sonnet 5.5** | 1.3x | Writing specs, safety-critical code (redaction), agent and skill instructions that need judgement, escalations from Haiku, main evaluation runs |
| **Claude Opus 5.5** | 2x | Only two tasks: RCA reasoning design (T10) and the final read-only review (T21). Plus escalations after Sonnet fails twice |
| **GPT 5.6 Luna** (optional) | 0.6x | One evaluation run per scenario to show the package works across model vendors. Only if your org allows cross-region models |

### Models to skip

| Model | Why |
|---|---|
| Haiku 4.5 (0.4x) | Haiku 5.5 is newer and about 7x cheaper |
| Sonnet 5 / 4.6 / 4.5 (1.3x) | Same price as Sonnet 5.5, which is newer |
| Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 (2.2x) | More expensive than Opus 5.5, which is newer |
| GPT 5.6 Sol (4.4x), GPT 5.6 Terra (2.2x) | Expensive, no advantage for this project |
| Qwen3 Coder Next (0.05x), MiniMax M2.1 / M2.5 | Barely cheaper than Haiku 5.5. Mixing vendors in your build adds inconsistency and possible approval questions |

### The core tactic: "Sonnet plans, Haiku builds"

In Kiro Spec mode, write the spec (requirements → design → tasks) with **Sonnet 5.5**, then **switch the model picker to Haiku 5.5** before clicking through the tasks. A good spec makes the implementation steps simple enough for Haiku, at about 1/20th of Sonnet's price.

**Escalation rule:** Haiku 5.5 fails twice on a task → Sonnet 5.5. Sonnet fails twice → Opus 5.5 for **one** attempt with a precise description of the failure. Then back down.

> Credit numbers in this plan are estimates. Real usage depends on how long each conversation runs. Check actual usage at the end of each day.

---

## 3. Credit-saving rules for Kiro IDE (read before T01)

1. **New chat session per task.** Long sessions resend growing context, so every message gets more expensive.
2. **Point to files, don't paste them.** Use `#File` / `#Folder` context references (e.g. `#HANDOVER.md`) instead of pasting text.
3. **Steering files do the repeating.** Rules, structure and data contracts live in `.kiro/steering/`, so prompts can stay short.
4. **Spec mode only for 3 things:** generator, parser, RCA reasoning. Use Vibe (chat) mode for everything else. Specs are the "Built with Kiro" evidence, but each costs credits.
5. **Run tests yourself** in Kiro's terminal (`pytest -q`). Don't ask the agent to "run tests and fix everything" in a loop. Paste only the failing test output back.
6. **Agent hooks cost credits each time they fire.** Create at most **two** narrowly scoped hooks (see T02). Never use a hook that fires on every file save across the repo. Disable hooks during heavy editing.
7. **Ask for targeted edits:** "change only function X in file Y". Avoid "rewrite the file".
8. **Supervised mode on core tasks** (generator, parser, RCA skill) so you review diffs before they're applied. Autopilot is fine for Haiku tasks.
9. **Use Claude chat outside Kiro for writing work** (README wording, demo script, reviewing the failure-pattern reference) if you have it. That costs zero Kiro credits.
10. **Check credit usage at the end of each day** against the tracker in §7.
11. **Never put scenario logs in context** (`#Folder examples/` or `#File` on a `.jsonl`). They are 20k–40k lines each. Only scripts read them.
12. **Private docs stay private.** Kiro may read `HANDOVER.md`, `BUILD_PLAN.md` and `docs/apm-notes.md`, but must never commit them, copy their content into `README.md`, or reference them from anything under `.apm/`.

---

## 4. One-time setup

- [ ] **S1 Kiro IDE:** sign in, confirm the 1,000 credit balance, open the model picker and note each model's multiplier.
- [x] **S2 Accounts:** GitLab push access works; portal publishing works (v0.1.0 visible).
- [ ] **S3 Local tools:** Python 3.11+, Git, `pip install pandas faker drain3 pyyaml jsonschema pytest`, gitleaks (or `pip install detect-secrets`), OBS (for the demo).
- [x] **S4 APM details:** `docs/apm-notes.md` written (install, `apm init`, `apm.yml`, `SKILL.md` format, publish flow, Kiro skill import). Agent/prompt/hook formats still marked VERIFY there.
- [ ] **S5 Test runtime:** run the package inside **Kiro** (skills imported via Agent Steering & Skills → + → Import a skill) with Sonnet 5.5 (primary), Haiku 5.5 (low-cost) and optionally GPT 5.6 Luna (cross-vendor). Only models you actually test become "supported models" in the README.
- [ ] **S5b Model approval:** confirm with the organizers that GPT 5.6 Luna (cross-region) is allowed. If unsure, skip it.
- [x] **S6 Form fields:** submitted for v0.1.0 (update description at final release; remove "preview").
- [ ] **S7 Private docs:** copy `HANDOVER.md`, `BUILD_PLAN.md` to the repo root and `apm-notes.md` to `docs/`. Make sure `.gitignore` lists all three **before** any commit. If they were already committed: `git rm --cached HANDOVER.md BUILD_PLAN.md docs/apm-notes.md`, commit and push.

---

## 5. Day-by-day plan

Credits shown are estimates **including** the model multiplier.

### Day 1 — Wed 18 Nov: foundation

| Task | Model | Mode | Credits |
|---|---|---|---|
| T01 Skeleton | Haiku 5.5 | Vibe | 1 |
| T02 Steering files + secret scanning + 2 hooks | Haiku 5.5 | Vibe | 1 |
| T03 JSON schemas + schema tests | Haiku 5.5 | Vibe | 1 |

**T01 prompt:**
> Read #HANDOVER.md §4 and #docs/apm-notes.md. Create the folder structure in §4 with one-line TODO placeholder files, but only for the components listed as kept in #BUILD_PLAN.md §1. apm.yml already exists: don't run apm init or edit it. Create requirements.txt (pandas, faker, drain3, pyyaml, jsonschema, pytest) and .gitignore with: HANDOVER.md, BUILD_PLAN.md, docs/apm-notes.md, .kiro/skills/, incident-report/, runs/, .env, __pycache__. No logic yet.

**T02 prompt:**
> Create Kiro steering files in .kiro/steering/: rules.md (data rules from #HANDOVER.md §2, plus: never commit or reference HANDOVER.md, BUILD_PLAN.md or docs/apm-notes.md), structure.md (§4), contracts.md (§5 JSON formats), style.md (Python 3.11, type hints, docstrings, no network calls, seeded randomness, small functions). Add a pre-commit config running gitleaks; if gitleaks isn't installed, skip it and tell me.
> Then create two Kiro agent hooks: (1) manual-trigger hook "update-readme-from-scorecard" that syncs README results from evidence/scorecard.md; (2) on-save hook only for files matching `.apm/skills/**/SKILL.md` that checks the frontmatter against #docs/apm-notes.md and reports problems without editing.

**T03 prompt:**
> Using #.kiro/steering/contracts.md, write JSON Schemas in schemas/ for log line, deploy event, answer key and evidence output, plus tests/test_schemas.py validating the examples in #HANDOVER.md §5.

**Done when:** tree exists; `git status` does not list the three private docs; a test commit containing `password=FAKE123` is flagged (if gitleaks installed); `pytest -q` passes; first commit pushed (no version tag).

---

### Day 2 — Thu 19 Nov: synthetic data generator

| Task | Model | Mode | Credits |
|---|---|---|---|
| T04 Generator spec | Sonnet 5.5 | **Spec** | 40 |
| T05 Generator: db-pool-exhaustion + bad-deploy | **Haiku 5.5** (escalate: Sonnet 5.5) | Spec tasks | 15 |

**T04 prompt (Spec mode):**
> Create a spec for examples/generator/generate_incident.py from #HANDOVER.md §8, limited to the scenarios in #BUILD_PLAN.md §1. Requirements: deterministic per seed; background traffic; at least two red herrings per scenario; 5–10 obviously fake planted secrets (FAKE- prefix, example.test emails, private IPs); answer.json per scenario; 20k–40k lines; output validates against schemas/. Stop after the spec so I can review it.

**T05:** after approving the spec, **switch the model picker to Haiku 5.5**, then run the spec tasks for the first 2 scenarios only. Ask for these tests: same seed gives identical output; schema validity; unique line_ids; answer evidence line_ids exist; planted secrets exist.

**Done when:** tests pass, and you've read ~50 lines around each fault start and they look realistic.

---

### Day 3 — Fri 20 Nov: remaining data + redaction

| Task | Model | Mode | Credits |
|---|---|---|---|
| T06 cert-expiry, memory-leak, loud-red-herring + SYNTHETIC_DATA.md | Haiku 5.5 (escalate: Sonnet 5.5) | Vibe | 5 |
| T07 Redaction hook + tests | **Sonnet 5.5** (safety-critical) | Vibe | 80 |

**T06 prompt:**
> Add scenarios cert-expiry, memory-leak and loud-red-herring to the generator following the existing pattern. Extend existing tests to all scenarios. Then write SYNTHETIC_DATA.md (fictional ShopSphere app, scenarios, seeds, regeneration command).

**T07 prompt:**
> Implement .apm/hooks/redact-sensitive-data/redact.py per #HANDOVER.md §6.6. Preserve line_id; write redaction-report.json with counts only; strict and standard modes. Tests: every planted secret in every answer.json is absent from the redacted output; non-sensitive fields are unchanged; the report never contains secret values.

**Done when:** all 5 scenarios regenerate with one command; redaction recall is 100% in tests. **Freeze and commit the scenarios.**

---

### Day 4 — Sat 21 Nov: parser skill

| Task | Model | Mode | Credits |
|---|---|---|---|
| T08 Parser spec + scripts + tests | Spec: Sonnet 5.5 → tasks: Haiku 5.5 | **Spec** | 55 |
| T09 log-parser SKILL.md | Haiku 5.5 | Vibe | 1 |

**T08 prompt (Spec mode, Sonnet 5.5; switch to Haiku 5.5 before running the tasks):**
> Create a spec, then implement parse_logs.py, cluster_errors.py, build_timeline.py and get_lines.py per #HANDOVER.md §6.1, JSONL only, working on the redacted folder. Tests: for every scenario, the causal cluster's first error is at or after fault_start; at least one key evidence line appears in cluster samples or the top timeline events; get_lines.py returns exact lines by ID and by range.

**T09 prompt:**
> Write .apm/skills/log-parser/SKILL.md using the frontmatter in #docs/apm-notes.md: run scripts in order, read only their outputs, use get_lines.py for evidence, never read raw logs. Include exact commands and a short example of each output.

**Done when:** tests pass, and `summary.json` for db-pool-exhaustion clearly shows the spike next to config change D012.

---

### Day 5 — Sun 22 Nov: reasoning, writer, agent

| Task | Model | Mode | Credits |
|---|---|---|---|
| T10 failure-patterns.md + rca-reasoning SKILL.md | **Opus 5.5** | **Spec** | 90 |
| T11 postmortem-writer SKILL.md + template | Sonnet 5.5 | Vibe | 40 |
| T12 incident-analyst.agent.md | Sonnet 5.5 | Vibe | 52 |

**T10 prompt (Spec mode, Opus 5.5):**
> Design the rca-reasoning skill per #HANDOVER.md §6.2. Produce (a) reference/failure-patterns.md covering the taxonomy, written as general SRE knowledge in original wording and not tailored to our scenario files, and (b) SKILL.md implementing the 8-step workflow, outputting the evidence.json format, allowing insufficient_evidence, and requiring every hypothesis to cite line_ids fetched with get_lines.py. Optimise for correct reasoning when the noisiest service is not the cause.

**T11 prompt:**
> Write postmortem-writer SKILL.md and the engineering template per #HANDOVER.md §6.3. Outputs: rca.md, timeline.md (Mermaid), postmortem.md, evidence.json. Blameless tone.

**T12 prompt:**
> Write .apm/agents/incident-analyst.agent.md per #HANDOVER.md §6.4 and §7. Pipeline: redact → parse → reason → write → evidence check. Stop with a clear message if logs are missing or unparsable, the time window is empty, or redaction fails. Never read the unredacted folder.

### 🚦 Gate 1 — end of Sun 22 Nov
- [ ] Skills imported into Kiro (Agent Steering & Skills → Import a skill) and visible.
- [ ] In a **new** Kiro chat on **Sonnet 5.5**, the agent runs end to end on db-pool-exhaustion and produces all outputs.
- [ ] Credits used: **≤ 400**.

**If missed:** apply cut list items 1–3 immediately.

---

### Day 6 — Mon 23 Nov: safety, prompts, eval script

| Task | Model | Mode | Credits |
|---|---|---|---|
| T13 Evidence-check hook + tests | Haiku 5.5 (escalate: Sonnet 5.5) | Vibe | 15 |
| T14 Register hooks / document enforcement limits | Haiku 5.5 | Vibe | 1 |
| T15 Two prompt files | Haiku 5.5 | Vibe | 1 |
| T16 Failure-case tests | Haiku 5.5 | Vibe | 2 |
| T17 run_eval.py + tests | Haiku 5.5 (escalate: Sonnet 5.5) | Vibe | 5 |

**T13 prompt:**
> Implement .apm/hooks/evidence-check/check_evidence.py per #HANDOVER.md §6.7 with tests: valid output passes; a nonexistent cited line_id fails; a root-cause sentence without a line reference appears in unverified_claims; no evidence for the top hypothesis gives a non-zero exit code.

**T14 prompt:**
> Using #docs/apm-notes.md, register redact-sensitive-data as a pre-step and evidence-check as a post-step in the supported hook format. If the runtime can't block reading the raw logs folder, enforce it in the agent instructions and write the limitation into docs/limitations.md (public). Add anything newly confirmed to the Status section of docs/apm-notes.md.

**T15 prompt:**
> Write .apm/prompts/investigate-incident.prompt.md (full pipeline) and quick-triage.prompt.md (top hypothesis + evidence, under 10 lines, accepts a symptom text) with parameters from #HANDOVER.md §7.

**T16 prompt:**
> Add tests/fixtures and tests for: empty folder, corrupted JSON lines, logs with no errors, empty time window, missing deploys file. Each script must fail with a clear message, never crash or produce an RCA without evidence.

**T17 prompt:**
> Implement examples/evaluation/run_eval.py per #HANDOVER.md §9 (metrics table), reading runs/<scenario>/<model>-run<N>/evidence.json. Write evidence/scorecard.md and scorecard.json, broken down by model. Add tests/test_eval.py using hand-made fake runs with known scores.

---

### Day 7 — Tue 24 Nov: evaluation and evidence

| Task | Model | Mode | Credits |
|---|---|---|---|
| T18 Eval runs: 5 scenarios × 2 on Sonnet 5.5 | Sonnet 5.5 | new chat per run | ~130 |
| T18b Eval runs: 5 scenarios × 2 on Haiku 5.5 | Haiku 5.5 | new chat per run | ~5 |
| T18c (optional) Eval runs: 5 scenarios × 1 on GPT 5.6 Luna | GPT 5.6 Luna | new chat per run | ~30 |
| T19 Fix general weaknesses | Sonnet 5.5 (Opus 5.5 if stuck) | Vibe | 80 |
| T20 Scorecard + screenshots | — | — | 0 |

- Start a **fresh chat for every run** and use only `/investigate-incident`. Never mention the answer key.
- Save outputs to `runs/<scenario>/<model>-run<N>/`, e.g. `sonnet55-run1`, `haiku55-run2`, `gpt56luna-run1`. Time each run.
- **Before running the agent**, do the manual baseline yourself on 2 scenarios, timed, and record it in `examples/evaluation/manual_baseline.md`.
- **Watch the first two Sonnet runs' credit cost.** If a run costs more than ~15 credits, drop to 1 Sonnet run per scenario.
- T19: fix general problems only, not scenario-specific hints. Re-run only the affected scenarios and note what changed and why.
- Comparing Sonnet 5.5 (1.3x) with Haiku 5.5 (0.06x), and optionally GPT 5.6 Luna, gives strong evidence: accuracy vs cost per RCA. If Haiku 5.5 scores close to Sonnet, that is a headline result for adoption ("runs at about 1/20th of the cost").

**Screenshots to take:** prompt being run, `rca.md` with evidence lines, `postmortem.md`, `redaction-report.json`, evidence-check catching a bad claim, `pytest` passing, `scorecard.md`, Kiro specs and steering folder (for "Built with Kiro"). Make sure no private doc is visible in any screenshot.

---

### Day 8 — Wed 25 Nov: finish and publish

| Task | Model | Mode | Credits |
|---|---|---|---|
| T21 Final quality review (read-only) | **Opus 5.5** | Vibe | 30 |
| T22 README final | Haiku 5.5 (via manual hook) | Vibe | 1 |
| T23 Demo video | — | — | 0 |
| T24 Publish | — | — | 0 |

**T21 prompt (Opus 5.5):**
> Review this repository against #HANDOVER.md §2 (rules and scoring). Don't edit files. List: any data-rule risks, README sections missing or inaccurate, claims not backed by evidence/scorecard.md, any reference to HANDOVER.md, BUILD_PLAN.md or docs/apm-notes.md in tracked files, and the 5 highest-value fixes ordered by impact. Keep the answer under 40 lines.

Apply only quick, high-value fixes from that list (Haiku or Sonnet).

**T22:** trigger the `update-readme-from-scorecard` hook, then check that the README lists **only the tested models** (Sonnet 5.5, Haiku 5.5, plus GPT 5.6 Luna if run), includes limitations (JSONL only, synthetic validation, hook enforcement notes), a "Using in Kiro" section (import skills step), a "How this fits with your observability stack" section, and has all rulebook sections.

**T23 demo (3–5 min):** problem (20s) → scenario with hidden answer key (20s) → run `/investigate-incident` live (90s) → RCA with evidence lines (45s) → redaction report + evidence check catching a bad claim (30s) → scorecard, Sonnet vs Haiku, and time saved vs manual (30s) → limitations (15s). Record it twice and keep the better take.

**T24 publish checklist:**
- [ ] `pytest -q` passes; gitleaks clean.
- [ ] No real data, keys, hostnames or company names in the repo.
- [ ] `git ls-files` does not list HANDOVER.md, BUILD_PLAN.md or docs/apm-notes.md.
- [ ] Remove the `hello-incidentlens` test skill.
- [ ] Set `version: 1.0.0` in apm.yml; commit; `git tag v1.0.0`; `git push origin main --tags`.
- [ ] Update the portal entry (description without "preview", tags, business line) and submit.
- [ ] Search the catalog to confirm it is visible.
- [ ] Fresh install in a new folder, import skills into Kiro, then run quick-triage on one scenario.

### Thu 26 Nov — buffer only
Fix anything broken by the fresh install test. No new features.

---

## 6. Cut list (apply in order if behind)

1. Drop the GPT 5.6 Luna eval runs.
2. Reduce Sonnet eval to 1 run per scenario, plus 1 repeat run on db-pool-exhaustion to show repeatability.
3. Drop `/quick-triage` (keep `/investigate-incident`).
4. Drop the Opus 5.5 final review (T21); use the README checklist instead.
5. Drop the `loud-red-herring` scenario.
6. Drop failure-case tests to 3 cases (empty folder, corrupted lines, no errors).

---

## 7. Credit tracker (1,000 total)

| Day | Planned | Cumulative | Actual |
|---|---|---|---|
| 1 Wed 18 | 3 | 3 | |
| 2 Thu 19 | 55 | 58 | |
| 3 Fri 20 | 85 | 143 | |
| 4 Sat 21 | 56 | 199 | |
| 5 Sun 22 | 182 | 381 | |
| 6 Mon 23 | 24 | 405 | |
| 7 Tue 24 | 245 | 650 | |
| 8 Wed 25 | 31 | 681 | |
| Escalation reserve (Haiku → Sonnet → Opus) | 200 | 881 | |
| Buffer | 119 | 1,000 | |

**Where the credits go:** Sonnet 5.5 about 60%, Opus 5.5 about 15%, Haiku 5.5 under 5% despite doing most of the tasks, GPT 5.6 Luna about 5%, reserve the rest.
**Rule:** if actual usage is more than 15% over cumulative plan at any day end, apply the next cut list item.

---

## 8. "Built with Kiro" evidence to collect along the way

- `.kiro/steering/` (4 files) and `.kiro/specs/` (generator, parser, rca-reasoning): screenshot them, and keep them in the repo as build evidence.
- The two agent hooks and what they do.
- Model strategy: Sonnet 5.5 writes specs, Haiku 5.5 implements them, Opus 5.5 only for the RCA reasoning design and final review. This is a good talking point for the Kiro form answer and the demo.
