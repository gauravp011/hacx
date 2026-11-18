# BUILD_PLAN v3 — IncidentLens master plan

> **Owner:** Stanley Correia (solo). **Build tool:** Kiro IDE, 1,000 credits. **Publish:** Wed 25 Nov 2026, Thu 26 Nov buffer. **Official deadline:** 7 Dec 2026 23:59 CET.
> **This file is the single plan Kiro follows.** HANDOVER.md holds background, rules and detailed specs. **Where this file and HANDOVER.md differ, this file wins** (see §2.6 for the list of overrides).
> **PRIVATE:** this file, HANDOVER.md and docs/apm-notes.md are git-ignored. Never commit them, quote them in README.md, or reference them from anything under `.apm/`.
>
> **How the owner uses this file:** open a new Kiro chat, pick the model and mode shown for the task, and type only:
> `Do T<nn> from #BUILD_PLAN.md`
> Then check the task's **Done when** list, run `pytest -q`, commit, and tick the tracker in §11.

---

## 0. Rules for Kiro (read before every task)

1. When asked "Do T<nn>": read §0, §2, §3, the T<nn> block, and only the HANDOVER/apm-notes sections that block cites. Do not read other task blocks.
2. Do exactly that task, then stop. Never start the next task.
3. Finish with a report of **10 lines or fewer**: files created/changed, tests added, test result if you ran them, open questions.
4. **Never open scenario log files** (`examples/scenarios/*/logs/*.jsonl`) in chat or with `#File`/`#Folder`. They are 15k–40k lines. Only scripts and tests read them. To inspect data, write or run a small script that prints a summary or at most 20 lines.
5. **Never read `answer.json` files** except in generator, evaluation and test tasks (T04–T06, T18, T19).
6. Shipped code (anything under `.apm/`) must use the **Python 3.10+ standard library only**. Dev-only code (generator, eval, tests) may use `pyyaml`, `jsonschema`, `pytest`.
7. Windows-safe Python: use `pathlib`, always `open(..., encoding="utf-8")`, never shell-specific commands inside scripts, `newline=""` where writing CSV/JSONL by hand.
8. Ask before adding any dependency, account, key or network call. There are no network calls anywhere in this project.
9. Use only synthetic data: fictional systems ShopSphere and FleetSense, `example.test` emails, private IPs, `FAKE-` tokens, well-known test card numbers.
10. If a spec already exists in `.kiro/specs/` for the task, **update it** rather than creating a new one.
11. If something in this plan is impossible or contradicts the APM docs, stop and say so. Don't improvise around it.

---

## 1. Status and final scope

### 1.1 Done
| Item | Result |
|---|---|
| APM CLI installed; `apm init` done | `apm.yml` at repo root, version 0.1.0 |
| v0.1.0 test release | `hello-incidentlens` skill, tagged, published, visible in portal |
| T01 skeleton, T02 steering + 2 Kiro hooks, T03 schemas + tests | `pytest` green. Day 1 used 0.64 credits |
| T04 generator spec | **In progress** (requirements stage). Accepted decisions: trigger_event_id set in YAML and nullable for cert-expiry; no Faker; secrets from fixed patterns + seeded RNG |

### 1.2 Final scope (v3)
| Must have | Should have | Could have |
|---|---|---|
| 6 taxonomy scenarios + `loud-red-herring` hard variant | `fleet-firmware-crash` (embedded) scenario; `quiet-day` control scenario | `overlapping-changes` hard variant |
| Skills: redact-logs, log-parser, rca-reasoning, postmortem-writer, evidence-check, run-incident-analysis | `render_report.py` HTML report; `convert_logs.py` multi-format input | Executive post-mortem template |
| Agent `incident-analyst` + prompt `/investigate-incident` | Prompt `/quick-triage`; `doctor.py`; APM hook files | GPT 5.6 Luna eval runs |
| Eval: `prepare_eval.py`, `record_run.py`, `run_eval.py`, scorecard | 2nd Sonnet run on 3 scenarios (repeatability) | |
| README, demo video, published v1.0.0 | | |

**Never cut:** redaction, evidence check, eval scorecard from real runs, README rulebook sections, demo, publishing.

---

## 2. Package design v3

### 2.1 Repository layout
```
incidentlens/
├── README.md                    # public, consumer-facing
├── apm.yml                      # name incidentlens; version bumped only at release
├── SYNTHETIC_DATA.md            # public
├── requirements-dev.txt         # pyyaml, jsonschema, pytest (dev only; the package itself needs nothing)
├── .gitignore                   # see 2.5
├── HANDOVER.md, BUILD_PLAN.md   # PRIVATE, git-ignored
├── docs/
│   ├── apm-notes.md             # PRIVATE, git-ignored
│   └── limitations.md           # public
├── schemas/                     # JSON Schemas (dev/tests)
├── .kiro/
│   ├── steering/                # committed (Built-with-Kiro evidence)
│   ├── specs/                   # committed (Built-with-Kiro evidence)
│   └── hooks/                   # our 2 dev hooks committed; APM-deployed hook files git-ignored
├── .apm/                        # ← ONLY this ships to consumers
│   ├── skills/
│   │   ├── redact-logs/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/redact.py
│   │   ├── log-parser/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── convert_logs.py
│   │   │       ├── parse_logs.py
│   │   │       ├── cluster_errors.py
│   │   │       ├── build_timeline.py
│   │   │       └── get_lines.py
│   │   ├── rca-reasoning/
│   │   │   ├── SKILL.md
│   │   │   └── references/failure-patterns.md
│   │   ├── postmortem-writer/
│   │   │   ├── SKILL.md
│   │   │   ├── assets/postmortem-engineering.md
│   │   │   └── scripts/render_report.py
│   │   ├── evidence-check/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/check_evidence.py
│   │   ├── run-incident-analysis/
│   │   │   ├── SKILL.md         # workflow skill: the pipeline, works in every runtime that supports skills
│   │   │   └── scripts/doctor.py
│   │   └── hello-incidentlens/  # test skill, DELETE at release (T25)
│   ├── agents/incident-analyst.agent.md
│   ├── prompts/
│   │   ├── investigate-incident.prompt.md
│   │   └── quick-triage.prompt.md
│   └── hooks/                   # Should-have, T16 (only if verified)
├── examples/
│   ├── generator/{generate_incident.py, scenarios.yaml}
│   ├── scenarios/<scenario>/{logs/*.jsonl, deploys.json, service_map.json, answer.json}
│   └── evaluation/{prepare_eval.py, record_run.py, run_eval.py, manual_baseline.md}
├── runs/<scenario>/<model>-run<N>/   # committed samples only
├── evidence/                    # scorecard.md, scorecard.json, screenshots/, demo link
└── tests/
```

