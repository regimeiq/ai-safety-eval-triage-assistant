# Triage Workflow Summary

Generated: 2026-06-02T02:10:59.335688+00:00
Analysis as of: 2026-05-05T12:30:00+00:00
Taxonomy version: `2026-05-v1`

This public artifact is generated from synthetic, redacted eval-style cases. It demonstrates a review workflow, not production deployment or model-provider performance.

## Evaluation Surface

- Input records are summarized eval cases with policy family, evaluator label, severity, attack style, evasion signals, and signal reliability.
- Cases are scored for review priority using deterministic reason codes rather than opaque model judgments.
- Related cases are clustered into risk families for analyst review, recurrence tracking, and risk-register drafting.
- Metrics are fixture sanity checks against hand-authored demonstration labels.

## Run Totals

| Metric | Value |
|---|---:|
| Cases | 18 |
| Risk clusters | 12 |
| Risk register entries | 7 |
| Eval health flags | 8 |

## Review Queue Tiers

| Tier | Cases | Review posture |
|---|---:|---|
| CRITICAL | 9 | Immediate analyst review |
| ELEVATED | 1 | Near-term review |
| WATCH | 2 | Watchlist / calibration review |
| LOW | 6 | Control / low-priority review |

## Top Risk Clusters

| Cluster | Tier | Max Score | Size | Dominant Policy | Rationale |
|---|---|---:|---:|---|---|
| cluster-001 | CRITICAL | 100.0 | 3 | Fraud & Scams | 3 related case(s), dominant policy family 'fraud_scam', max escalation score 100.0. |
| cluster-002 | CRITICAL | 100.0 | 2 | Cyber Safety | 2 related case(s), dominant policy family 'cyber_safety', max escalation score 100.0. |
| cluster-003 | CRITICAL | 100.0 | 2 | Self-Harm | 2 related case(s), dominant policy family 'self_harm', max escalation score 100.0. |
| cluster-011 | CRITICAL | 100.0 | 1 | Violence & Threats | 1 related case(s), dominant policy family 'violence_threats', max escalation score 100.0. |
| cluster-004 | CRITICAL | 97.0 | 2 | Policy Boundary / Dual Use | 2 related case(s), dominant policy family 'policy_boundary', max escalation score 97.0. |

## Eval Health Flags

- Missing labels: **1**
- Evaluator disagreements: **3**
- Low-reliability cases: **1**
- Stale cases: **2**
- Blind-spot policy families: **1**

## Output Files

- `outputs/triage_queue.csv`: ranked case queue with score, tier, review lane, cluster, and reason codes.
- `outputs/risk_clusters.csv`: explainable cluster table with shared signals and rationale.
- `outputs/risk_register.csv`: risk areas with severity, exposure, trajectory, confidence, monitoring signals, and mitigation options.

## Scope

- Synthetic fixture only.
- Redacted summaries only.
- Human review required before policy, safety, or product action.
