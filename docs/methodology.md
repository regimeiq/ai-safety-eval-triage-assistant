# Methodology

## Purpose

This project turns redacted AI safety eval-style records into review artifacts: a ranked triage queue, explainable risk clusters, eval-health checks, and a structured risk register.

The workflow is designed for human review. It does not automate enforcement, claim model access, or represent production safety performance.

## Input Records

Each case includes:

- redacted prompt and response summaries
- policy family
- expected and observed evaluator labels
- severity
- attack style
- evasion signals
- signal reliability
- optional hand-authored fixture labels for sanity checks

The public fixture uses summaries rather than full prompts or responses. Validation rejects common markers for unredacted prompt text.

## Scoring

Escalation scoring is deterministic and reason-coded. The score combines:

- severity tier
- policy-family weight
- evaluator label
- missing-label or evaluator-disagreement signal
- attack style
- evasion signals
- low-reliability signal
- recurrence in a cluster

Scores are not calibrated probabilities. They are queue-prioritization scores.

Review tiers:

| Tier | Score Range | Review Posture |
|---|---:|---|
| CRITICAL | 75-100 | Immediate analyst review |
| ELEVATED | 55-74.9 | Near-term review |
| WATCH | 35-54.9 | Watchlist or calibration review |
| LOW | 0-34.9 | Control or low-priority review |

## Clustering

Cases are grouped with a lightweight, explainable linkage process:

- TF-IDF text similarity over redacted summaries and metadata
- shared policy family
- shared attack style
- shared evasion signals
- shared fixture source as supporting context

Cluster outputs include member case IDs, dominant policy family, shared signals, max and average score, reason codes, and a short rationale.

## Eval Health

The health snapshot tracks whether the eval set itself is trustworthy enough to interpret:

- policy coverage
- dataset and model coverage
- attack-style coverage
- missing labels
- evaluator disagreement
- low-reliability signals
- stale cases
- blind-spot policy families

Time-based checks use the run's `analysis_as_of` timestamp, derived from the newest fixture case, so generated outputs remain reproducible as the calendar advances.

## Outputs

`make demo` generates:

- `outputs/summary.md`: run summary, review tiers, top clusters, and scope notes
- `outputs/triage_queue.csv`: ranked case review queue
- `outputs/risk_clusters.csv`: explainable cluster table
- `outputs/risk_register.csv`: structured risk register
- `docs/evaluation_report.md`: workflow metrics and highest-priority cases
- `docs/eval_health_heartbeat.md`: eval health summary
- `docs/demo_casepack.md`: representative cluster casepack
- `docs/emerging_ai_risk_register.md`: Markdown risk register
- `docs/error_analysis.md`: fixture false positives, false negatives, and cluster errors
- `out/triage_run.json`: complete serialized run object

## Metrics

The fixture reports escalation precision, recall, F1, and pairwise cluster precision, recall, and F1. These compare deterministic workflow outputs against hand-authored synthetic fixture labels.

These are sanity checks for the workflow. They are not official benchmark scores or model-performance claims.