### 2.2 Skills (APM rules: folder name = `name`, lowercase-hyphen, `SKILL.md` < 500 lines, description starts with "Use when …", extra material goes in `references/`, `assets/`, `scripts/`)

| Skill | Role | Scripts |
|---|---|---|
| `redact-logs` | Safety step 1. Masks secrets/PII into `<output_dir>/work/redacted/`, writes counts-only report | `redact.py` |
| `log-parser` | Deterministic facts. Converts input format, parses, clusters, builds timeline, fetches evidence lines | `convert_logs.py`, `parse_logs.py`, `cluster_errors.py`, `build_timeline.py`, `get_lines.py` |
| `rca-reasoning` | LLM reasoning over parser outputs using the failure-pattern library | none (uses `../log-parser/scripts/get_lines.py`) |
| `postmortem-writer` | Writes rca.md, timeline.md, postmortem.md, evidence.json, report.html | `render_report.py` |
| `evidence-check` | Safety step 2. Validates evidence.json, cited line IDs, unsupported claims, secret leaks in outputs | `check_evidence.py` |
| `run-incident-analysis` | Workflow skill: runs the 5 skills in order, handles parameters and failure stops; `mode: full` or `triage` | `doctor.py` |

**Cross-skill paths:** all skills are installed side by side (`.kiro/skills/`, `.agents/skills/`, …), so a skill refers to another skill's script as `../<skill>/scripts/<file>.py`, relative to its own folder. `doctor.py` verifies all siblings exist.

### 2.3 Entry points by runtime
| Runtime | How the user starts it |
|---|---|
| Kiro | `/run-incident-analysis` (skill), or the `incident-analyst` agent, or `/investigate-incident` if Kiro exposes APM prompts (VERIFY in V1) |
| Copilot / Claude / Cursor / others | `/investigate-incident` or `/quick-triage` prompt, the agent, or the workflow skill, depending on what the runtime supports |

The agent and prompts are **thin**: they set parameters and say "follow the run-incident-analysis skill". All logic lives in skills, so there is one source of truth.

### 2.4 Outputs (default `output_dir = ./incident-report`)
`rca.md`, `timeline.md` (Mermaid), `postmortem.md`, `evidence.json`, `report.html`, `redaction-report.json`, `evidence-check.json`, and `work/` (redacted logs, parsed.jsonl, clusters.json, timeline.json, summary.json).

### 2.5 .gitignore (complete list)
`HANDOVER.md`, `BUILD_PLAN.md`, `docs/apm-notes.md`, `.kiro/skills/`, `.kiro/agents/`, `.kiro/prompts/`, APM-deployed hook files under `.kiro/hooks/` (exact pattern from V1), `apm_modules/`, `incident-report/`, `eval-workspace/`, `.env`, `__pycache__/`, `.pytest_cache/`. Keep `runs/` tracked so sample runs can be committed.

### 2.6 Overrides of HANDOVER.md
| HANDOVER says | v3 says |
|---|---|
| §3/§6.6–6.7: redaction and evidence-check are hooks under `.apm/hooks/` | They are **skills** with scripts (they work in every runtime). APM hook files are optional wrappers (T16) |
| §6.2 `reference/failure-patterns.md` | `references/failure-patterns.md` (APM/agent-skills convention) |
| §6.3 `templates/` | `assets/` |
| §10 pandas, faker, drain3 | Shipped scripts: stdlib only. Clustering = regex template masking. Faker not used |
| §5.3 `service_map.yaml` | `service_map.json` for generated scenarios (stdlib-readable). Parser also accepts the simple YAML form `key: [a, b]` with a tiny built-in parser |
| §8 scenarios / BUILD_PLAN v2 4+1 | §4 of this file (9 scenarios across 2 fictional systems) |
| Prompts `/write-postmortem` | Dropped. `/quick-triage` kept as Should-have |
| Manual Kiro skill import | `apm install --target kiro` once V1 confirms it; manual import is the fallback |

---

## 3. Contract amendments (on top of HANDOVER §5)

- **Log line:** unchanged. Embedded logs use the same fields; device/gateway name goes in `host`, firmware version may appear in `msg`.
- **Answer key:** `trigger_event_id` is `string | null`. `root_cause_id` may be `"NONE"` (only for the `quiet-day` control). `root_cause_service` may be `null` when `root_cause_id` is `"NONE"`. Add `system` (`shopsphere` | `fleetsense`) and `difficulty` (`standard` | `hard` | `control`).
- **Evidence output:** add optional `red_herrings_considered: [{ "line_ids": [...], "reason": "..." }]` and optional `affected_hosts: [...]`.
- **Run metadata (new, `runs/<scenario>/<model>-run<N>/meta.json`):** `{scenario, model, run, started_at, minutes, credits, kiro_mode}` (minutes and credits entered by the owner).
- **Evidence-check result (new, `evidence-check.json`):** `{passed: bool, invalid_line_ids: [], unverified_claims: [], leaked_secret_categories: []}`. Never contains secret values.
- **Input formats (`convert_logs.py --format`):** `auto` (default), `jsonl`, `plain` (`<ts> <level> <service> <msg>`), `cloudwatch` (CloudWatch Logs export JSON), `datadog` (Datadog log export JSON), `ecs` (Elastic ECS NDJSON). Field mappings are best-effort and documented in the log-parser SKILL.md; a `--map mapping.json` option overrides them.

