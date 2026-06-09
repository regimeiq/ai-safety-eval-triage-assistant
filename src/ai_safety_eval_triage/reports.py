from __future__ import annotations

import csv
import json
from itertools import combinations
from pathlib import Path

from ai_safety_eval_triage.models import RiskCluster, TriageCase, TriageRun
from ai_safety_eval_triage.risk_register import build_risk_register
from ai_safety_eval_triage.scoring import ESCALATION_THRESHOLD
from ai_safety_eval_triage.taxonomy import policy_display_name


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _table_rows(mapping: dict[str, int]) -> str:
    return "\n".join(f"| {_md_cell(key)} | {value} |" for key, value in mapping.items())


def _md_cell(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _list_cell(values: list[str]) -> str:
    return "; ".join(values)


def _review_lane(case: TriageCase) -> str:
    if case.escalation_tier == "CRITICAL":
        return "Immediate analyst review"
    if case.escalation_tier == "ELEVATED":
        return "Near-term review"
    if case.escalation_tier == "WATCH":
        return "Watchlist / calibration review"
    return "Control / low-priority review"


def render_evaluation_report(run: TriageRun) -> str:
    metrics = run.metrics
    risk_register_entries = build_risk_register(run)
    escalation_ready = sum(case.escalation_tier in {"CRITICAL", "ELEVATED"} for case in run.cases)
    health_flags = (
        run.health.missing_label_count
        + run.health.evaluator_disagreement_count
        + run.health.low_reliability_count
        + run.health.stale_case_count
        + len(run.health.blind_spot_policies)
    )
    lines = [
        "# AI Safety Eval Triage: Evaluation Report",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
        f"Taxonomy version: `{run.taxonomy_version}`",
        "",
        "## Workflow Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Cases | {len(run.cases)} |",
        f"| Cases to review | {escalation_ready} |",
        f"| Risk clusters | {len(run.clusters)} |",
        f"| Risk register entries | {len(risk_register_entries)} |",
        f"| Eval health flags | {health_flags} |",
        "",
        "## Synthetic Fixture Checks",
        "",
        "These checks verify the fixture workflow against hand-authored demonstration labels; they are not production safety-performance claims.",
        "",
        "| Metric | Value |",
        "|---|---:|",
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
                    _md_cell(case.case_id),
                    _md_cell(case.escalation_tier),
                    f"{case.escalation_score:.1f}",
                    _md_cell(policy_display_name(case.normalized_policy_family)),
                    _md_cell(case.evaluator_label),
                    _md_cell(", ".join(case.reason_codes[:5])),
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


def render_output_summary(run: TriageRun) -> str:
    risk_register_entries = build_risk_register(run)
    critical_cases = sum(case.escalation_tier == "CRITICAL" for case in run.cases)
    elevated_cases = sum(case.escalation_tier == "ELEVATED" for case in run.cases)
    watch_cases = sum(case.escalation_tier == "WATCH" for case in run.cases)
    low_cases = sum(case.escalation_tier == "LOW" for case in run.cases)
    health_flags = (
        run.health.missing_label_count
        + run.health.evaluator_disagreement_count
        + run.health.low_reliability_count
        + run.health.stale_case_count
        + len(run.health.blind_spot_policies)
    )
    top_clusters = sorted(run.clusters, key=lambda cluster: (-cluster.max_score, -cluster.size))[:5]

    lines = [
        "# Triage Workflow Summary",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
        f"Taxonomy version: `{run.taxonomy_version}`",
        "",
        "This public artifact is generated from synthetic, redacted eval-style cases. It demonstrates a review workflow, not production deployment or model-provider performance.",
        "",
        "## Evaluation Surface",
        "",
        "- Input records are summarized eval cases with policy family, evaluator label, severity, attack style, evasion signals, and signal reliability.",
        "- Cases are scored for review priority using deterministic reason codes rather than opaque model judgments.",
        "- Related cases are clustered into risk families for analyst review, recurrence tracking, and risk-register drafting.",
        "- Metrics are fixture sanity checks against hand-authored demonstration labels.",
        "",
        "## Run Totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Cases | {len(run.cases)} |",
        f"| Risk clusters | {len(run.clusters)} |",
        f"| Risk register entries | {len(risk_register_entries)} |",
        f"| Eval health flags | {health_flags} |",
        "",
        "## Review Queue Tiers",
        "",
        "| Tier | Cases | Review posture |",
        "|---|---:|---|",
        f"| CRITICAL | {critical_cases} | Immediate analyst review |",
        f"| ELEVATED | {elevated_cases} | Near-term review |",
        f"| WATCH | {watch_cases} | Watchlist / calibration review |",
        f"| LOW | {low_cases} | Control / low-priority review |",
        "",
        "## Top Risk Clusters",
        "",
        "| Cluster | Tier | Max Score | Size | Dominant Policy | Rationale |",
        "|---|---|---:|---:|---|---|",
    ]
    for cluster in top_clusters:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(cluster.cluster_id),
                    _md_cell(cluster.escalation_tier),
                    f"{cluster.max_score:.1f}",
                    str(cluster.size),
                    _md_cell(policy_display_name(cluster.dominant_policy_family)),
                    _md_cell(cluster.rationale),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Eval Health Flags",
            "",
            f"- Missing labels: **{run.health.missing_label_count}**",
            f"- Evaluator disagreements: **{run.health.evaluator_disagreement_count}**",
            f"- Low-reliability cases: **{run.health.low_reliability_count}**",
            f"- Stale cases: **{run.health.stale_case_count}**",
            f"- Blind-spot policy families: **{len(run.health.blind_spot_policies)}**",
            "",
            "## Output Files",
            "",
            "- `outputs/triage_queue.csv`: ranked case queue with score, tier, review lane, cluster, and reason codes.",
            "- `outputs/risk_clusters.csv`: explainable cluster table with shared signals and rationale.",
            "- `outputs/risk_register.csv`: risk areas with severity, exposure, trajectory, confidence, monitoring signals, and mitigation options.",
            "",
            "## Scope",
            "",
            "- Synthetic fixture only.",
            "- Redacted summaries only.",
            "- Human review required before policy, safety, or product action.",
        ]
    )
    return "\n".join(lines) + "\n"


