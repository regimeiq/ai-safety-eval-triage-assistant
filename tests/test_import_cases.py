from __future__ import annotations

import json
from pathlib import Path

from scripts.import_cases import import_cases


def test_import_cases_normalizes_json_fixture(tmp_path: Path) -> None:
    output = tmp_path / "imported.json"
    import_cases(Path("fixtures/eval_cases.json"), output, "json")
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["cases"]
    assert payload["cases"][0]["case_id"]
    assert isinstance(payload["cases"][0]["evasion_signals"], list)


def test_import_cases_normalizes_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "cases.csv"
    csv_path.write_text(
        "\n".join(
            [
                "case_id,dataset_source,model_name,created_at,prompt_summary,response_summary,policy_family,expected_label,evaluator_label,severity,attack_style,evasion_signals,signal_reliability,human_escalate,gold_cluster_id,notes",
                "CSV-001,local_eval,model-x,2026-05-01T00:00:00Z,User asks for redacted risky content.,Model response summary is redacted.,fraud_scam,violation,violation,high,direct_request,social_engineering,0.8,true,CSV-FRAUD,CSV import test",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "imported.json"
    import_cases(csv_path, output, "csv")
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["cases"][0]["case_id"] == "CSV-001"
    assert payload["cases"][0]["human_escalate"] is True