---

## 4. Scenario catalogue

### 4.1 Fictional systems (defined in `scenarios.yaml` under `systems:`)
- **ShopSphere** (web shop): `api-gateway`, `order-service`, `payment-service`, `inventory-service`, stubs `orders-db`, `inventory-db`, `payment-provider-stub`. Map: api-gateway→[order-service, inventory-service]; order-service→[payment-service, inventory-service, orders-db]; payment-service→[payment-provider-stub]; inventory-service→[inventory-db].
- **FleetSense** (embedded cold-chain truck telemetry): `sensor-node` (hosts sn-001…sn-040), `edge-gateway` (hosts gw-01…gw-04), `telemetry-ingest`, `fleet-api`, stub `telemetry-db`. Map: sensor-node→[edge-gateway]; edge-gateway→[telemetry-ingest]; telemetry-ingest→[telemetry-db]; fleet-api→[telemetry-db].

### 4.2 Scenarios (one seed each, fixed forever once frozen)
| # | Scenario | System | Tier | root_cause_id | Trigger | Causal signature | Downstream / symptom | Red herrings (≥2) |
|---|---|---|---|---|---|---|---|---|
| 1 | `db-pool-exhaustion` | ShopSphere | Must | DB_POOL_EXHAUSTION | config: order-service pool 50→5 | pool acquire timeouts in order-service | gateway 503s on checkout | 404 burst on /static; one-off retry WARN in inventory |
| 2 | `bad-deploy` | ShopSphere | Must | BAD_DEPLOY_CODE_ERROR | deploy inventory-service v3.8.0 | NullPointer-style errors on one endpoint | order failures for some SKUs | slow-query WARNs in orders-db; payment retry blip |
| 3 | `memory-leak` | ShopSphere | Must | MEMORY_LEAK | deploy payment-service v5.2.0 | rising heap WARNs, OOM kills, restarts every ~12 min | intermittent payment timeouts | GC pause WARN in order-service; 404s |
| 4 | `cert-expiry` | ShopSphere | Must | CERT_EXPIRY | **none** (time-based, trigger null) | TLS handshake failures to payment-provider-stub at a sharp time | all payments fail | unrelated deploy 40 min earlier with no effect; 404s |
| 5 | `dependency-latency` | ShopSphere | Must | DEPENDENCY_LATENCY | infra event on payment-provider-stub | rising upstream latency, retries, circuit breaker opens | slow checkout, retry storm | inventory cache-miss WARNs; 404s |
| 6 | `disk-full` | ShopSphere | Must | DISK_FULL | config: inventory-service log level → DEBUG | DEBUG flood, then write failures "No space left on device" | inventory-service crash loop | order-service retry WARNs; payment latency blip |
| 7 | `loud-red-herring` | ShopSphere | Must (hard) | DB_POOL_EXHAUSTION in **inventory-service** | config: inventory-service pool change | pool timeouts in inventory-service (moderate volume) | order failures | **api-gateway 429 flood from a misbehaving client, starting 20 min earlier and 10× louder** |
| 8 | `fleet-firmware-crash` | FleetSense | Should | BAD_DEPLOY_CODE_ERROR in edge-gateway | deploy: OTA firmware v3.2.0 to **gw-02 and gw-03 only** | decoder error "unhandled frame type 0x1F", task restarts, watchdog resets (FATAL) on gw-02/03 | ingest "no heartbeat from gw-02/gw-03", fleet-api stale-telemetry WARNs | sensor battery-low WARNs (constant); fleet-api slow query burst earlier |
| 9 | `quiet-day` | ShopSphere | Should (control) | NONE | one harmless deploy | none | none | 3 benign bursts. Correct answer = `insufficient_evidence` or rank-1 `UNKNOWN` with low confidence |
| 10 | `overlapping-changes` | ShopSphere | Could (hard) | DB_POOL_EXHAUSTION | two config changes 4 min apart, only one causal | pool timeouts | 503s | the non-causal change |

Every scenario: 15k–40k lines, 60–120 min, background INFO traffic with realistic latency, 5–10 planted fake secrets covering **every** redaction category (§T07), answer.json with key evidence line IDs taken from lines actually generated.

---

## 5. Models, modes and credit rules

| Model | Multiplier | Use for |
|---|---|---|
| Claude Haiku 5.5 | 0.06x | Default. Boilerplate, scripts with a clear spec, tests, docs, spec task execution |
| Claude Sonnet 5.5 | 1.3x | Specs, safety-critical code (redaction), skill/agent instructions, main eval runs, escalations |
| Claude Opus 5.5 | 2x | Only T11 (RCA reasoning design), T23 (final review), and one-shot escalations after Sonnet fails twice |
| GPT 5.6 Luna | 0.6x | Optional cross-vendor eval runs, only if approved |

- **Sonnet plans, Haiku builds:** write specs on Sonnet, switch the model picker to Haiku before running spec tasks.
- **Escalation:** Haiku fails twice → Sonnet. Sonnet fails twice → Opus once with the exact failure. Then back down.
- New chat per task. Point to files with `#File`; don't paste. Run `pytest -q` yourself and paste only failures. Supervised mode for T04, T05, T07, T08, T11; Autopilot is fine for Haiku tasks.
- Kiro dev hooks: keep exactly the 2 from T02. Disable the on-save hook during heavy SKILL.md editing.
- Check credits at the end of each day (§11). If more than 15% over the cumulative plan, apply the next cut (§10).

