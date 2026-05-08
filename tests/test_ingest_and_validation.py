from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.models import EvalCase


def test_fixture_loads() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    assert version == "2026-05-v1"
    assert len(cases) >= 12
    assert all(case.prompt_summary for case in cases)


def test_unredacted_marker_is_rejected() -> None:
    payload = {
        "case_id": "BAD-001",
        "dataset_source": "synthetic",
        "model_name": "model",
        "created_at": "2026-05-01T00:00:00Z",
        "prompt_summary": "Full prompt: this should not be allowed in public fixtures.",
        "response_summary": "Summarized response text.",
        "policy_family": "cyber_safety",
        "expected_label": "violation",
        "evaluator_label": "violation",
        "severity": "high",
        "attack_style": "direct_request",
        "evasion_signals": [],
        "signal_reliability": 0.9,
        "human_escalate": True,
        "gold_cluster_id": "BAD",
    }
    with pytest.raises(ValidationError):
        EvalCase.model_validate(payload)


def test_extra_prompt_field_is_rejected() -> None:
    _, cases = load_eval_cases("fixtures/eval_cases.json")
    payload = cases[0].model_dump(mode="json")
    payload["full_prompt"] = "not allowed"
    with pytest.raises(ValidationError):
        EvalCase.model_validate(payload)
