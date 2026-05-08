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

from ai_safety_eval_triage.ingest import load_eval_cases
from ai_safety_eval_triage.models import TriageRun
from ai_safety_eval_triage.pipeline import run_triage
from ai_safety_eval_triage.risk_register import build_risk_register
from ai_safety_eval_triage.reports import render_casepack
from ai_safety_eval_triage.taxonomy import policy_display_name

st.set_page_config(page_title="AI Safety Eval Triage", layout="wide")


@st.cache_data(show_spinner=False)
def load_run() -> dict:
    out_path = Path("out/triage_run.json")
    if out_path.exists():
        return json.loads(out_path.read_text(encoding="utf-8"))
    taxonomy_version, cases = load_eval_cases("fixtures/eval_cases.json")
    return run_triage(cases, taxonomy_version).model_dump(mode="json")


run = TriageRun.model_validate(load_run())
case_df = pd.DataFrame([case.model_dump(mode="json") for case in run.cases])
cluster_df = pd.DataFrame([cluster.model_dump(mode="json") for cluster in run.clusters])

st.title("AI Safety Eval Triage Assistant")
st.caption("Fixture-first eval-ops decision support. Redacted summaries only; no external APIs.")

overview, queue, clusters, risk_register, health, casepack = st.tabs(
    ["Overview", "Triage Queue", "Risk Clusters", "Risk Register", "Eval Health", "Casepack"]
)

with overview:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Eval Cases", len(run.cases))
    k2.metric("Risk Clusters", len(run.clusters))
    k3.metric("Escalation F1", f"{run.metrics.escalation_f1:.3f}")
    k4.metric("Cluster F1", f"{run.metrics.cluster_pairwise_f1:.3f}")

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
        st.plotly_chart(px.pie(tier_counts, names="tier", values="cases"), use_container_width=True)

with queue:
    st.subheader("Ranked Eval Findings")
    min_score = st.slider("Minimum score", 0, 100, 35)
    filtered = case_df[case_df["escalation_score"] >= min_score].copy()
    filtered["policy"] = filtered["normalized_policy_family"].map(policy_display_name)
    st.dataframe(
        filtered[
            [
                "case_id",
                "escalation_tier",
                "escalation_score",
                "policy",
                "evaluator_label",
                "cluster_id",
                "prompt_summary",
                "reason_codes",
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
            st.write("Reason codes:", ", ".join(cluster.reason_codes[:12]))
            members = case_df[case_df["case_id"].isin(cluster.case_ids)]
            st.dataframe(
                members[["case_id", "escalation_score", "evaluator_label", "prompt_summary"]],
                use_container_width=True,
                hide_index=True,
            )

with risk_register:
    st.subheader("Emerging AI Risk Register")
    entries = build_risk_register(run)
    register_df = pd.DataFrame([entry.model_dump() for entry in entries])
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
                "abuse_pathway",
                "recommended_mitigation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with health:
    st.subheader("Eval Health Heartbeat")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Missing Labels", run.health.missing_label_count)
    h2.metric("Disagreements", run.health.evaluator_disagreement_count)
    h3.metric("Low Reliability", run.health.low_reliability_count)
    h4.metric("Stale Cases", run.health.stale_case_count)
    st.write("Blind spots:", ", ".join(map(policy_display_name, run.health.blind_spot_policies)) or "None")
    st.dataframe(pd.DataFrame(run.health.coverage_by_attack_style.items(), columns=["attack_style", "cases"]))

with casepack:
    st.subheader("Cluster Casepack Preview")
    cluster_ids = [cluster.cluster_id for cluster in run.clusters]
    selected = st.selectbox("Cluster", cluster_ids)
    st.markdown(render_casepack(run, selected))