def triage_queue_rows(run: TriageRun) -> list[dict[str, object]]:
    return [
        {
            "priority_rank": index,
            "case_id": case.case_id,
            "escalation_tier": case.escalation_tier,
            "escalation_score": f"{case.escalation_score:.1f}",
            "review_lane": _review_lane(case),
            "policy_family": policy_display_name(case.normalized_policy_family),
            "evaluator_label": case.evaluator_label,
            "expected_label": case.expected_label,
            "severity": case.severity,
            "attack_style": case.attack_style,
            "signal_reliability": f"{case.signal_reliability:.2f}",
            "cluster_id": case.cluster_id or "",
            "reason_codes": _list_cell(case.reason_codes),
            "evasion_signals": _list_cell(case.evasion_signals),
            "created_at": case.created_at.isoformat(),
            "dataset_source": case.dataset_source,
            "prompt_summary": case.prompt_summary,
            "response_summary": case.response_summary,
        }
        for index, case in enumerate(run.cases, start=1)
    ]


def risk_cluster_rows(run: TriageRun) -> list[dict[str, object]]:
    return [
        {
            "cluster_id": cluster.cluster_id,
            "escalation_tier": cluster.escalation_tier,
            "max_score": f"{cluster.max_score:.1f}",
            "avg_score": f"{cluster.avg_score:.1f}",
            "size": cluster.size,
            "dominant_policy_family": policy_display_name(cluster.dominant_policy_family),
            "case_ids": _list_cell(cluster.case_ids),
            "shared_attack_styles": _list_cell(cluster.shared_attack_styles),
            "shared_evasion_signals": _list_cell(cluster.shared_evasion_signals),
            "reason_codes": _list_cell(cluster.reason_codes),
            "rationale": cluster.rationale,
        }
        for cluster in run.clusters
    ]


def risk_register_rows(run: TriageRun) -> list[dict[str, object]]:
    return [
        {
            "risk_area": entry.risk_area,
            "abuse_pathway": entry.abuse_pathway,
            "severity": entry.severity,
            "prevalence": entry.prevalence,
            "exposure": entry.exposure,
            "trajectory": entry.trajectory,
            "confidence": entry.confidence,
            "risk_score": f"{entry.risk_score:.1f}",
            "early_indicators": _list_cell(entry.early_indicators),
            "monitoring_signals": _list_cell(entry.monitoring_signals),
            "recommended_mitigation": entry.recommended_mitigation,
            "source_case_ids": _list_cell(entry.source_case_ids),
        }
        for entry in build_risk_register(run)
    ]


def render_health_heartbeat(run: TriageRun) -> str:
    health = run.health
    lines = [
        "# Eval Health Heartbeat",
        "",
        f"Generated: {run.generated_at.isoformat()}",
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
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
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
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
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
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
                    _md_cell(entry.risk_area),
                    _md_cell(entry.abuse_pathway),
                    _md_cell(entry.severity),
                    _md_cell(entry.prevalence),
                    _md_cell(entry.exposure),
                    _md_cell(entry.trajectory),
                    _md_cell(entry.confidence),
                    f"{entry.risk_score:.1f}",
                    _md_cell("; ".join(entry.monitoring_signals)),
                    _md_cell(entry.recommended_mitigation),
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


def render_error_analysis(
    run: TriageRun, escalation_threshold: float = ESCALATION_THRESHOLD
) -> str:
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
        f"Analysis as of: {run.analysis_as_of.isoformat()}",
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


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_reports(
    run: TriageRun,
    docs_dir: str | Path = "docs",
    out_dir: str | Path = "out",
    outputs_dir: str | Path = "outputs",
) -> None:
    docs = Path(docs_dir)
    docs.mkdir(parents=True, exist_ok=True)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    outputs = Path(outputs_dir)
    outputs.mkdir(parents=True, exist_ok=True)
    (docs / "evaluation_report.md").write_text(render_evaluation_report(run), encoding="utf-8")
    (docs / "eval_health_heartbeat.md").write_text(render_health_heartbeat(run), encoding="utf-8")
    (docs / "demo_casepack.md").write_text(render_casepack(run), encoding="utf-8")
    (docs / "emerging_ai_risk_register.md").write_text(render_risk_register(run), encoding="utf-8")
    (docs / "error_analysis.md").write_text(render_error_analysis(run), encoding="utf-8")
    (outputs / "summary.md").write_text(render_output_summary(run), encoding="utf-8")
    _write_csv(outputs / "triage_queue.csv", triage_queue_rows(run))
    _write_csv(outputs / "risk_clusters.csv", risk_cluster_rows(run))
    _write_csv(outputs / "risk_register.csv", risk_register_rows(run))
    write_run_json(run, Path(out_dir) / "triage_run.json")
