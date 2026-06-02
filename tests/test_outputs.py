from __future__ import annotations

import csv

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import (
    render_output_summary,
    risk_cluster_rows,
    risk_register_rows,
    triage_queue_rows,
    write_reports,
)


def test_output_summary_describes_review_workflow() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    summary = render_output_summary(run)
    assert "Triage Workflow Summary" in summary
    assert "Review Queue Tiers" in summary
    assert "not production deployment or model-provider performance" in summary
    assert "outputs/triage_queue.csv" in summary


def test_structured_output_rows_cover_queue_clusters_and_register() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    queue_rows = triage_queue_rows(run)
    cluster_rows = risk_cluster_rows(run)
    register_rows = risk_register_rows(run)

    assert len(queue_rows) == len(run.cases)
    assert len(cluster_rows) == len(run.clusters)
    assert register_rows
    assert queue_rows[0]["priority_rank"] == 1
    assert "reason_codes" in queue_rows[0]
    assert "rationale" in cluster_rows[0]
    assert "monitoring_signals" in register_rows[0]


def test_write_reports_generates_public_outputs(tmp_path) -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    write_reports(
        run,
        docs_dir=tmp_path / "docs",
        out_dir=tmp_path / "out",
        outputs_dir=tmp_path / "outputs",
    )

    summary = (tmp_path / "outputs" / "summary.md").read_text(encoding="utf-8")
    assert "Synthetic fixture only" in summary

    with (tmp_path / "outputs" / "triage_queue.csv").open(encoding="utf-8", newline="") as file:
        queue = list(csv.DictReader(file))
    assert len(queue) == len(run.cases)
    assert queue[0]["case_id"] == run.cases[0].case_id
    assert "full prompt:" not in summary.lower()
