# BUILD_PLAN v4 — IncidentLens (finish by Tue 24 Nov 2026)

> **v4 (19 Nov 2026):** the full package was built and tested in the Claude (Cowork) session and delivered as `incidentlens-v0.9.0.zip`. Kiro is now used to **install, run, evaluate, review and fix** the package, plus the specs/steering already created. Supersedes v3. PRIVATE: git-ignored, never pushed.
> Owner types in Kiro: `Do R<nn> from #BUILD_PLAN.md` for Kiro tasks; owner-only tasks are marked (owner).
> **Kiro does not rebuild the code.** The code is finished and tested. Kiro's jobs: verify it on this machine (R02–R04), run the package as the end user would (R06–R07), improve it from evaluation results (R09–R10), update docs (R11) and review (R13). One new Kiro chat per task.
> **Evaluation runs (R06–R07) are not "Do R.." prompts:** they are real user sessions, opened in the separate eval folder, using only `/run-incident-analysis ...`.

---

## 0. Rules for Kiro
1. Do only the requested R-task, then stop and report in ≤10 lines.
2. Never open `examples/scenarios/*/logs/*.jsonl`; never read `answer.json` except in R07/R08 evaluation scripts.
3. Shipped code under `.apm/` stays Python 3.10+ stdlib only (tests enforce it).
4. Never commit or quote HANDOVER.md, BUILD_PLAN.md, docs/apm-notes.md.
5. Fix general problems only; never tune skills or `failure-patterns.md` to specific scenarios or answer keys.

## 1. What is already built (in the zip)
| Area | Contents | Status |
|---|---|---|
| Skills (6) | run-incident-analysis, redact-logs, log-parser, rca-reasoning, postmortem-writer, evidence-check | done |
| Scripts (stdlib) | prepare_incident, finalize_incident, doctor, convert_logs (10 formats + mapping), redact, parse/cluster/timeline/get_lines, render_report, check_evidence | done |
| Agent / prompts / hook | incident-analyst, /investigate-incident, /quick-triage, evidence-gate | done (hook: VERIFY) |
| Data | data-driven generator, 10 scenarios across 2 systems, lock file | done |
| Evaluation | prepare_eval (blind case folders, no answer keys), record_run, run_eval (scorecard) | done |
| Tests | 75 pytest tests, all green | done |
| Docs | README, SYNTHETIC_DATA, docs/limitations, steering (4) | done; results pending |
| Sample | `examples/sample-run/loud-red-herring/` produced by Claude Opus 5.5 following the skills | done |

## 2. Steps

### Thu 19 – Fri 20: land it and prove it runs in Kiro
- **R01 (owner) Replace the repo contents** (the earlier T01–T03 skeleton is superseded; the T04 spec is kept as Kiro evidence). In PowerShell at the repo root:
  ```
  git checkout -b backup-t01-t04; git add -A; git commit -m "backup before v0.9.0"; git checkout main
  ```
  Then in File Explorer: delete everything in the repo **except** `.git`, `.kiro\specs`, `.kiro\hooks`. Extract the zip somewhere else, open its `incidentlens` folder, select all (show hidden items so `.apm`, `.kiro`, `.gitignore` are included) and copy into the repo root. Finally put `HANDOVER.md` and `BUILD_PLAN.md` at the root and `apm-notes.md` in `docs\`.
- **R02 (Kiro, Haiku 5.5, Autopilot) Verify locally.** Kiro prompt: `Do R02 from #BUILD_PLAN.md`
  Kiro instructions: run these in the terminal and report the last line of each; do not edit any file.
  ```
  pip install -r requirements-dev.txt
  python examples/generator/generate_incident.py --scenario all --check
  python -m pytest -q
  git status --short
  ```
  Expected: "All generated files match", 75 passed, and `git status` does not list HANDOVER.md, BUILD_PLAN.md, docs/apm-notes.md or examples/scenarios/.
- **R03 (Kiro, Haiku 5.5; Sonnet 5.5 if it fails twice) Fix Windows-only failures** — only if R02 had failures. Kiro prompt: `Do R03 from #BUILD_PLAN.md. Failing output: <paste>`
  Kiro instructions: fix only what the failing output shows, smallest change possible, keep the stdlib-only rule under `.apm/`, then rerun `python -m pytest -q`.
- **R04 (Kiro, Haiku 5.5) APM checks.** Kiro prompt: `Do R04 from #BUILD_PLAN.md`
  Kiro instructions: at the repo root run `apm install --dry-run --target kiro`, then `apm audit --file <path>` for every `.apm/skills/*/SKILL.md`, `.apm/agents/incident-analyst.agent.md` and both `.apm/prompts/*.prompt.md`. Report where each primitive would be placed and any error. Do not change files. Owner decides: if the hook is rejected, delete `.apm/hooks/` and add a line to docs/limitations.md; if the agent is rejected, change its `tools` line to the syntax the error asks for. Add the results to the Status section of docs/apm-notes.md.
