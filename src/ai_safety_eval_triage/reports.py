from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from ai_safety_eval_triage.models import RiskCluster, TriageCase, TriageRun
from ai_safety_eval_triage.risk_register import build_risk_register
from ai_safety_eval_triage.taxonomy import policy_display_name


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _table_rows(mapping: dict[str, int]) -> str:
    return "\n".join(f"| {key} | {value} |" for key, value in mapping.items())


def render_evaluation_report(run: TriageRun) -> str:
    metrics = run.metrics
    lines = [
        "# AI Safety Eval Triage: Evaluation Report",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        f"Taxonomy version: `{run.taxonomy_version}`",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Cases | {len(run.cases)} |",
        f"| Risk clusters | {len(run.clusters)} |",
        f"| Escalation precision | {metrics.escalation_precision:.3f} |",
        f"| Escalation recall | {metrics.escalation_recall:.3f} |",
        f"| Escalation F1 | {metrics.escalation_f1:.3f} |",
        f"| Cluster pairwise precision | {metrics.cluster_pairwise_precision:.3f} |",
        f"| Cluster pairwise recall | {metrics.cluster_pairwise_recall:.3f} |",
        f"| Cluster pairwise F1 | {metrics.cluster_pairwise_f1:.3f} |",
        "",
        "## Highest Priority Cases",
        "",
        "| Case | Tier | Score | Policy | Evaluator | Reasons |",
        "|---|---|---:|---|---|---|",
    ]
    for case in run.cases[:10]:
        lines.append(
            "| "
            + " | ".join(
                [
                    case.case_id,
                    case.escalation_tier,
                    f"{case.escalation_score:.1f}",
                    policy_display_name(case.normalized_policy_family),
                    case.evaluator_label,
                    ", ".join(case.reason_codes[:5]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Synthetic fixture benchmark; metrics do not estimate production safety performance.",
            "- Redacted summaries are suitable for public demonstration, not full policy adjudication.",
            "- Clustering is deterministic decision support and should be reviewed by a human analyst.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_health_heartbeat(run: TriageRun) -> str:
    health = run.health
    lines = [
        "# Eval Health Heartbeat",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        "",
        "## Fleet Summary",
        "",
        f"- Cases: **{health.total_cases}**",
        f"- Missing-label rate: **{_pct(health.missing_label_rate)}**",
        f"- Evaluator disagreement rate: **{_pct(health.evaluator_disagreement_rate)}**",
        f"- Low-reliability cases: **{health.low_reliability_count}**",
        f"- Stale cases: **{health.stale_case_count}**",
        f"- Blind-spot policy families: **{len(health.blind_spot_policies)}**",
        "",
        "## Coverage By Policy",
        "",
        "| Policy | Cases |",
        "|---|---:|",
        _table_rows(health.coverage_by_policy),
        "",
        "## Coverage By Model",
        "",
        "| Model | Cases |",
        "|---|---:|",
        _table_rows(health.coverage_by_model),
        "",
        "## Blind Spots",
        "",
    ]
    if health.blind_spot_policies:
        lines.extend(f"- {policy_display_name(policy)}" for policy in health.blind_spot_policies)
    else:
        lines.append("- None detected in the configured taxonomy.")
    return "\n".join(lines) + "\n"


def _case_line(case: TriageCase) -> str:
    return (
        f"- **{case.case_id}** ({case.escalation_tier}, {case.escalation_score:.1f}) "
        f"{policy_display_name(case.normalized_policy_family)}: {case.prompt_summary}"
    )


def render_casepack(run: TriageRun, cluster_id: str | None = None) -> str:
    cluster = _select_cluster(run, cluster_id)
    member_ids = set(cluster.case_ids)
    members = [case for case in run.cases if case.case_id in member_ids]
    lines = [
        "# Demo Risk Cluster Casepack",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        f"Cluster: `{cluster.cluster_id}`",
        "",
        "## Executive Summary",
        "",
        cluster.rationale,
        "",
        "## Escalation Rationale",
        "",
        f"- Tier: **{cluster.escalation_tier}**",
        f"- Max score: **{cluster.max_score:.1f}**",
        f"- Average score: **{cluster.avg_score:.1f}**",
        f"- Dominant policy: **{policy_display_name(cluster.dominant_policy_family)}**",
        f"- Reason codes: {', '.join(cluster.reason_codes[:10])}",
        "",
        "## Case Timeline",
        "",
    ]
    lines.extend(_case_line(case) for case in sorted(members, key=lambda item: item.created_at))
    lines.extend(
        [
            "",
            "## Analyst Notes",
            "",
            "- Public artifact uses redacted summaries only.",
            "- Recommended disposition should be confirmed by human review before policy or model-feedback action.",
            "- Use this cluster to demonstrate explainable grouping, not automated enforcement.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_risk_register(run: TriageRun) -> str:
    entries = build_risk_register(run)
    lines = [
        "# Emerging AI Risk Register",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        "",
        "This register is a scoped demonstration artifact derived from synthetic eval fixtures. It is intended to demonstrate emerging-risk triage, not estimate production prevalence.",
        "",
        "| Risk Area | Abuse Pathway | Severity | Prevalence | Exposure | Trajectory | Confidence | Score | Monitoring Signals | Recommended Mitigation |",
        "|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for entry in entries:
        lines.append(
            "| "
            + " | ".join(
                [
                    entry.risk_area,
                    entry.abuse_pathway,
                    entry.severity,
                    entry.prevalence,
                    entry.exposure,
                    entry.trajectory,
                    entry.confidence,
                    f"{entry.risk_score:.1f}",
                    "; ".join(entry.monitoring_signals),
                    entry.recommended_mitigation,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Early Indicators By Risk Area",
            "",
        ]
    )
    for entry in entries:
        lines.append(f"### {entry.risk_area}")
        lines.append("")
        lines.append(f"- Source cases: {', '.join(entry.source_case_ids)}")
        lines.append(f"- Early indicators: {', '.join(entry.early_indicators)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_error_analysis(run: TriageRun, escalation_threshold: float = 55.0) -> str:
    predicted_escalations = {
        case.case_id for case in run.cases if case.escalation_score >= escalation_threshold
    }
    expected_escalations = {case.case_id for case in run.cases if case.human_escalate}
    false_positives = sorted(predicted_escalations - expected_escalations)
    false_negatives = sorted(expected_escalations - predicted_escalations)
    over_merged, under_merged = _cluster_errors(run)

    lines = [
        "# Error Analysis",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        "",
        "This report is generated from the synthetic fixture benchmark. It is intended to make failure modes reviewable, not to estimate production performance.",
        "",
        "## Escalation Errors",
        "",
        f"- False positives: **{len(false_positives)}**",
        f"- False negatives: **{len(false_negatives)}**",
        "",
        "### False Positives",
        "",
    ]
    lines.extend(_case_bullets(run, false_positives) or ["- None in this fixture run."])
    lines.extend(["", "### False Negatives", ""])
    lines.extend(_case_bullets(run, false_negatives) or ["- None in this fixture run."])
    lines.extend(
        [
            "",
            "## Clustering Errors",
            "",
            f"- Over-merged pairs: **{len(over_merged)}**",
            f"- Under-merged pairs: **{len(under_merged)}**",
            "",
            "### Over-Merged Pairs",
            "",
        ]
    )
    lines.extend(_pair_bullets(over_merged) or ["- None in this fixture run."])
    lines.extend(["", "### Under-Merged Pairs", ""])
    lines.extend(_pair_bullets(under_merged) or ["- None in this fixture run."])
    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- False positives are useful for tuning analyst workload and over-escalation pressure.",
            "- False negatives are higher priority because they represent missed escalation opportunities.",
            "- Over-merged clusters can hide distinct policy issues; under-merged clusters can fragment recurring risk patterns.",
        ]
    )
    return "\n".join(lines) + "\n"


def _select_cluster(run: TriageRun, cluster_id: str | None = None) -> RiskCluster:
    if cluster_id:
        for cluster in run.clusters:
            if cluster.cluster_id == cluster_id:
                return cluster
        raise ValueError(f"Cluster not found: {cluster_id}")
    return sorted(run.clusters, key=lambda cluster: (-cluster.max_score, -cluster.size))[0]


def _case_bullets(run: TriageRun, case_ids: list[str]) -> list[str]:
    cases = {case.case_id: case for case in run.cases}
    return [
        f"- **{case_id}** ({cases[case_id].escalation_tier}, {cases[case_id].escalation_score:.1f}): "
        f"{cases[case_id].prompt_summary}"
        for case_id in case_ids
        if case_id in cases
    ]


def _pair_key(left: TriageCase, right: TriageCase) -> tuple[str, str]:
    return tuple(sorted((left.case_id, right.case_id)))


def _cluster_errors(run: TriageRun) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    predicted_pairs = {
        _pair_key(left, right)
        for left, right in combinations(run.cases, 2)
        if left.cluster_id == right.cluster_id
    }
    expected_pairs = {
        _pair_key(left, right)
        for left, right in combinations(run.cases, 2)
        if left.gold_cluster_id == right.gold_cluster_id
    }
    return sorted(predicted_pairs - expected_pairs), sorted(expected_pairs - predicted_pairs)


def _pair_bullets(pairs: list[tuple[str, str]]) -> list[str]:
    return [f"- `{left}` / `{right}`" for left, right in pairs]


def write_run_json(run: TriageRun, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(run.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_reports(run: TriageRun, docs_dir: str | Path = "docs", out_dir: str | Path = "out") -> None:
    docs = Path(docs_dir)
    docs.mkdir(parents=True, exist_ok=True)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    (docs / "evaluation_report.md").write_text(render_evaluation_report(run), encoding="utf-8")
    (docs / "eval_health_heartbeat.md").write_text(render_health_heartbeat(run), encoding="utf-8")
    (docs / "demo_casepack.md").write_text(render_casepack(run), encoding="utf-8")
    (docs / "emerging_ai_risk_register.md").write_text(render_risk_register(run), encoding="utf-8")
    (docs / "error_analysis.md").write_text(render_error_analysis(run), encoding="utf-8")
    write_run_json(run, Path(out_dir) / "triage_run.json")
