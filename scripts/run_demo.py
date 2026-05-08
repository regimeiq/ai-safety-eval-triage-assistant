from __future__ import annotations

from pathlib import Path

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import write_reports


def main() -> None:
    taxonomy_version, cases = load_eval_cases(Path("fixtures/eval_cases.json"))
    run = run_triage(cases, taxonomy_version=taxonomy_version)
    write_reports(run)
    print("Generated demo artifacts:")
    print("  docs/evaluation_report.md")
    print("  docs/eval_health_heartbeat.md")
    print("  docs/demo_casepack.md")
    print("  docs/emerging_ai_risk_register.md")
    print("  out/triage_run.json")


if __name__ == "__main__":
    main()
