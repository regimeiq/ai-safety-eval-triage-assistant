# AI Safety Eval Triage Assistant

Local triage workflow for redacted AI safety eval-style cases.

The tool ingests sanitized cases, scores review priority with transparent reason codes, clusters related failures into risk families, tracks eval-health issues, and exports review artifacts for human analysis.

Portfolio page: https://wksprojects.com/ai-safety-eval-triage-assistant/

## What It Evaluates

- Redacted adversarial or policy-boundary eval cases
- Policy family, severity, evaluator label, attack style, evasion signals, and signal reliability
- Recurring risk patterns across cases, models, datasets, and attack styles
- Eval-health signals such as missing labels, stale cases, evaluator disagreement, low reliability, and policy coverage gaps

The default data in `fixtures/eval_cases.json` is synthetic and summarized. It does not include live user data, proprietary evals, full prompts, or provider-specific model access.

## How Cases Are Scored

Each case receives a deterministic escalation score from 0 to 100. The score combines severity, policy family, evaluator outcome, attack style, evasion signals, missing-label status, signal reliability, and cluster recurrence.

Scores are queue-prioritization signals, not calibrated probabilities.

| Tier | Score Range | Review Posture |
|---|---:|---|
| CRITICAL | 75-100 | Immediate analyst review |
| ELEVATED | 55-74.9 | Near-term review |
| WATCH | 35-54.9 | Watchlist or calibration review |
| LOW | 0-34.9 | Control or low-priority review |

## Outputs

Run the demo:

```bash
pip install -r requirements.txt -r requirements-dev.txt
make demo
make check
```

Generated review artifacts:

- `outputs/summary.md`: run summary, review tiers, top clusters, and scope notes
- `outputs/triage_queue.csv`: ranked review queue with score, tier, reason codes, cluster, and summaries
- `outputs/risk_clusters.csv`: cluster table with shared signals, member cases, and rationale
- `outputs/risk_register.csv`: risk areas with severity, exposure, trajectory, confidence, monitoring signals, and mitigation options
- `docs/evaluation_report.md`: workflow metrics and highest-priority cases
- `docs/eval_health_heartbeat.md`: eval health summary
- `docs/demo_casepack.md`: representative risk-cluster casepack
- `docs/emerging_ai_risk_register.md`: Markdown risk register
- `docs/error_analysis.md`: fixture false positives, false negatives, and cluster errors
- `out/triage_run.json`: complete serialized run object

## Review Prioritization

The queue is sorted by escalation score and then reviewed by tier:

1. Critical and elevated cases go to analyst review first.
2. Related cases are grouped into explainable clusters so recurring patterns are reviewed together.
3. Eval-health flags prevent over-interpreting weak coverage, stale cases, missing labels, or low-reliability records.
4. The risk register summarizes non-low clusters into severity, prevalence, exposure, trajectory, confidence, indicators, and recommended mitigations.

## Screenshots

| Overview | Triage Queue |
|---|---|
| ![Overview dashboard](docs/screenshots/overview.png) | ![Triage queue](docs/screenshots/triage_queue.png) |

| Emerging AI Risk Register |
|---|
| ![Emerging AI risk register](docs/screenshots/risk_register.png) |

## Methodology And Scope

- [docs/methodology.md](docs/methodology.md)
- [docs/limitations.md](docs/limitations.md)
- [docs/public_incident_companion.md](docs/public_incident_companion.md)
- [DATA_CARD.md](DATA_CARD.md)

Scope guardrails:

- Public-safe synthetic fixture by default
- Redacted summaries only
- No live user data, PII, external APIs, benchmark downloads, or operational deployment claims
- Human-in-the-loop decision support, not automated enforcement
