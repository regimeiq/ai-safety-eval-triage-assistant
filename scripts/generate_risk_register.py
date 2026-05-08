from __future__ import annotations

from pathlib import Path

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.reports import render_risk_register


def main() -> None:
    taxonomy_version, cases = load_eval_cases("fixtures/eval_cases.json")
    report = render_risk_register(run_triage(cases, taxonomy_version))
    path = Path("docs/emerging_ai_risk_register.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