- **R05 (owner) Commit, tag pre-release, push.** `git add .; git commit -m "IncidentLens v0.9.0"; git tag v0.9.0; git push origin main --tags`. (Pre-release: don't update the portal yet.)
- **R06 (owner) Clean-workspace smoke test = real user experience.**
  ```
  python examples/evaluation/prepare_eval.py --scenario all --dest C:\work\incidentlens-eval
  ```
  Open `C:\work\incidentlens-eval` in Kiro, install the package there from GitLab (`apm install <gitlab path>#v0.9.0 --target kiro`; fallback: import the 6 skills via Agent Steering & Skills). New chat on **Sonnet 5.5**:
  ```
  /run-incident-analysis logs=case-01/logs deploys=case-01/deploys.json service_map=case-01/service_map.json symptom="<case-01/symptom.txt>" output_dir=case-01/incident-report
  ```
  Expected: report.html opens, evidence check passed. Note minutes and credits.

### Sat 21: manual baseline + evaluation runs
- **R07a (owner, ~60 min) Manual baseline** on db-pool-exhaustion and loud-red-herring (case-01, case-07) with a text editor only, **before** looking at agent output. Fill `examples/evaluation/manual_baseline.md`.
- **R07 (owner) Eval runs.** New chat per run, only `/run-incident-analysis` with the case paths and the symptom text. After each run:
  ```
  python examples/evaluation/record_run.py --case case-01 --model sonnet55 --run 1 --from C:\work\incidentlens-eval\case-01\incident-report --minutes 5 --credits 12
  ```
  then delete that case's `incident-report/` before the next run.
  Matrix: Sonnet 5.5 run 1 on case-01…case-09 (9 runs) + run 2 on case-01, 07, 08; Haiku 5.5 runs 1–2 on case-01…case-09; GPT 5.6 Luna run 1 (optional, if approved); case-10 optional. **If the first two Sonnet runs cost >15 credits each, drop Sonnet run 2.**
- **R08 (owner) Scorecard.** `python examples/evaluation/run_eval.py` → `evidence/scorecard.md`.

### Sun 22: improve with Kiro (Built-with-Kiro evidence)
- **R09 (Kiro, Sonnet 5.5; Opus 5.5 once if stuck) Fix general weaknesses.** Prompt: "Do R09 from #BUILD_PLAN.md. Read #evidence/scorecard.md and the evidence.json of failing runs I point to. Propose general fixes to skills, scripts or references (never scenario-specific). Apply after I approve." Re-run only affected cases as new run numbers; log changes in `evidence/changelog.md`.
- **R10 (Kiro, Haiku 5.5) Spec + tests for any script change** made in R09 (keep pytest green).

### Mon 23: evidence and docs
- **R11 (Kiro, Haiku 5.5) README results.** Kiro prompt: `Do R11 from #BUILD_PLAN.md` (or trigger the `update-readme-from-scorecard` hook).
  Kiro instructions: read #evidence/scorecard.md and #examples/evaluation/manual_baseline.md. In README.md replace only the text between `<!-- RESULTS:MODELS -->` and `<!-- /RESULTS:MODELS -->` with a list of the models that appear in the scorecard, and between `<!-- RESULTS:TABLE -->` and `<!-- /RESULTS:TABLE -->` with a short table (per model: runs, top-1, service, evidence-check pass, redaction recall, avg minutes, credits per correct RCA) plus one line comparing average minutes with the manual baseline. Use only numbers from those two files. Change nothing else.
- **R12 (owner) Screenshots** into `evidence/screenshots/`: Kiro running the command; report.html; rca.md with line IDs; redaction-report.json; evidence-check catching a bad claim (add "The root cause was a cosmic ray." to a copy of rca.md, run check_evidence with `--strict-claims`); pytest green; scorecard; `.kiro/specs` + `.kiro/steering`.
- **R13 (Kiro, Opus 5.5) Final read-only review.** "Review the repo against #HANDOVER.md §2. Don't edit. ≤40 lines: data-rule risks, README gaps or unbacked claims, private-doc references in tracked files, top 5 fixes." Apply quick fixes only.

### Tue 24: demo and publish
- **R14 (owner) Demo video (3–5 min):** problem → hand a log bundle to Kiro → run → report.html walk-through (earliest vs loudest, cited lines, red herrings) → safety (redaction + leak scan + evidence check) → scorecard (accuracy, Sonnet vs Haiku cost per correct RCA, minutes vs manual baseline, quiet-day control) → embedded fleet case (15 s) → limitations.
- **R15 (owner) Publish v1.0.0.**
  - [ ] `pytest -q` green; `generate_incident.py --check` green.
  - [ ] `git ls-files` shows no HANDOVER.md, BUILD_PLAN.md, docs/apm-notes.md; no hello skill.
  - [ ] `apm audit` clean; `apm install --dry-run --target kiro` clean.
  - [ ] apm.yml `version: 1.0.0`; commit; `git tag v1.0.0`; `git push origin main --tags` (PowerShell: separate commands with `;`, not `&&`).
  - [ ] Portal entry: final description (no "preview"), tags, business line; submit; search the catalog.
  - [ ] Fresh install in a new folder → run quick-triage on one case.
- **Wed 25 – Thu 26: buffer** (fix only what fresh install broke; v1.0.1 if needed).

## 3. Credits (remaining ~950)
| Item | Estimate |
|---|---|
| R06 smoke run | 15 |
| Sonnet eval (12 runs) | ~150 |
| Haiku eval (18 runs) | ~10 |
| Luna eval (optional, 9 runs) | ~50 |
| R09/R10 fixes | ~100 |
| R13 Opus review | ~30 |
| Reserve | ~595 |

## 4. "Solution Built with Kiro" — honest wording to adapt
> Kiro was the build and evaluation workbench: specs and steering files encode the data rules, package structure, data contracts and coding standards; Kiro agent hooks validate skill frontmatter and sync results into the README. The package was installed and run inside Kiro on Claude Sonnet 5.5 and Haiku 5.5 (and GPT 5.6 Luna) to produce the scorecard, and Kiro was used to diagnose and fix weaknesses found in evaluation and for the final review. [Add: which parts of the code were generated outside Kiro, if the rulebook asks.]

## 5. Cut list (in order)
1. Luna runs · 2. Sonnet run 2 · 3. case-10 · 4. evidence-gate hook (document instead) · 5. R13 Opus review · 6. Haiku run 2.
