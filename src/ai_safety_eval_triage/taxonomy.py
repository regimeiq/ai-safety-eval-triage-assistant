from __future__ import annotations

POLICY_FAMILIES = {
    "cyber_safety": "Cyber Safety",
    "fraud_scam": "Fraud & Scams",
    "harassment_hate": "Harassment & Hate",
    "violence_threats": "Violence & Threats",
    "self_harm": "Self-Harm",
    "privacy_data": "Privacy & Personal Data",
    "sexual_content": "Sexual Content",
    "policy_boundary": "Policy Boundary / Dual Use",
    "benign_near_miss": "Benign Near-Miss",
}

ALIASES = {
    "cyber": "cyber_safety",
    "cybersecurity": "cyber_safety",
    "fraud": "fraud_scam",
    "scam": "fraud_scam",
    "harassment": "harassment_hate",
    "hate": "harassment_hate",
    "violence": "violence_threats",
    "threat": "violence_threats",
    "self-harm": "self_harm",
    "self harm": "self_harm",
    "privacy": "privacy_data",
    "personal_data": "privacy_data",
    "dual_use": "policy_boundary",
    "boundary": "policy_boundary",
    "benign": "benign_near_miss",
}


def normalize_policy_family(value: str) -> str:
    clean = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
    return ALIASES.get(clean, clean)


def policy_display_name(policy_family: str) -> str:
    normalized = normalize_policy_family(policy_family)
    return POLICY_FAMILIES.get(normalized, normalized.replace("_", " ").title())
