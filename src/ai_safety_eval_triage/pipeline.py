from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from ai_safety_eval_triage.clustering import assign_clusters, build_clusters
from ai_safety_eval_triage.health import build_health_snapshot
from ai_safety_eval_triage.metrics import compute_metrics
from ai_safety_eval_triage.models import EvalCase, TriageRun
from ai_safety_eval_triage.scoring import apply_recurrence_adjustment, score_case


def run_triage(cases: list[EvalCase], taxonomy_version: str = "unknown") -> TriageRun:
    scored_cases = [score_case(case) for case in cases]
    clustered_cases, pair_reasons = assign_clusters(scored_cases)
    cluster_sizes = Counter(case.cluster_id for case in clustered_cases)
    adjusted_cases = [
        apply_recurrence_adjustment(case, cluster_sizes[case.cluster_id])
        for case in clustered_cases
    ]
    analysis_as_of = max(
        (case.created_at for case in adjusted_cases), default=datetime.now(timezone.utc)
    )
    clusters = build_clusters(adjusted_cases, pair_reasons)
    health = build_health_snapshot(adjusted_cases, now=analysis_as_of)
    metrics = compute_metrics(adjusted_cases)
    return TriageRun(
        taxonomy_version=taxonomy_version,
        analysis_as_of=analysis_as_of,
        cases=sorted(adjusted_cases, key=lambda case: (-case.escalation_score, case.case_id)),
        clusters=clusters,
        health=health,
        metrics=metrics,
        generated_at=datetime.now(timezone.utc),
    )
