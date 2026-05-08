from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EvalLabel = Literal["violation", "safe", "refusal", "ambiguous", "unlabeled"]
Severity = Literal["low", "medium", "high", "critical"]


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    case_id: str = Field(min_length=3)
    dataset_source: str = Field(min_length=3)
    model_name: str = Field(min_length=2)
    created_at: datetime
    prompt_summary: str = Field(min_length=12)
    response_summary: str = Field(min_length=12)
    policy_family: str = Field(min_length=3)
    expected_label: EvalLabel
    evaluator_label: EvalLabel
    severity: Severity
    attack_style: str = Field(min_length=3)
    evasion_signals: list[str] = Field(default_factory=list)
    signal_reliability: float = Field(ge=0.0, le=1.0)
    human_escalate: bool
    gold_cluster_id: str = Field(min_length=3)
    notes: str = ""

    @field_validator("case_id", "dataset_source", "model_name", "policy_family", "attack_style")
    @classmethod
    def _strip_required(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("value must not be blank")
        return clean

    @field_validator("prompt_summary", "response_summary")
    @classmethod
    def _block_unredacted_markers(cls, value: str) -> str:
        lowered = value.lower()
        blocked = ["full prompt:", "verbatim prompt:", "exact prompt:", "unredacted"]
        if any(marker in lowered for marker in blocked):
            raise ValueError("public fixture text must remain summarized/redacted")
        return value.strip()

    @field_validator("evasion_signals")
    @classmethod
    def _clean_signals(cls, values: list[str]) -> list[str]:
        return sorted({str(value).strip().lower() for value in values if str(value).strip()})


class TriageCase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    dataset_source: str
    model_name: str
    created_at: datetime
    prompt_summary: str
    response_summary: str
    policy_family: str
    normalized_policy_family: str
    expected_label: EvalLabel
    evaluator_label: EvalLabel
    severity: Severity
    attack_style: str
    evasion_signals: list[str]
    signal_reliability: float
    human_escalate: bool
    gold_cluster_id: str
    notes: str
    escalation_score: float
    escalation_tier: str
    reason_codes: list[str]
    cluster_id: str | None = None


class RiskCluster(BaseModel):
    cluster_id: str
    case_ids: list[str]
    size: int
    dominant_policy_family: str
    shared_attack_styles: list[str]
    shared_evasion_signals: list[str]
    max_score: float
    avg_score: float
    escalation_tier: str
    reason_codes: list[str]
    rationale: str


class EvalHealthSnapshot(BaseModel):
    total_cases: int
    coverage_by_policy: dict[str, int]
    coverage_by_dataset: dict[str, int]
    coverage_by_model: dict[str, int]
    coverage_by_attack_style: dict[str, int]
    missing_label_count: int
    missing_label_rate: float
    evaluator_disagreement_count: int
    evaluator_disagreement_rate: float
    low_reliability_count: int
    stale_case_count: int
    blind_spot_policies: list[str]


class TriageMetrics(BaseModel):
    escalation_precision: float
    escalation_recall: float
    escalation_f1: float
    false_positives: int
    false_negatives: int
    cluster_pairwise_precision: float
    cluster_pairwise_recall: float
    cluster_pairwise_f1: float
    cluster_true_positives: int
    cluster_false_positives: int
    cluster_false_negatives: int


class TriageRun(BaseModel):
    taxonomy_version: str
    analysis_as_of: datetime
    cases: list[TriageCase]
    clusters: list[RiskCluster]
    health: EvalHealthSnapshot
    metrics: TriageMetrics
    generated_at: datetime
