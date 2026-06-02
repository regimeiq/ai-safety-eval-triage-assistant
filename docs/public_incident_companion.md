# Public Incident Companion Case Study

## Source Feasibility

Public incident datasets are useful for validating whether a triage workflow can reason about real-world risk patterns, but they are not included in the default demo run.

Sources reviewed:

- [AI Incident Database](https://incidentdatabase.ai/) and its [public GraphQL endpoint](https://github.com/responsible-ai-collaborative/aiid#public-graphql-endpoint)
- [Butterfly Labs AI Incident Database dataset](https://huggingface.co/datasets/butterflylabs/ai-incidents), an aggregated AI incident metadata dataset
- Public AI safety eval datasets such as HarmBench-style, AgentHarm-style, and FORTRESS-style benchmarks

Default ingestion was not added because public incident datasets are continuously updated and often include named parties, copyrighted summaries, or source-specific context. Public eval datasets may also include adversarial prompt text that is not appropriate to mirror in a public portfolio artifact.

## Companion Mapping

The table below shows how public incident-style records can be mapped into this triage workflow without copying full reports or prompt text.

| Public Signal Pattern | Triage Mapping | Review Use |
|---|---|---|
| AI-generated impersonation used in a financial scam | `fraud_scam`, high severity, synthetic-media or impersonation signal, external incident source | Create eval coverage for scam enablement, social engineering, and impersonation guardrail behavior |
| Sensitive personal or student data processed through AI tooling without clear authorization | `privacy_data`, medium or high severity, sensitive-data and third-party-processing signals | Track privacy-risk coverage, exposure, and mitigation follow-through |
| AI-generated legal or procedural material causing downstream institutional strain | `policy_boundary`, medium severity, reliability and domain-misuse signals | Flag taxonomy gaps where the fixture does not yet represent professional-domain misuse well |
| Public reports of unsafe chatbot advice in crisis or threat contexts | `self_harm` or `violence_threats`, high or critical severity, crisis-context signal | Prioritize supportive-completion and refusal-consistency eval coverage |

## How This Would Be Used

An analyst could sample public incident metadata, write redacted summaries, normalize them into the local schema, and run them through the same queue, cluster, health, and register outputs.

The key control is redaction: the workflow needs incident-level signals and risk categories, not verbatim harmful prompts or sensitive personal details.

## Why The Demo Remains Synthetic

The checked-in fixture is synthetic so the repository remains stable, reproducible, and public-safe. The public companion demonstrates that the schema can be extended to incident intelligence without claiming that this repo has run live incident monitoring.
