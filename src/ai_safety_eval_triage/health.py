from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from ai_safety_eval_triage.models import EvalHealthSnapshot, TriageCase
from ai_safety_eval_triage.taxonomy import POLICY_FAMILIES


def _rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def build_health_snapshot(cases: list[TriageCase], now: datetime | None = None) -> EvalHealthSnapshot:
    now = now or datetime.now(timezone.utc)
    total = len(cases)
    missing_label_count = sum(
        1 for case in cases if "unlabeled" in {case.expected_label, case.evaluator_label}
    )
    disagreement_count = sum(
        1
        for case in cases
        if case.expected_label != "unlabeled"
        and case.evaluator_label != "unlabeled"
        and case.expected_label != case.evaluator_label
    )
    low_reliability_count = sum(1 for case in cases if case.signal_reliability < 0.55)
    stale_count = sum(1 for case in cases if (now - case.created_at).days > 30)
    coverage_by_policy = dict(sorted(Counter(case.normalized_policy_family for case in cases).items()))

    return EvalHealthSnapshot(
        total_cases=total,
        coverage_by_policy=coverage_by_policy,
        coverage_by_dataset=dict(sorted(Counter(case.dataset_source for case in cases).items())),
        coverage_by_model=dict(sorted(Counter(case.model_name for case in cases).items())),
        coverage_by_attack_style=dict(sorted(Counter(case.attack_style for case in cases).items())),
        missing_label_count=missing_label_count,
        missing_label_rate=_rate(missing_label_count, total),
        evaluator_disagreement_count=disagreement_count,
        evaluator_disagreement_rate=_rate(disagreement_count, total),
        low_reliability_count=low_reliability_count,
        stale_case_count=stale_count,
        blind_spot_policies=sorted(set(POLICY_FAMILIES) - set(coverage_by_policy)),
    )

