from __future__ import annotations

from pathlib import Path

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import render_evaluation_report

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    taxonomy_version, cases = load_eval_cases(ROOT / "fixtures" / "eval_cases.json")
    report = render_evaluation_report(run_triage(cases, taxonomy_version))
    path = ROOT / "docs" / "evaluation_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
