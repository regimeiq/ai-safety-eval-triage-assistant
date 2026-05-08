# AI Safety Eval Triage Assistant

Standalone V2-style artifact translating a protective-intelligence operating model into AI trust & safety and model-evaluation triage.

This is not a feature update to the Protective Intelligence Assistant. V1 demonstrated domain tradecraft: noisy signal collection, reason-coded correlation, source-health telemetry, and analyst-ready case products. This project applies the same operating model to AI safety eval cases, abuse-pattern review, and red-team support workflows.

## What It Does

- Ingests sanitized synthetic eval cases from `fixtures/eval_cases.json`.
- Normalizes policy families and evaluator labels.
- Scores escalation priority with transparent reason codes.
- Clusters related cases into explainable risk families.
- Tracks eval health: coverage gaps, stale runs, missing labels, evaluator disagreement, and low-reliability signals.
- Produces an emerging AI risk register with early indicators, severity, prevalence, exposure, trajectory, confidence, and mitigation recommendations.
- Generates portfolio-ready Markdown reports and a Streamlit analyst queue.

## Quick Start

```bash
pip install -r requirements.txt -r requirements-dev.txt
make demo
make test
make dashboard
```

Generated artifacts:

- `docs/evaluation_report.md`
- `docs/eval_health_heartbeat.md`
- `docs/demo_casepack.md`
- `docs/emerging_ai_risk_register.md`
- `out/triage_run.json`

## Scope Guardrails

- Fixture-first and redacted-summary-only.
- No live user data, PII, external APIs, or benchmark downloads.
- No production safety, official benchmark, or automated enforcement claims.
- Human-in-the-loop decision support, not autonomous policy enforcement.

## Resume Bullet

Built an AI safety eval triage assistant that ingests adversarial eval cases, clusters related failures into explainable risk families, scores escalation priority with reason codes, and generates an emerging-risk register tracking indicators, severity, prevalence, exposure, confidence, and mitigation options.

## Interview Pitch

My first project demonstrated the protective-intelligence operating model: collect noisy signals, correlate them into reviewable threads, score risk transparently, and monitor source health. This second project translates that same model into AI trust & safety: eval cases and red-team findings become risk clusters, evaluator reliability replaces source credibility, and heartbeat telemetry becomes eval coverage and blind-spot monitoring.
