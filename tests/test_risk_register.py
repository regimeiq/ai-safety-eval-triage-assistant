from __future__ import annotations

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import render_risk_register
from ai_safety_eval_triage.risk_register import build_risk_register


def test_risk_register_contains_emerging_risk_fields() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    entries = build_risk_register(run)
    assert entries
    assert entries[0].risk_area
    assert entries[0].early_indicators
    assert entries[0].monitoring_signals
    assert entries[0].recommended_mitigation


def test_risk_register_report_is_public_safe() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    report = render_risk_register(run).lower()
    assert "emerging ai risk register" in report
    assert "severity" in report
    assert "prevalence" in report
    assert "exposure" in report
    assert "trajectory" in report
    assert "full prompt:" not in report
