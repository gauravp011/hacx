# IncidentLens

Turns raw application logs into an evidence-backed root cause analysis and a ready-to-review post-mortem — with secrets masked before any AI sees them.

![IncidentLens report](evidence/screenshots/sample-report.png)

**For:** on-call engineers, SREs, support and embedded/IoT teams who need to find out *why* an incident happened from a log bundle.

---

## Install

**Prerequisites:** Python 3.10+ (no packages needed) · APM CLI · an AI coding agent (Kiro, GitHub Copilot, Claude Code, Cursor, …)

```bash
apm install https://<gitlab-host>/<group>/incidentlens.git#v1.0.0 --target <your-tool>
```

| Your tool | `--target` |
|---|---|
| Kiro | `kiro` |
| GitHub Copilot (VS Code) | `copilot` |
| Claude Code | `claude` |
| Cursor | `cursor` |
| Any Agent Skills tool | `agent-skills` |

Private GitLab: set `GITLAB_APM_PAT` (scope `read_repository`) or make sure `git clone` of the URL works first.
Check the install: `python <skills-folder>/run-incident-analysis/scripts/doctor.py` → `Ready.`

---

## Use

1. Put your inputs in the workspace:
   - `logs/` — one or more log files (required)
   - `deploys.json` — recent changes (recommended)
   - `service_map.json` — which service calls which (optional)
2. In a new chat, run:
   ```
   /run-incident-analysis logs=logs deploys=deploys.json service_map=service_map.json symptom="checkout returns 503"
   ```
   Fast answer instead: `/quick-triage logs=logs symptom="..."`
3. Open `incident-report/report.html`.

**deploys.json**
```json
[{"event_id": "C1", "ts": "2026-11-25T08:40:00Z", "service": "billing-api", "change_type": "deploy", "details": "release 4.2.0"}]
```
`change_type`: `deploy` · `config` · `infra` · `feature_flag`

**service_map.json** (caller → callees)
```json
{"web-frontend": ["billing-api"], "billing-api": ["payments-db"]}
```

---

## Inputs

| Log format | Examples |
|---|---|
| JSON lines / JSON / CSV | app logs, tool exports |
| CloudWatch, Datadog, Elastic ECS | exports from those platforms |
| Plain text | log4j / Spring Boot, Python logging, syslog (devices, gateways), nginx / Apache access logs |
| Anything else | the agent writes a small mapping file and re-runs |

## Outputs (`incident-report/`)

| File | Content |
|---|---|
| `report.html` | One-page report: root cause, error chart, cited log lines, red herrings ruled out |
| `rca.md` | Root cause analysis with five whys |
| `postmortem.md` | Blameless post-mortem draft with action items |
| `timeline.md` | Mermaid incident timeline |
| `evidence.json` | Machine-readable hypotheses and evidence |
| `evidence-check.json` | Citation and leak-scan result |
| `redaction-report.json` | What was masked (counts only) |

## Parameters

| Parameter | Default | Notes |
|---|---|---|
| `logs` | — | Required; file or folder |
| `deploys` | none | Recommended |
| `service_map` | none | Optional |
| `symptom` | none | What users saw |
| `mode` | `full` | `full` or `triage` |
| `time_window` | auto | `START/END` ISO timestamps |
| `redaction` | `strict` | `strict` or `standard`; cannot be turned off |
| `output_dir` | `./incident-report` | |

---

## How it works

1. **Convert** any format to one clean format with an ID per line.
2. **Redact** emails, IPs, tokens, passwords, keys and card numbers — before the AI sees anything.
3. **Parse** thousands of lines into a short summary: what failed first, what is loudest, which changes came just before, which hosts are affected.
4. **Reason** from the symptom along the service map to the **earliest** anomaly (not the loudest), cite exact log lines, rule out red herrings — or say "insufficient evidence".
5. **Write** the RCA, post-mortem and timeline.
6. **Check** every citation, flag unsupported claims, re-scan all outputs for leaked secrets, build the HTML report.

Read-only: no remediation, no config changes, no network calls.

## Package contents

| Type | Name |
|---|---|
| Skills | `run-incident-analysis`, `redact-logs`, `log-parser`, `rca-reasoning`, `postmortem-writer`, `evidence-check` |
| Agent | `incident-analyst` |
| Prompts | `/investigate-incident`, `/quick-triage` |
| Hook | `evidence-gate` (re-checks the report when the session ends) |

## Supported models

Evaluated in Kiro with **Claude Sonnet 5.5**. Results: [`evidence/scorecard.md`](evidence/scorecard.md).

## Results

Synthetic incidents with hidden answer keys (fictional systems only):

| Metric | Result |
|---|---|
| Root cause correct (Sonnet 5.5) | 3 / 3 |
| Evidence check passed | 3 / 3 |
| Planted secrets removed | 100% |
| Time to root cause, hard case | ~<MIN> min with IncidentLens vs 58 min manual |

## Benefits

- Minutes instead of hours to an evidence-backed root cause
- Same RCA quality whoever is on call
- Logs usable with AI safely: redaction first, leak scan last
- Works on any exported log bundle, including customer sites and devices with no monitoring stack

## Limitations

Pattern-based redaction (names and addresses aren't detected) · validated on synthetic data · one incident window per run · the post-mortem is a draft for human review. Details: [`docs/limitations.md`](docs/limitations.md).

## Data

All examples are synthetic (fictional ShopSphere and FleetSense systems, fake secrets). See [`SYNTHETIC_DATA.md`](SYNTHETIC_DATA.md).
