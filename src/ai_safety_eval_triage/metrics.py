from __future__ import annotations

from itertools import combinations

from ai_safety_eval_triage.models import TriageCase, TriageMetrics


def _f1(precision: float, recall: float) -> float:
    return round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0


def _safe_div(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def compute_metrics(cases: list[TriageCase], escalation_threshold: float = 55.0) -> TriageMetrics:
    predicted_escalations = {
        case.case_id for case in cases if case.escalation_score >= escalation_threshold
    }
    expected_escalations = {case.case_id for case in cases if case.human_escalate}
    tp = len(predicted_escalations & expected_escalations)
    fp = len(predicted_escalations - expected_escalations)
    fn = len(expected_escalations - predicted_escalations)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)

    predicted_pairs = {
        _pair_key(left.case_id, right.case_id)
        for left, right in combinations(cases, 2)
        if left.cluster_id == right.cluster_id
    }
    expected_pairs = {
        _pair_key(left.case_id, right.case_id)
        for left, right in combinations(cases, 2)
        if left.gold_cluster_id == right.gold_cluster_id
    }
    cluster_tp = len(predicted_pairs & expected_pairs)
    cluster_fp = len(predicted_pairs - expected_pairs)
    cluster_fn = len(expected_pairs - predicted_pairs)
    cluster_precision = _safe_div(cluster_tp, cluster_tp + cluster_fp)
    cluster_recall = _safe_div(cluster_tp, cluster_tp + cluster_fn)

    return TriageMetrics(
        escalation_precision=precision,
        escalation_recall=recall,
        escalation_f1=_f1(precision, recall),
        false_positives=fp,
        false_negatives=fn,
        cluster_pairwise_precision=cluster_precision,
        cluster_pairwise_recall=cluster_recall,
        cluster_pairwise_f1=_f1(cluster_precision, cluster_recall),
        cluster_true_positives=cluster_tp,
        cluster_false_positives=cluster_fp,
        cluster_false_negatives=cluster_fn,
    )
