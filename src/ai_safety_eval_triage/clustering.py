from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai_safety_eval_triage.models import RiskCluster, TriageCase
from ai_safety_eval_triage.scoring import escalation_tier


def _case_text(case: TriageCase) -> str:
    signals = " ".join(case.evasion_signals)
    return " ".join(
        [
            case.prompt_summary,
            case.response_summary,
            case.normalized_policy_family,
            case.attack_style,
            signals,
        ]
    )


def _link_reasons(left: TriageCase, right: TriageCase, similarity: float) -> list[str]:
    reasons: list[str] = []
    same_policy = left.normalized_policy_family == right.normalized_policy_family
    shared_signals = set(left.evasion_signals) & set(right.evasion_signals)

    if same_policy:
        reasons.append("SAME_POLICY_FAMILY")
    if left.attack_style == right.attack_style and left.attack_style != "benign_control":
        reasons.append("SHARED_ATTACK_STYLE")
    if shared_signals:
        reasons.append("SHARED_EVASION_SIGNAL")
    if similarity >= 0.22:
        reasons.append("SEMANTIC_SIMILARITY")
    if left.dataset_source == right.dataset_source and same_policy:
        reasons.append("SHARED_DATASET_SOURCE")

    non_benign_policy = same_policy and left.normalized_policy_family != "benign_near_miss"
    shared_signal_link = non_benign_policy and bool(shared_signals)
    shared_attack_link = (
        non_benign_policy
        and left.attack_style == right.attack_style
        and left.attack_style != "benign_control"
        and similarity >= 0.16
    )
    strong_policy_link = (
        same_policy
        and similarity >= 0.12
        and (bool(shared_signals) or left.attack_style == right.attack_style)
    )
    semantic_policy_link = same_policy and similarity >= 0.25
    recurring_control_link = (
        same_policy
        and left.attack_style == right.attack_style == "benign_control"
        and similarity >= 0.2
    )
    if (
        semantic_policy_link
        or strong_policy_link
        or recurring_control_link
        or shared_signal_link
        or shared_attack_link
    ):
        return sorted(set(reasons))
    return []


def assign_clusters(
    cases: list[TriageCase],
) -> tuple[list[TriageCase], dict[tuple[str, str], list[str]]]:
    if not cases:
        return [], {}

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform([_case_text(case) for case in cases])
    similarities = cosine_similarity(matrix)

    adjacency: dict[str, set[str]] = {case.case_id: set() for case in cases}
    pair_reasons: dict[tuple[str, str], list[str]] = {}
    case_by_id = {case.case_id: case for case in cases}

    for i, j in combinations(range(len(cases)), 2):
        left, right = cases[i], cases[j]
        reasons = _link_reasons(left, right, float(similarities[i, j]))
        if reasons:
            adjacency[left.case_id].add(right.case_id)
            adjacency[right.case_id].add(left.case_id)
            pair_reasons[tuple(sorted((left.case_id, right.case_id)))] = reasons

    seen: set[str] = set()
    components: list[list[str]] = []
    for case in cases:
        if case.case_id in seen:
            continue
        stack = [case.case_id]
        component: list[str] = []
        seen.add(case.case_id)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))

    components.sort(key=lambda ids: (-len(ids), ids[0]))
    cluster_id_by_case: dict[str, str] = {}
    for idx, component in enumerate(components, start=1):
        cluster_id = f"cluster-{idx:03d}"
        for case_id in component:
            cluster_id_by_case[case_id] = cluster_id

    assigned = [
        case_by_id[case.case_id].model_copy(update={"cluster_id": cluster_id_by_case[case.case_id]})
        for case in cases
    ]
    return assigned, pair_reasons


def build_clusters(
    cases: list[TriageCase], pair_reasons: dict[tuple[str, str], list[str]]
) -> list[RiskCluster]:
    grouped: dict[str, list[TriageCase]] = defaultdict(list)
    for case in cases:
        grouped[str(case.cluster_id)].append(case)

    clusters: list[RiskCluster] = []
    for cluster_id, members in sorted(grouped.items()):
        policies = Counter(member.normalized_policy_family for member in members)
        dominant_policy = policies.most_common(1)[0][0]
        shared_styles = sorted({member.attack_style for member in members})
        signal_counts = Counter(signal for member in members for signal in member.evasion_signals)
        shared_signals = sorted(signal for signal, count in signal_counts.items() if count >= 2)
        scores = np.array([member.escalation_score for member in members], dtype=float)
        max_score = round(float(scores.max()), 1)
        avg_score = round(float(scores.mean()), 1)

        reasons = set()
        member_ids = {member.case_id for member in members}
        for pair, pair_reason_codes in pair_reasons.items():
            if set(pair).issubset(member_ids):
                reasons.update(pair_reason_codes)
        for member in members:
            reasons.update(member.reason_codes)

        rationale = (
            f"{len(members)} related case(s), dominant policy family '{dominant_policy}', "
            f"max escalation score {max_score}."
        )
        clusters.append(
            RiskCluster(
                cluster_id=cluster_id,
                case_ids=sorted(member.case_id for member in members),
                size=len(members),
                dominant_policy_family=dominant_policy,
                shared_attack_styles=shared_styles,
                shared_evasion_signals=shared_signals,
                max_score=max_score,
                avg_score=avg_score,
                escalation_tier=escalation_tier(max_score),
                reason_codes=sorted(reasons),
                rationale=rationale,
            )
        )
    return sorted(
        clusters, key=lambda cluster: (-cluster.max_score, -cluster.size, cluster.cluster_id)
    )
