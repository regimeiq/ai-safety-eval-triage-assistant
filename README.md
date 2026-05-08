# AI Safety Eval Triage Assistant

Standalone tool for AI trust & safety and model-evaluation triage.

The assistant ingests sanitized eval cases, groups related findings into explainable risk clusters, scores escalation priority, monitors eval health, and produces analyst-ready reports for human review.

## Portfolio Scope

This is a focused portfolio artifact, not a SaaS MVP. The goal is to demonstrate practical AI safety eval-ops judgment: transparent triage logic, safe fixture handling, reproducible reports, and clear human-review workflows.

## What It Does

- Ingests sanitized synthetic eval cases from `fixtures/eval_cases.json`.
- Normalizes policy families and evaluator labels.
- Scores escalation priority with transparent reason codes.
- Clusters related cases into explainable risk families.
- Tracks eval health: coverage gaps, stale runs, missing labels, evaluator disagreement, and low-reliability signals.
- Produces an emerging AI risk register with early indicators, severity, prevalence, exposure, trajectory, confidence, and mitigation recommendations.
- Generates Markdown reports and a Streamlit analyst queue.

## Screenshots

| Overview | Triage Queue |
|---|---|
| ![Overview dashboard](docs/screenshots/overview.png) | ![Triage queue](docs/screenshots/triage_queue.png) |

| Emerging AI Risk Register |
|---|
| ![Emerging AI risk register](docs/screenshots/risk_register.png) |

## Analytical Approach

This project treats eval findings as triage signals rather than isolated benchmark rows.

- **Policy taxonomy:** normalizes cases into harm/risk families before scoring.
- **Weak-signal clustering:** groups related findings by policy family, attack style, evasion signals, and text similarity.
- **Signal reliability:** tracks missing labels, evaluator disagreement, stale cases, and low-reliability signals.
- **Eval health:** distinguishes low observed risk from low eval coverage.
- **Emerging risk register:** summarizes risk areas by severity, prevalence, exposure, trajectory, confidence, indicators, and mitigation options.
- **Fixture sanity checks:** verifies the synthetic workflow against hand-authored demonstration labels without presenting the numbers as production safety performance.

See [METHODOLOGY.md](METHODOLOGY.md) for implementation details and [DATA_CARD.md](DATA_CARD.md) for fixture scope and limitations.

## Quick Start

```bash
pip install -r requirements.txt -r requirements-dev.txt
make demo
make check
make dashboard
```

Generated artifacts:

- `docs/evaluation_report.md`
- `docs/eval_health_heartbeat.md`
- `docs/demo_casepack.md`
- `docs/emerging_ai_risk_register.md`
- `docs/error_analysis.md`
- `out/triage_run.json`

## Scope Guardrails

- Fixture-first and redacted-summary-only.
- No live user data, PII, external APIs, or benchmark downloads.
- No production safety, official benchmark, or automated enforcement claims.
- Human-in-the-loop decision support, not autonomous policy enforcement.
