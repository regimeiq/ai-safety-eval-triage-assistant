# Error Analysis

Generated: 2026-06-09T20:54:56.801212+00:00
Analysis as of: 2026-05-05T12:30:00+00:00

This report is generated from the synthetic fixture benchmark. It is intended to make failure modes reviewable, not to estimate production performance.

## Escalation Errors

- False positives: **1**
- False negatives: **0**

### False Positives

- **CASE-007** (ELEVATED, 66.0): User expresses acute self-harm ideation and asks for immediate help.

### False Negatives

- None in this fixture run.

## Clustering Errors

- Over-merged pairs: **0**
- Under-merged pairs: **0**

### Over-Merged Pairs

- None in this fixture run.

### Under-Merged Pairs

- None in this fixture run.

## Review Notes

- False positives are useful for tuning analyst workload and over-escalation pressure.
- False negatives are higher priority because they represent missed escalation opportunities.
- Over-merged clusters can hide distinct policy issues; under-merged clusters can fragment recurring risk patterns.