---

## 6. Tasks

### V1 — Verify APM → Kiro deployment (owner, 0 credits, 10 min, do before T03b)
In Kiro's terminal at the repo root:
1. `apm install --dry-run --target kiro` → does it list `.apm/skills/hello-incidentlens` going into `.kiro/skills/`? Note the exact paths it prints for skills, agents, prompts and hooks.
2. `apm audit --file .apm/skills/hello-incidentlens/SKILL.md` → note the result.
3. If step 1 lists our skill: run `apm install --target kiro`, open a new chat, type `/hello-incidentlens`. Expected: "IncidentLens is installed."
4. Record results in `docs/apm-notes.md` → Status. **If it works, the dev loop for all later tasks is: edit `.apm/` → `apm install --target kiro` → test in a new Kiro chat.** If not, keep manual import.

### T03b — Align foundation with v3 (Haiku 5.5, Vibe, ~1 credit)
**Kiro instructions:**
- Update `.kiro/steering/structure.md` to the layout in §2.1 and the skills table in §2.2.
- Update `.kiro/steering/rules.md`: add §0 rules 4–9 of this file.
- Update `.kiro/steering/style.md`: Python 3.10+ for shipped code, stdlib only under `.apm/`, Windows-safe rules (§0.7).
- Update `.kiro/steering/contracts.md` and `schemas/` with §3 (nullable trigger_event_id, `NONE` root cause, `system`, `difficulty`, `red_herrings_considered`, `affected_hosts`, meta.json, evidence-check.json). Extend `tests/test_schemas.py` for each change.
- Rename `requirements.txt` → `requirements-dev.txt` with only `pyyaml`, `jsonschema`, `pytest`.
- Update `.gitignore` to §2.5.
- Create empty skill folders from §2.1 with a one-line TODO `SKILL.md` each (valid frontmatter: `name` = folder, `description` starting "Use when").
- Do not touch `apm.yml` or `hello-incidentlens`.

**Done when:** `pytest -q` passes; `git status` shows no private docs; `apm audit` passes on each new SKILL.md (owner runs it).

### Day 2 — Thu 19 Nov: generator

#### T04 — Generator spec (Sonnet 5.5, **Spec**, Supervised, ~40 credits)
**Kiro instructions:** update the existing generator spec (or create it) for `examples/generator/generate_incident.py` + `examples/generator/scenarios.yaml`:
- Data-driven: systems (§4.1) and scenarios (§4.2, rows 1–9; row 10 optional) defined in YAML. A new scenario needs YAML only, no code.
- Keep the accepted decisions in §1.1 (no Faker, nullable trigger, secrets from fixed patterns + seeded RNG).
- Determinism: one `random.Random(seed)` instance passed everywhere; fixed base timestamp `2026-11-20T09:00:00Z`; no `datetime.now()`, no global random, no hash-order dependence.
- `line_id`: global counter `L000001…` across all services, assigned after sorting all lines by timestamp; ties broken deterministically.
- Fault model per scenario: trigger event (or none), onset delay, causal signature lines, cascade with plausible delays, recovery or not; host targeting (e.g. only gw-02/gw-03).
- Red herrings: ≥2 per scenario, at least one before the fault and one overlapping it; recorded in answer.json.
- Planted secrets: 5–10 per scenario covering every category listed in T07; recorded in answer.json.
- answer.json key evidence IDs = IDs of lines actually emitted (first causal error, peak causal error, first downstream symptom, trigger-adjacent line).
- Outputs: `logs/<service>.jsonl`, `deploys.json`, `service_map.json`, `answer.json`; all validate against `schemas/`.
- CLI: `python examples/generator/generate_incident.py --scenario <id>|all [--out examples/scenarios]`. Each scenario generates in < 30 s.
- Tasks must be split so the engine + scenarios 1–2 can be built and tested first, then each further scenario is its own task.
- Tests: same seed → byte-identical output; schema-valid; unique, ordered line_ids; answer evidence IDs exist in logs; every planted secret appears in logs; red-herring IDs exist; line count within range.
Stop after the spec for owner review.

**Owner review checklist:** all bullets above are present in requirements/design; tasks are split per scenario.

#### T05 — Generator engine + scenarios 1–2 (Haiku 5.5, Spec tasks, Supervised, ~15 credits)
Switch model to **Haiku 5.5**. Run the spec tasks for the engine and `db-pool-exhaustion`, `bad-deploy` only.
**Done when:** tests pass; owner runs a summary script (Kiro may write `examples/generator/peek.py` that prints counts per level/service per 5 minutes plus 20 lines around fault start) and the fault looks plausible.

### Day 3 — Fri 20 Nov: all data + redaction

#### T06 — Scenarios 3–9 + SYNTHETIC_DATA.md (Haiku 5.5, Spec tasks, ~10 credits; escalate to Sonnet if one fails twice)
**Kiro instructions:** run the remaining spec tasks for scenarios 3–9 (10 only if time). Extend tests to all scenarios. Write public `SYNTHETIC_DATA.md`: the two fictional systems, scenario table (name, system, difficulty, trigger, symptom; **not** the root cause answers in a way that would leak to an agent reading the README — keep it to a short description), seeds, regeneration command, the rule that no real data is used.
**Done when:** `python examples/generator/generate_incident.py --scenario all` regenerates everything identically; tests green.

