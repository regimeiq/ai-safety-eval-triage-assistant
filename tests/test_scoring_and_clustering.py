from __future__ import annotations

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.models import is_label_disagreement
from ai_safety_eval_triage.pipeline import run_triage


def test_scoring_ranks_clear_violations_above_benign_controls() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    by_id = {case.case_id: case for case in run.cases}
    assert by_id["CASE-001"].escalation_score > by_id["CASE-016"].escalation_score
    assert "EVALUATOR_POLICY_VIOLATION" in by_id["CASE-001"].reason_codes
    assert "BENIGN_CONTROL" in by_id["CASE-016"].reason_codes


def test_clustering_recovers_gold_pairs_with_usable_precision() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    assert run.metrics.cluster_pairwise_precision >= 0.65
    assert run.metrics.cluster_pairwise_recall >= 0.45
    assert run.metrics.cluster_pairwise_f1 >= 0.5


def test_escalation_metrics_are_nonzero() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    assert run.metrics.escalation_precision >= 0.7
    assert run.metrics.escalation_recall >= 0.7


def test_disagreement_predicate_excludes_unlabeled() -> None:
    assert is_label_disagreement("violation", "ambiguous")
    assert is_label_disagreement("safe", "violation")
    assert not is_label_disagreement("violation", "violation")
    assert not is_label_disagreement("unlabeled", "ambiguous")
    assert not is_label_disagreement("violation", "unlabeled")
    assert not is_label_disagreement("unlabeled", "unlabeled")


def test_unlabeled_case_is_not_model_judge_disagreement() -> None:
    version, cases = load_eval_cases("fixtures/eval_cases.json")
    run = run_triage(cases, version)
    by_id = {case.case_id: case for case in run.cases}
    assert "MISSING_LABEL" in by_id["CASE-018"].reason_codes
    assert "MODEL_JUDGE_DISAGREEMENT" not in by_id["CASE-018"].reason_codes
