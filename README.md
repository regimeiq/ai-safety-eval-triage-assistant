# AI Safety Eval Triage Assistant

Standalone tool for AI trust & safety and model-evaluation triage.

The assistant ingests sanitized eval cases, groups related findings into explainable risk clusters, scores escalation priority, monitors eval health, and produces analyst-ready reports for human review.

## What It Does

- Ingests sanitized synthetic eval cases from `fixtures/eval_cases.json`.
- Normalizes policy families and evaluator labels.
- Scores escalation priority with transparent reason codes.
- Clusters related cases into explainable risk families.
- Tracks eval health: coverage gaps, stale runs, missing labels, evaluator disagreement, and low-reliability signals.
- Produces an emerging AI risk register with early indicators, severity, prevalence, exposure, trajectory, confidence, and mitigation recommendations.
- Generates Markdown reports and a Streamlit analyst queue.

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