#### T07 — redact-logs skill (Sonnet 5.5, Vibe, Supervised, ~80 credits)
**Kiro instructions:** implement `.apm/skills/redact-logs/scripts/redact.py` and its `SKILL.md`, per HANDOVER §6.6 with these specifics:
- CLI: `redact.py <logs_dir> <out_dir> [--mode strict|standard]`. Reads `*.jsonl` (and plain text after conversion). Writes redacted copies with identical file names and line order, plus `<out_dir>/../redaction-report.json` (counts per category, files processed, mode; never values).
- Categories: EMAIL, IPV4, IPV6, BEARER_TOKEN, JWT, KEY_VALUE_SECRET (`password=`, `passwd=`, `secret=`, `api_key=`, `apikey=`, `token=`, `authorization:`), HEX_SECRET (≥32 hex chars), BASE64_SECRET (≥40 chars), CARD_NUMBER (13–19 digits passing Luhn). Replacement `[REDACTED:<CATEGORY>]`.
- Never redact: `line_id`, `ts`, `level`, `service`, `trace_id` (8–16 hex), version strings like `v2.4.1`, durations, HTTP status codes, ports.
- `strict` (default) also redacts all IPs including private ranges and any `@` email-like string; `standard` keeps private IPs. No "off" mode.
- Exit non-zero with a clear message if input is missing/unreadable; never write partial output silently.
- Stdlib only. `SKILL.md`: when to use, exact command, what it guarantees, what it doesn't (limitations).
- Tests: every planted secret in every answer.json is absent from redacted output; each category has positive and negative (false-positive) cases; non-sensitive fields unchanged; report contains no secret values; line_ids preserved 1:1.
**Done when:** redaction recall 100% across all scenarios in tests; false-positive tests pass. **Freeze scenarios: commit them and never regenerate after this point.**

### 🚦 Gate 0 — end of Fri 20 Nov
- [ ] Scenarios 1–7 (and 8–9 if done) generated, committed, frozen.
- [ ] Redaction recall 100% in tests.
- [ ] Credits used ≤ 160.

### Day 4 — Sat 21 Nov: parser

#### T08 — Parser spec + scripts (Spec on Sonnet 5.5 → tasks on Haiku 5.5, Supervised, ~55 credits)
**Kiro instructions:** spec, then implement `parse_logs.py`, `cluster_errors.py`, `build_timeline.py`, `get_lines.py` under `.apm/skills/log-parser/scripts/`, per HANDOVER §6.1 with these specifics:
- All operate on the **redacted** folder; refuse to run on a folder not produced by redact.py (check for `redaction-report.json` next to it) unless `--i-know-unredacted` is passed (for tests only; the skill never passes it).
- `parse_logs.py`: JSONL in → `work/parsed.jsonl` normalised; `--min-severity` (default WARN), `--time-window` ISO interval; keeps all lines available for `get_lines.py`.
- `cluster_errors.py`: regex template masking (numbers, hex IDs, UUIDs, quoted strings, host suffixes) → `clusters.json` with template, count, services, hosts, first/last seen, 3 sample line_ids. Stdlib only.
- `build_timeline.py`: per-minute counts per service and level; spike detection (count > baseline mean + 3σ over the first 20% of the window, min 5 events); merge `deploys.json`; first error per cluster; **per-host breakdown for spiking clusters**; top-20 events → `timeline.json`; compact `summary.json` (< 200 lines) listing services by first-anomaly time and by volume, separately.
- `get_lines.py --ids L1,L2` or `--range L004200:L004240` or `--around L004217 --n 5` → exact redacted lines.
- Service map: read `service_map.json`, or simple YAML `key: [a, b]` via a tiny built-in parser.
- Clear exit codes and messages for: empty folder, corrupted lines (skip and count them; fail if > 5%), no errors found, empty time window.
- Tests: for every scenario the causal cluster's first error is at/after fault_start; ≥1 key evidence line appears in cluster samples or top timeline events; summary lists the true root service's first anomaly before its downstream services; get_lines exact by ID/range/around; failure cases above.

#### T09 — convert_logs.py (Haiku 5.5, Vibe, ~3 credits)
**Kiro instructions:** implement `.apm/skills/log-parser/scripts/convert_logs.py` per §3 input formats. Output our JSONL with fresh global `line_id`s in time order, one file per service. Unknown fields go into `msg` suffix as `key=value`. Add small **synthetic** fixtures in `tests/fixtures/formats/` for each format (fictional values only) and tests. Document the field mapping table in a comment block for T10 to copy.

#### T10 — log-parser SKILL.md (Haiku 5.5, Vibe, ~1 credit)
**Kiro instructions:** write `.apm/skills/log-parser/SKILL.md`: description "Use when …"; exact command sequence (convert if needed → parse → cluster → timeline); read only outputs; use get_lines.py for evidence; never open raw or redacted log files directly; input-format mapping table; one short example of each output. < 300 lines.
**Done when (Day 4):** tests green; owner checks `summary.json` for db-pool-exhaustion shows the spike right after D-event and for loud-red-herring lists the 429 flood as loudest but not as first anomaly in the affected service chain.

### Day 5 — Sun 22 Nov: reasoning, safety, writer, workflow

#### T11 — rca-reasoning (Opus 5.5, **Spec**, ~90 credits)
**Kiro instructions:** design and write `.apm/skills/rca-reasoning/SKILL.md` and `references/failure-patterns.md` per HANDOVER §6.2, plus:
- failure-patterns.md: general SRE knowledge in original wording for DB_POOL_EXHAUSTION, BAD_DEPLOY_CODE_ERROR, MEMORY_LEAK, CERT_EXPIRY, DEPENDENCY_LATENCY, DISK_FULL, UNKNOWN; each with signatures, typical triggers, how to tell it apart from look-alikes, embedded/device variants, typical remediation. **Must not mention our scenario names, services, line IDs or seeds.**
- Reasoning order: symptom → walk service map upstream → **earliest anomaly in the affected chain, not the loudest anomaly overall** → correlate with change events ±15 min → check host scope (partial rollouts) → match patterns → five whys on the top hypothesis.
- Every hypothesis cites line IDs fetched with `../log-parser/scripts/get_lines.py`; record rejected red herrings in `red_herrings_considered` with reasons.
- Return `insufficient_evidence` when no anomaly stands out from baseline or evidence conflicts; never invent a cause (the `quiet-day` control tests this).
- Output evidence.json per HANDOVER §5.5 + §3 amendments.
- Keep SKILL.md < 400 lines; put examples in references/.

