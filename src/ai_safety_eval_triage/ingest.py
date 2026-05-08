from __future__ import annotations

import json
from pathlib import Path

from ai_safety_eval_triage.models import EvalCase


def load_eval_cases(path: str | Path) -> tuple[str, list[EvalCase]]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    taxonomy_version = str(payload.get("taxonomy_version") or "unknown")
    raw_cases = payload.get("cases", payload if isinstance(payload, list) else [])
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError(f"No eval cases found in {fixture_path}")
    return taxonomy_version, [EvalCase.model_validate(item) for item in raw_cases]
