from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _reason_label(reason_code: str) -> str:
    return reason_code.replace("_", " ").title()


def _reason_summary(reason_codes: list[str], limit: int = 4) -> str:
    return ", ".join(_reason_label(code) for code in reason_codes[:limit])


def main() -> None:
    from ai_safety_eval_triage.ingest import load_eval_cases
    from ai_safety_eval_triage.models import TriageRun
    from ai_safety_eval_triage.pipeline import run_triage
    from ai_safety_eval_triage.reports import render_casepack
    from ai_safety_eval_triage.risk_register import build_risk_register
    from ai_safety_eval_triage.taxonomy import policy_display_name

    st.set_page_config(page_title="AI Safety Eval Triage", layout="wide")

    @st.cache_data(show_spinner=False)
    def load_run() -> dict:
        out_path = ROOT / "out" / "triage_run.json"
        if out_path.exists():
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            if "analysis_as_of" in payload:
                return payload
        taxonomy_version, cases = load_eval_cases(ROOT / "fixtures" / "eval_cases.json")
        return run_triage(cases, taxonomy_version).model_dump(mode="json")

    run = TriageRun.model_validate(load_run())
    case_df = pd.DataFrame([case.model_dump(mode="json") for case in run.cases])
    risk_entries = build_risk_register(run)

    st.title("AI Safety Eval Triage Assistant")
    st.caption(
        "Fixture-first eval-ops decision support. "
        f"Analysis as of {run.analysis_as_of.date().isoformat()}; redacted summaries only."
    )

    overview, queue, clusters, risk_register, health, casepack = st.tabs(
        ["Overview", "Triage Queue", "Risk Clusters", "Risk Register", "Eval Health", "Casepack"]
    )

    with overview:
        escalation_ready = sum(
            case.escalation_tier in {"CRITICAL", "ELEVATED"} for case in run.cases
        )
        health_flags = (
            run.health.missing_label_count
            + run.health.evaluator_disagreement_count
            + run.health.low_reliability_count
            + run.health.stale_case_count
            + len(run.health.blind_spot_policies)
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Cases To Review", escalation_ready)
        k2.metric("Risk Register Entries", len(risk_entries))
        k3.metric("Explainable Clusters", len(run.clusters))
        k4.metric("Eval Health Flags", health_flags)

        left, right = st.columns(2)
        with left:
            st.subheader("Policy Coverage")
            policy_counts = pd.DataFrame(
                [
                    {"policy": policy_display_name(key), "cases": value}
                    for key, value in run.health.coverage_by_policy.items()
                ]
            )
            st.plotly_chart(px.bar(policy_counts, x="policy", y="cases"), use_container_width=True)
        with right:
            st.subheader("Escalation Tiers")
            tier_counts = case_df["escalation_tier"].value_counts().reset_index()
            tier_counts.columns = ["tier", "cases"]
            st.plotly_chart(
                px.pie(tier_counts, names="tier", values="cases"), use_container_width=True
            )

        st.subheader("Fixture Sanity Checks")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Escalation Precision", f"{run.metrics.escalation_precision:.3f}")
        m2.metric("Escalation Recall", f"{run.metrics.escalation_recall:.3f}")
        m3.metric("Cluster Precision", f"{run.metrics.cluster_pairwise_precision:.3f}")
        m4.metric("Cluster Recall", f"{run.metrics.cluster_pairwise_recall:.3f}")

    with queue:
        st.subheader("Ranked Eval Findings")
        min_score = st.slider("Minimum score", 0, 100, 35)
        filtered = case_df[case_df["escalation_score"] >= min_score].copy()
        filtered["policy"] = filtered["normalized_policy_family"].map(policy_display_name)
        filtered["why_escalated"] = filtered["reason_codes"].map(_reason_summary)
        st.dataframe(
            filtered[
                [
                    "case_id",
                    "escalation_tier",
                    "escalation_score",
                    "policy",
                    "evaluator_label",
                    "cluster_id",
                    "why_escalated",
                    "prompt_summary",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with clusters:
        st.subheader("Explainable Risk Clusters")
        for cluster in run.clusters:
            with st.expander(
                f"{cluster.cluster_id} · {policy_display_name(cluster.dominant_policy_family)} · "
                f"{cluster.escalation_tier} · max {cluster.max_score:.1f}",
                expanded=cluster.escalation_tier in {"CRITICAL", "ELEVATED"},
            ):
                st.write(cluster.rationale)
                st.write(
                    "Link and scoring signals:", _reason_summary(cluster.reason_codes, limit=12)
                )
                members = case_df[case_df["case_id"].isin(cluster.case_ids)]
                st.dataframe(
                    members[["case_id", "escalation_score", "evaluator_label", "prompt_summary"]],
                    use_container_width=True,
                    hide_index=True,
                )

    with risk_register:
        st.subheader("Emerging AI Risk Register")
        if risk_entries:
            register_df = pd.DataFrame([entry.model_dump() for entry in risk_entries])
            register_df["early_indicators"] = register_df["early_indicators"].map(
                lambda values: ", ".join(values)
            )
            st.dataframe(
                register_df[
                    [
                        "risk_area",
                        "severity",
                        "prevalence",
                        "exposure",
                        "trajectory",
                        "confidence",
                        "risk_score",
                        "early_indicators",
                        "abuse_pathway",
                        "recommended_mitigation",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No risk-register entries: every cluster in this run is LOW tier.")

    with health:
        st.subheader("Eval Health Heartbeat")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Missing Labels", run.health.missing_label_count)
        h2.metric("Disagreements", run.health.evaluator_disagreement_count)
        h3.metric("Low Reliability", run.health.low_reliability_count)
        h4.metric("Stale Cases", run.health.stale_case_count)
        blind_spots = ", ".join(map(policy_display_name, run.health.blind_spot_policies)) or "None"
        st.write("Blind spots:", blind_spots)
        st.dataframe(
            pd.DataFrame(
                run.health.coverage_by_attack_style.items(), columns=["attack_style", "cases"]
            ),
            use_container_width=True,
            hide_index=True,
        )

    with casepack:
        st.subheader("Cluster Casepack Preview")
        cluster_ids = [cluster.cluster_id for cluster in run.clusters]
        if cluster_ids:
            selected = st.selectbox("Cluster", cluster_ids)
            st.markdown(render_casepack(run, selected))
        else:
            st.info("No clusters were produced by this run.")


if __name__ == "__main__":
    main()