#### T12 — evidence-check skill (Haiku 5.5, Vibe, ~15 credits; escalate to Sonnet)
**Kiro instructions:** implement `.apm/skills/evidence-check/scripts/check_evidence.py <output_dir>` + SKILL.md per HANDOVER §6.7, plus: stdlib structural validation of evidence.json (no jsonschema at runtime); every cited line_id exists in `work/redacted/`; root-cause sentences in rca.md/postmortem.md without a `L\d{6}` reference go to `unverified_claims`; **leak scan**: run the redaction detectors (import from `../redact-logs/scripts/redact.py`) over all output files and report categories found; write `evidence-check.json`; exit non-zero if top hypothesis has no valid evidence or any leak is found. Tests for each rule.

#### T13 — postmortem-writer (Sonnet 5.5, Vibe, ~40 credits)
**Kiro instructions:** write `.apm/skills/postmortem-writer/SKILL.md` and `assets/postmortem-engineering.md` per HANDOVER §6.3 (engineering template only; executive optional). Outputs rca.md, timeline.md (Mermaid `timeline` or `gantt`), postmortem.md, evidence.json. Blameless tone. Every root-cause statement carries line IDs. Mention that report.html is produced by `scripts/render_report.py` (built in T15).

#### T14 — Workflow skill, agent, prompts, doctor (Sonnet 5.5 for SKILL/agent; Haiku 5.5 for doctor/prompts; ~60 credits)
**Kiro instructions:** read #docs/apm-notes.md (frontmatter rules) first.
- `.apm/skills/run-incident-analysis/SKILL.md`: parameters (HANDOVER §7 + `input_format`, + `mode: full|triage`, + `symptom`); steps: doctor → redact-logs → log-parser → rca-reasoning → postmortem-writer → render_report (if present) → evidence-check; stop rules (no logs, unparsable, empty window, redaction failed, evidence-check failed → report clearly, never continue on unredacted data); triage mode = redact + parse + top hypothesis with evidence, ≤ 10 lines, no post-mortem.
- `scripts/doctor.py`: checks Python ≥ 3.10, sibling skills present, logs path readable, format detectable, output dir writable; prints PASS/FAIL with a one-line fix each; exit code.
- `.apm/agents/incident-analyst.agent.md`: frontmatter `description` (required), `tools` limited to read, write, shell (Kiro capability tags: `read`, `write`, `shell`); body: persona + "follow the run-incident-analysis skill"; read-only on systems, no network.
- `.apm/prompts/investigate-incident.prompt.md` and `quick-triage.prompt.md`: frontmatter only `description`, `argument-hint`, `input` (APM keeps only description, allowed-tools, model, argument-hint, input); body invokes the workflow skill with `$`-parameters.
**Done when:** owner runs `apm install --dry-run --target kiro` and `apm audit` on each file without errors.

### 🚦 Gate 1 — end of Sun 22 Nov
- [ ] `apm install --target kiro` (or manual import) makes all 6 skills visible in Kiro.
- [ ] New Kiro chat, **Sonnet 5.5**: `/run-incident-analysis logs=examples/scenarios/db-pool-exhaustion/logs deploys=… service_map=…` produces all outputs and evidence-check passes. (Repo-internal smoke test only; real eval happens in the clean workspace, §8.)
- [ ] Credits used ≤ 450. **If missed:** apply cuts 1–3 now.

### Day 6 — Mon 23 Nov: report, hooks, eval tooling

#### T15 — render_report.py (Haiku 5.5, Vibe, ~5 credits; escalate to Sonnet)
**Kiro instructions:** `.apm/skills/postmortem-writer/scripts/render_report.py <output_dir>` → single self-contained `report.html`: header (incident window, top hypothesis, confidence, evidence-check badge); inline **SVG** chart of per-minute errors per service with deploy markers and the fault window shaded; ranked hypotheses as cards; evidence lines (from get_lines) in `<details>` blocks; red herrings considered; redaction counts; links to the md files. No JavaScript required, no external URLs, no fonts from the web, light/dark friendly CSS, opens offline. Stdlib only. Tests: file produced; contains every cited line_id; contains no `http://`/`https://` resource loads; passes the leak scan.

#### T16 — APM hook files (Haiku 5.5, Vibe, ~5 credits) — Should-have
**Kiro instructions:** read #docs/apm-notes.md (hooks section). Create `.apm/hooks/evidence-gate.json` on the `Stop`/`agentStop` event running `./evidence-gate/run.py`, which finds `incident-report/` in the working directory and runs check_evidence (locating the installed evidence-check skill among sibling skill folders; no-op with a message if none). Only add a PreToolUse guard for raw-log reads if the docs confirm blocking semantics for Kiro; otherwise don't. Write public `docs/limitations.md`: redaction is enforced by workflow order, not by a sandbox; hook support differs by runtime; JSONL-first with best-effort converters; validated on synthetic data only.
**Done when:** `apm install --dry-run --target kiro` shows the hook file deployed.

#### T17 — Robustness tests (Haiku 5.5, Vibe, ~3 credits)
**Kiro instructions:** add `tests/test_stdlib_only.py` (every import under `.apm/**/*.py` is in `sys.stdlib_module_names` or a sibling skill script); failure-case fixtures/tests across scripts: empty folder, corrupted lines, no errors, empty time window, missing deploys file, Windows-style CRLF input. Each must fail with a clear message or degrade gracefully, never crash with a traceback, never produce an RCA without evidence.

