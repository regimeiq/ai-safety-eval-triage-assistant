# Methodology

## Goal

The assistant turns AI safety eval findings into reviewable triage artifacts: ranked cases, explainable risk clusters, eval-health telemetry, an emerging-risk register, and error analysis.

It is human-in-the-loop decision support. It does not automate enforcement or claim production safety performance.

## Pipeline

1. **Ingest:** Load fixture or imported CSV/JSON cases and validate them with Pydantic.
2. **Normalize:** Map policy-family aliases into a consistent taxonomy.
3. **Score:** Assign a deterministic escalation score using severity, evaluator label, attack style, evasion signals, signal reliability, missing labels, and cluster recurrence.
4. **Cluster:** Build TF-IDF representations over redacted summaries plus policy/attack metadata, then link cases with transparent reason codes.
5. **Evaluate:** Compare escalation decisions against `human_escalate` and cluster links against `gold_cluster_id`.
6. **Monitor:** Summarize coverage, missing labels, evaluator disagreement, low-reliability signals, stale cases, and blind-spot policy families.
7. **Report:** Generate Markdown artifacts and a Streamlit dashboard for human review.

## Scoring

The escalation score is rule-based and intentionally interpretable. Inputs include:

- severity tier
- normalized policy family
- evaluator label
- missing-label status
- attack style
- evasion signals
- signal reliability
- recurrence in a cluster

Scores are not calibrated probabilities. They are prioritization scores for triage review.

## Clustering

Cases are linked when there is enough evidence that they belong to the same reviewable risk family. Linkage signals include:

- same policy family
- shared attack style with minimum semantic similarity
- shared evasion signals
- TF-IDF semantic similarity over summaries and metadata
- shared dataset source as supporting context

The clustering method is intentionally lightweight. It is suitable for small to medium local eval exports, not large-scale production queues.

## Metrics

The project reports:

- escalation precision, recall, and F1
- false positives and false negatives
- pairwise cluster precision, recall, and F1
- over-merged and under-merged cluster pairs
- missing-label rate
- evaluator disagreement rate
- low-reliability and stale-case counts

Metrics are scoped to the synthetic fixture benchmark.

## Risk Register

The emerging-risk register summarizes non-low risk clusters by:

- risk area
- abuse pathway
- early indicators
- severity
- prevalence
- exposure
- trajectory
- confidence
- monitoring signals
- recommended mitigation

The register is a structured analytic output, not a production risk assessment.

## Limitations

- Synthetic fixtures cannot estimate production prevalence.
- Rule-based scoring is explainable but not calibrated.
- TF-IDF similarity is transparent but shallow.
- No public benchmark is downloaded or run by default.
- No multi-rater reliability study is included.
- Redacted summaries trade realism for public safety.

## Extension Path

The intended next step is not live scraping. The safer extension is importing local benchmark-style eval exports through `scripts/import_cases.py`, then reviewing the normalized cases before public use.
