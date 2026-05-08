# Emerging AI Risk Register

Generated: 2026-05-08T14:07:13.948814+00:00
Analysis as of: 2026-05-05T12:30:00+00:00

This register is a scoped demonstration artifact derived from synthetic eval fixtures. It is intended to demonstrate emerging-risk triage, not estimate production prevalence.

| Risk Area | Abuse Pathway | Severity | Prevalence | Exposure | Trajectory | Confidence | Score | Monitoring Signals | Recommended Mitigation |
|---|---|---|---|---|---|---|---:|---|---|
| Cyber Safety | jailbreak, roleplay; indicators include benign pretext, credential targeting, fictional framing | CRITICAL | Moderate | Moderate | Emerging | High | 100.0 | Cyber Safety eval coverage; evaluator disagreement rate; escalation precision/recall; benign pretext; credential targeting; fictional framing | Add targeted jailbreak/evasion cases for credential-abuse scenarios; review refusal consistency and route high-confidence failures into model feedback. |
| Fraud & Scams | direct request, obfuscation; indicators include financial targeting, logging gap, social engineering | CRITICAL | Moderate | Broad | Emerging | Low | 100.0 | Fraud & Scams eval coverage; evaluator disagreement rate; escalation precision/recall; financial targeting; logging gap; social engineering | Expand scam and social-engineering eval coverage; monitor low-reliability reports separately from confirmed violations. |
| Policy Boundary / Dual Use | policy boundary; indicators include benign pretext, dual use ambiguity | CRITICAL | Moderate | Narrow | Emerging | Low | 100.0 | Policy Boundary / Dual Use eval coverage; evaluator disagreement rate; escalation precision/recall; benign pretext; dual use ambiguity | Separate dual-use educational context from procedural enablement and route ambiguous cases to policy review. |
| Self-Harm | direct request; indicators include private planning | CRITICAL | Moderate | Moderate | Emerging | Medium | 100.0 | Self-Harm eval coverage; evaluator disagreement rate; escalation precision/recall; private planning | Review supportive-completion behavior and escalate ambiguous failures even when evaluator confidence is imperfect. |
| Violence & Threats | direct request; indicators include targeted abuse, threatening intent | CRITICAL | Low | Narrow | Needs Refresh | High | 100.0 | Violence & Threats eval coverage; evaluator disagreement rate; escalation precision/recall; targeted abuse; threatening intent | Refresh stale violent-threat eval cases and prioritize refusal consistency for targeted intimidation requests. |
| Privacy & Personal Data | obfuscation; indicators include benign pretext, personal data targeting | CRITICAL | Low | Narrow | Emerging | Medium | 95.0 | Privacy & Personal Data eval coverage; evaluator disagreement rate; escalation precision/recall; benign pretext; personal data targeting | Expand personal-data targeting tests and validate that benign privacy-protection requests remain allowed. |
| Harassment & Hate | direct request; indicators include targeted abuse | CRITICAL | Low | Narrow | Emerging | Medium | 85.0 | Harassment & Hate eval coverage; evaluator disagreement rate; escalation precision/recall; targeted abuse | Add targeted-abuse near-misses and track false-positive pressure on heated but non-abusive speech. |

## Early Indicators By Risk Area

### Cyber Safety

- Source cases: CASE-001, CASE-002
- Early indicators: benign pretext, credential targeting, fictional framing, recurring case family

### Fraud & Scams

- Source cases: CASE-004, CASE-005, CASE-018
- Early indicators: financial targeting, logging gap, social engineering, evaluator/model-judge disagreement, low-reliability or incomplete signal, recurring case family

### Policy Boundary / Dual Use

- Source cases: CASE-012, CASE-013
- Early indicators: benign pretext, dual use ambiguity, evaluator/model-judge disagreement, recurring case family

### Self-Harm

- Source cases: CASE-006, CASE-007
- Early indicators: private planning, evaluator/model-judge disagreement, recurring case family

### Violence & Threats

- Source cases: CASE-014
- Early indicators: targeted abuse, threatening intent

### Privacy & Personal Data

- Source cases: CASE-010
- Early indicators: benign pretext, personal data targeting

### Harassment & Hate

- Source cases: CASE-008
- Early indicators: targeted abuse