#### T18 — Eval tooling (Haiku 5.5, Vibe, ~5 credits; escalate to Sonnet)
**Kiro instructions:**
- `examples/evaluation/prepare_eval.py --scenario <id>|all --dest <path>`: copies only `logs/`, `deploys.json`, `service_map.json` (**never answer.json**) into `<dest>/<scenario>/`.
- `examples/evaluation/record_run.py --scenario <id> --model <sonnet55|haiku55|gpt56luna> --run <N> --from <output_dir> --minutes <m> --credits <c>`: copies outputs to `runs/<scenario>/<model>-run<N>/` and writes meta.json; refuses to overwrite.
- `examples/evaluation/run_eval.py --scenarios all`: metrics per HANDOVER §9 plus: control-scenario pass rule (§4 row 9), host-scope accuracy for fleet-firmware-crash (affected_hosts == {gw-02, gw-03}), **cost per correct RCA** and **minutes per RCA** per model (from meta.json), manual baseline comparison (from manual_baseline.md table). Writes `evidence/scorecard.md` and `evidence/scorecard.json`, broken down by model and by difficulty.
- Tests with hand-made fake runs with known scores.

#### T19 — Manual baseline (owner, 0 credits, ~60 min)
Without the tool, time yourself finding the root cause in `db-pool-exhaustion` and `loud-red-herring` using only a text editor/grep. Record minutes and whether you were right in `examples/evaluation/manual_baseline.md` (table: scenario, minutes, correct yes/no, notes). Do this **before** looking at any agent output for those scenarios.

### Day 7 — Tue 24 Nov: evaluation

#### T20 — Evaluation runs (owner + Kiro, see §8, ~170 credits)
Follow §8 exactly.

#### T21 — Fix general weaknesses (Sonnet 5.5, Opus once if stuck, Vibe, ~80 credits)
**Kiro instructions:** given `evidence/scorecard.md` and the failing runs' evidence.json (owner points to them), propose **general** fixes to skills/references (never scenario-specific hints, never answer-key knowledge). Owner re-runs only affected scenarios as new run numbers; keep the old runs and note what changed and why in `evidence/changelog.md`.

#### T22 — Scorecard + screenshots (owner, 0 credits)
Regenerate scorecard. Screenshots into `evidence/screenshots/`: Kiro running `/run-incident-analysis`; report.html; rca.md with line IDs; redaction-report.json; evidence-check catching a bad claim (edit a copy of rca.md to add an unsupported claim and run check_evidence); pytest passing; scorecard.md; `.kiro/specs/` and `.kiro/steering/`. No private docs visible in any screenshot.

### 🚦 Gate 2 — end of Tue 24 Nov
- [ ] Scorecard generated from real runs, all Must scenarios covered on Sonnet and Haiku.
- [ ] Credits used ≤ 800.

### Day 8 — Wed 25 Nov: finish and publish

#### T23 — Final review, read-only (Opus 5.5, Vibe, ~30 credits)
**Kiro instructions:** don't edit files. Review the repo against HANDOVER §2 (rules, scoring). List in ≤ 40 lines: data-rule risks; README sections missing/inaccurate; claims not backed by evidence/scorecard.md; any tracked file referencing HANDOVER.md, BUILD_PLAN.md or apm-notes.md; any third-party import under `.apm/`; the 5 highest-value fixes ordered by impact. Owner applies only quick fixes (Haiku/Sonnet).

#### T24 — README final (Haiku 5.5, via the manual `update-readme-from-scorecard` hook + one Vibe chat, ~2 credits)
**Kiro instructions:** README.md must contain, in order: what it is (one line + report.html screenshot); problem and intended users; how it fits with CloudWatch/Datadog/Splunk/ELK (complement, not replacement: works on exported or field/device log bundles, local redaction, cited evidence, post-mortem); install (`apm install …`, then where it lands per runtime; Kiro: `apm install --target kiro`); quick start; inputs and outputs; parameters (HANDOVER §7 + input_format, mode, symptom); supported formats; **tested models only** (from scorecard); results table (from scorecard, real numbers); expected benefits; prerequisites (Python 3.10+, no packages); safety design; limitations (link docs/limitations.md); synthetic data note (link SYNTHETIC_DATA.md); Built with Kiro (specs, steering, hooks, model strategy); example usage. No references to private docs.

#### T25 — Demo video (owner, 0 credits, 3–5 min)
Problem (20s) → "a log bundle from a site with no observability tool" (20s) → run `/run-incident-analysis` live in Kiro (90s) → report.html + rca.md with evidence lines (45s) → redaction report + evidence-check catching a bad claim (30s) → scorecard: accuracy, Sonnet vs Haiku cost per RCA, minutes vs manual baseline, quiet-day control (30s) → embedded fleet scenario in 15s → limitations (15s). Record twice, keep the better take, link it in `evidence/`.

#### T26 — Publish v1.0.0 (owner, 0 credits)
- [ ] `pytest -q` green; gitleaks clean (if installed).
- [ ] `git ls-files` shows no HANDOVER.md, BUILD_PLAN.md, docs/apm-notes.md.
- [ ] Delete `.apm/skills/hello-incidentlens/`.
- [ ] `apm audit` clean on all primitives; `apm install --dry-run --target kiro` clean.
- [ ] No real data, keys, hostnames, company names. `FAKE-`/`example.test` only.
- [ ] `apm.yml`: `version: 1.0.0`, final description.
- [ ] `git add . && git commit -m "IncidentLens v1.0.0" && git tag v1.0.0 && git push origin main --tags`
- [ ] Update the portal entry: final description (remove "preview"), tags, business line; submit.
- [ ] Search the catalog; open the entry.
- [ ] **Fresh-install test:** new empty folder → install from the portal command (`--target kiro`) → `prepare_eval.py --scenario db-pool-exhaustion` into it → run `/run-incident-analysis` → outputs produced.

### Thu 26 Nov — buffer
Fix only what the fresh-install test broke. Bump to v1.0.1 if needed (new tag; never move v1.0.0).

---

