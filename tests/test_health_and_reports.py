from __future__ import annotations

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import (
    render_casepack,
    render_error_analysis,
    render_evaluation_report,
    render_health_heartbeat,
)


def test_health_snapshot_detects_quality_issues() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    assert run.analysis_as_of.isoformat().startswith("2026-05-05")
    assert run.health.missing_label_count == 1
    assert run.health.low_reliability_count == 1
    assert run.health.stale_case_count == 2
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
            render_error_analysis(run),
        ]
    ).lower()
    assert "full prompt:" not in combined
    assert "verbatim prompt:" not in combined
    assert "exact prompt:" not in combined
    assert "unredacted" not in combined


def test_error_analysis_renders_failure_sections() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    report = render_error_analysis(run)
    assert "False Positives" in report
    assert "False Negatives" in report
    assert "Over-Merged Pairs" in report
    assert "Under-Merged Pairs" in report


def test_evaluation_report_labels_fixture_metrics_as_sanity_checks() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    report = render_evaluation_report(run)
    assert "Workflow Summary" in report
    assert "Synthetic Fixture Checks" in report
    assert "not production safety-performance claims" in report
