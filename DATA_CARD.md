# Data Card

## Dataset

The default dataset is `fixtures/eval_cases.json`, a synthetic, redacted set of AI safety eval cases. It is designed to exercise the tool's triage workflow, not to estimate real-world misuse rates or model safety performance.

## Intended Use

- Demonstrate ingestion, validation, scoring, clustering, eval-health telemetry, error analysis, and emerging-risk reporting.
- Provide a safe public demo without live user data, personally identifiable information, harmful prompt corpora, external API calls, or benchmark downloads.
- Support local experimentation with the import adapter for benchmark-style CSV/JSON exports.
- Generate review artifacts in `outputs/` that make the triage queue, risk clusters, and risk register inspectable outside the dashboard.

## Not Intended For

- Production trust & safety enforcement.
- Measuring real-world abuse prevalence.
- Claiming official benchmark performance.
- Evaluating a deployed model provider.
- Publishing verbatim harmful prompts or sensitive user content.
- Claiming operational use of public incident data.

## Schema

Each case includes:

- `case_id`
- `dataset_source`
- `model_name`
- `created_at`
- `prompt_summary`
- `response_summary`
- `policy_family`
- `expected_label`
- `evaluator_label`
- `severity`
- `attack_style`
- `evasion_signals`
- `signal_reliability`
- `human_escalate`
- `gold_cluster_id`
- `notes`

The public fixture uses summaries rather than full prompts or full responses. Validation rejects fields outside the schema and blocks common markers for unredacted prompt text.

## Label Semantics

- `expected_label`: the intended gold label for the case.
- `evaluator_label`: the observed evaluator/model-judge label.
- `human_escalate`: whether the case should be escalated in this scoped fixture benchmark.
- `gold_cluster_id`: hand-authored cluster family used for pairwise clustering metrics.

## Known Limitations

- Synthetic cases are small-scale and easier to reason about than real eval logs.
- Labels are hand-authored for demonstration, not produced through a multi-rater adjudication process.
- Harm categories are intentionally broad.
- Metrics are valid only for this fixture benchmark.
- Time-based health outputs are computed from the run's fixture-derived `analysis_as_of` timestamp for reproducibility.
- Redacted summaries are safer for public display but less expressive than full eval records.
- Public incident datasets are discussed as companion material in `docs/public_incident_companion.md`, but are not downloaded or ingested by default.

## Safety Handling

- No live data collection.
- No real user data.
- No PII.
- No external network calls.
- No verbatim harmful prompt corpus.
- Generated reports reiterate that results are scoped demonstration outputs.