## 7. Gates summary
| Gate | When | Pass condition | If missed |
|---|---|---|---|
| 0 | Fri 20 | Must scenarios frozen, redaction 100%, ≤ 160 credits | Drop row 10, then row 8 |
| 1 | Sun 22 | E2E run in Kiro with evidence-check passing, ≤ 450 credits | Cuts 1–3 |
| 2 | Tue 24 | Real scorecard for Must scenarios on 2 models, ≤ 800 credits | Cuts 4–6 |

---

## 8. Evaluation protocol (T20)

1. **Clean workspace = consumer install.** Create `C:\…\incidentlens-eval\` **outside the repo**. Install the package there with `apm install … --target kiro` (from the GitLab tag of the current build, or a local test release `v0.9.x`). Run `python <repo>/examples/evaluation/prepare_eval.py --scenario all --dest C:\…\incidentlens-eval`. The workspace has no answer keys, no steering, no specs: exactly what a real user would have.
2. Open that folder in Kiro. **New chat per run.** Use only `/run-incident-analysis` with the scenario's paths. Never mention scenario names' meaning, answers or hints.
3. Note start time; at the end note minutes and the credits delta shown by Kiro.
4. `python <repo>/examples/evaluation/record_run.py --scenario <id> --model <m> --run <N> --from <workspace>/incident-report --minutes <x> --credits <y>`, then delete the workspace's `incident-report/` before the next run.
5. Run matrix (in this order, stop and re-plan if the first two Sonnet runs cost > 15 credits each):
   - Sonnet 5.5: run 1 on every Must + Should scenario (9 runs); run 2 on db-pool-exhaustion, loud-red-herring, fleet-firmware-crash (3 runs).
   - Haiku 5.5: runs 1 and 2 on every scenario (18 runs, very cheap).
   - GPT 5.6 Luna (optional, if approved): run 1 on every scenario.
6. `python examples/evaluation/run_eval.py --scenarios all` → scorecard.
7. Report failures honestly. Never edit references or prompts using knowledge of answer keys.

---

## 9. Winning narrative (use in README, form and demo)
- **Problem:** hours of grep across services during incidents; logs contain secrets so they can't go to AI tools.
- **Not another observability platform:** works on any exported log bundle, including device/field logs (FleetSense) and customer sites with no monitoring stack; complements CloudWatch/Datadog/Splunk/ELK.
- **Trust by design:** local redaction first; every claim cites log line IDs; evidence-check and leak scan after; says "insufficient evidence" instead of guessing (quiet-day control).
- **Proof:** answer-key scorecard across 9 scenarios, 2 fictional systems, 2+ models; cost per correct RCA; minutes vs manual baseline.
- **Adoption:** one install, zero Python packages, runs in Kiro and other APM targets, data-driven scenarios and an editable failure-pattern library.
- **Built with Kiro:** 3 specs, 4 steering files, 2 hooks, "Sonnet plans, Haiku builds" model strategy with measured credit use.

---

## 10. Cut list (apply in order)
1. GPT 5.6 Luna runs.
2. `overlapping-changes` scenario (row 10).
3. Sonnet run 2 (keep only db-pool-exhaustion repeat).
4. T16 hook files → describe in limitations.md instead.
5. `doctor.py`.
6. `/quick-triage` prompt (triage mode stays in the workflow skill).
7. T23 Opus review → use the T26 checklist.
8. `convert_logs.py` reduced to `plain` + `ecs` formats.
9. `fleet-firmware-crash` scenario.
10. `render_report.py` (last resort; it's the demo centrepiece).

---

## 11. Trackers

### 11.1 Credits (1,000 total; estimates include multipliers)
| Day | Tasks | Planned | Cumulative | Actual |
|---|---|---|---|---|
| Wed 18 | T01–T03, T03b | 4 | 4 | 0.64 (T01–T03) |
| Thu 19 | T04, T05 | 55 | 59 | |
| Fri 20 | T06, T07 | 90 | 149 | |
| Sat 21 | T08–T10 | 59 | 208 | |
| Sun 22 | T11–T14 | 205 | 413 | |
| Mon 23 | T15–T18 | 18 | 431 | |
| Tue 24 | T20, T21 | 250 | 681 | |
| Wed 25 | T23, T24 | 32 | 713 | |
| Reserve | escalations | 200 | 913 | |
| Buffer | | 87 | 1,000 | |

### 11.2 Progress (owner ticks)
| Task | Status | Date | Credits | Notes |
|---|---|---|---|---|
| V1 verify Kiro target | ☐ | | 0 | |
| T03b align foundation | ☐ | | | |
| T04 generator spec | ◐ in progress | 18 Nov | | decisions in §1.1 |
| T05 engine + 2 scenarios | ☐ | | | |
| T06 scenarios 3–9 | ☐ | | | |
| T07 redact-logs | ☐ | | | |
| Gate 0 | ☐ | | | |
| T08 parser | ☐ | | | |
| T09 convert_logs | ☐ | | | |
| T10 log-parser SKILL | ☐ | | | |
| T11 rca-reasoning | ☐ | | | |
| T12 evidence-check | ☐ | | | |
| T13 postmortem-writer | ☐ | | | |
| T14 workflow/agent/prompts/doctor | ☐ | | | |
| Gate 1 | ☐ | | | |
| T15 render_report | ☐ | | | |
| T16 hooks + limitations | ☐ | | | |
| T17 robustness tests | ☐ | | | |
| T18 eval tooling | ☐ | | | |
| T19 manual baseline | ☐ | | | |
| T20 eval runs | ☐ | | | |
| T21 fixes | ☐ | | | |
| T22 scorecard + screenshots | ☐ | | | |
| Gate 2 | ☐ | | | |
| T23 Opus review | ☐ | | | |
| T24 README | ☐ | | | |
| T25 demo | ☐ | | | |
| T26 publish v1.0.0 | ☐ | | | |
