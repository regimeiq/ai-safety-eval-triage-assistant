from __future__ import annotations

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import (
    render_casepack,
    render_evaluation_report,
    render_health_heartbeat,
)


def test_health_snapshot_detects_quality_issues() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    assert run.health.missing_label_count == 1
    assert run.health.low_reliability_count == 1
    assert run.health.evaluator_disagreement_count >= 2
    assert "sexual_content" in run.health.blind_spot_policies


def test_reports_do_not_expose_disallowed_prompt_fields() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    combined = "\n".join(
        [
            render_evaluation_report(run),
            render_health_heartbeat(run),
            render_casepack(run),
        ]
    ).lower()
    assert "full prompt:" not in combined
    assert "verbatim prompt:" not in combined
    assert "exact prompt:" not in combined
    assert "unredacted" not in combined

