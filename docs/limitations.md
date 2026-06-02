# Limitations

## Public Scope

This repository is a public, local workflow demonstration. It does not contain live user data, proprietary evals, full harmful prompts, provider-specific model access, or operational deployment evidence.

## Data Limits

- The default fixture is synthetic and redacted.
- Fixture prevalence cannot estimate real-world abuse prevalence.
- Labels are hand-authored for workflow testing, not produced by a multi-rater adjudication process.
- Summaries are safer for public display but less expressive than full eval records.
- Some policy families are intentionally under-covered so the health checks can surface blind spots.

## Scoring Limits

- Escalation scores are prioritization signals, not calibrated probabilities.
- Rule-based scoring is explainable but can overweight hand-authored fixture assumptions.
- Human review is required before policy, product, safety, or enforcement action.

## Clustering Limits

- TF-IDF similarity is transparent and easy to audit, but shallow.
- Small fixture clusters can look cleaner than messy real review queues.
- Over-merged clusters can hide distinct risks; under-merged clusters can fragment recurring patterns.

## Metrics Limits

- Precision, recall, and F1 are synthetic fixture sanity checks.
- Metrics do not describe a deployed model, platform, or provider.
- The fixture is too small to support claims about production reliability.

## Public Dataset Handling

Public AI incident and safety-eval datasets can be useful companion material, but many include sensitive incident descriptions, names, copyrighted summaries, or adversarial prompt text. This repo does not download or ingest those datasets by default.

The safer default is a synthetic fixture plus a documented public-incident mapping note in `docs/public_incident_companion.md`.
