from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    from ai_safety_eval_triage.ingest import load_eval_cases
    from ai_safety_eval_triage.pipeline import run_triage
    from ai_safety_eval_triage.reports import write_reports

    taxonomy_version, cases = load_eval_cases(ROOT / "fixtures" / "eval_cases.json")
    run = run_triage(cases, taxonomy_version=taxonomy_version)
    write_reports(run, docs_dir=ROOT / "docs", out_dir=ROOT / "out", outputs_dir=ROOT / "outputs")
    print("Generated demo artifacts:")
    print("  docs/evaluation_report.md")
    print("  docs/eval_health_heartbeat.md")
    print("  docs/demo_casepack.md")
    print("  docs/emerging_ai_risk_register.md")
    print("  docs/error_analysis.md")
    print("  outputs/summary.md")
    print("  outputs/triage_queue.csv")
    print("  outputs/risk_clusters.csv")
    print("  outputs/risk_register.csv")
    print("  out/triage_run.json")


if __name__ == "__main__":
    main()
