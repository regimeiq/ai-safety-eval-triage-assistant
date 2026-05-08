from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from ai_safety_eval_triage.models import EvalCase


REQUIRED_FIELDS = {
    "case_id",
    "dataset_source",
    "model_name",
    "created_at",
    "prompt_summary",
    "response_summary",
    "policy_family",
    "expected_label",
    "evaluator_label",
    "severity",
    "attack_style",
    "signal_reliability",
    "human_escalate",
    "gold_cluster_id",
}


def _parse_signals(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [item.strip() for item in text.replace(";", ",").split(",") if item.strip()]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [text]


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def _normalize_row(row: dict) -> dict:
    normalized = dict(row)
    missing = sorted(field for field in REQUIRED_FIELDS if field not in normalized)
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")
    normalized["evasion_signals"] = _parse_signals(normalized.get("evasion_signals", []))
    normalized["signal_reliability"] = float(normalized["signal_reliability"])
    normalized["human_escalate"] = _parse_bool(normalized["human_escalate"])
    normalized["notes"] = str(normalized.get("notes") or "")
    return EvalCase.model_validate(normalized).model_dump(mode="json")


def _load_json(path: Path) -> tuple[str, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    taxonomy_version = str(payload.get("taxonomy_version") or "imported-v1")
    rows = payload.get("cases", payload if isinstance(payload, list) else [])
    if not isinstance(rows, list):
        raise ValueError("JSON input must be a list of cases or an object with a 'cases' list.")
    return taxonomy_version, [_normalize_row(row) for row in rows]


def _load_csv(path: Path) -> tuple[str, list[dict]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return "imported-v1", [_normalize_row(row) for row in rows]


def import_cases(input_path: Path, output_path: Path, input_format: str) -> None:
    if input_format == "json":
        taxonomy_version, cases = _load_json(input_path)
    elif input_format == "csv":
        taxonomy_version, cases = _load_csv(input_path)
    else:
        raise ValueError("format must be 'json' or 'csv'")
    output = {
        "description": "Normalized local eval-case import. Review before public use.",
        "taxonomy_version": taxonomy_version,
        "cases": cases,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize local eval-case CSV/JSON into fixture schema.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    args = parser.parse_args()
    import_cases(args.input, args.output, args.format)
    print(args.output)


if __name__ == "__main__":
    main()
