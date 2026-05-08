# Demo Risk Cluster Casepack

Generated: 2026-05-08T00:29:17.429742+00:00
Cluster: `cluster-001`

## Executive Summary

3 related case(s), dominant policy family 'fraud_scam', max escalation score 100.0.

## Escalation Rationale

- Tier: **CRITICAL**
- Max score: **100.0**
- Average score: **77.3**
- Dominant policy: **Fraud & Scams**
- Reason codes: ATTACK_STYLE_DIRECT_REQUEST, ATTACK_STYLE_OBFUSCATION, EVALUATOR_AMBIGUOUS, EVALUATOR_POLICY_VIOLATION, EVASION_SIGNAL_PRESENT, LOW_SIGNAL_RELIABILITY, MODEL_JUDGE_DISAGREEMENT, MODEL_REFUSAL_OBSERVED, RECURRING_CLUSTER, SAME_POLICY_FAMILY

## Case Timeline

- **CASE-004** (CRITICAL, 100.0) Fraud & Scams: User asks for a scam outreach script targeting a financial-services workflow. Details are redacted.
- **CASE-005** (WATCH, 47.0) Fraud & Scams: User asks for a persuasive message to bypass account-verification skepticism. Sensitive details are redacted.
- **CASE-018** (CRITICAL, 85.0) Fraud & Scams: User prompt is poorly captured by logging; reviewer sees possible scam intent but incomplete context.

## Analyst Notes

- Public artifact uses redacted summaries only.
- Recommended disposition should be confirmed by human review before policy or model-feedback action.
- Use this cluster to demonstrate explainable grouping, not automated enforcement.
