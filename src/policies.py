"""
Policy definitions and helper functions for synthetic health insurance plans.
"""

# Synthetic illustrative policies
# In production, these would be loaded from an insurer's underwriting system.
POLICY = {
    "POL-100": {
        "name": "Essential Health Plan",
        "room_limit": 5000,
        "coverage": ["hospitalization", "surgery", "diagnostics"],
        "waiting_period_days": 30,
        "deductible": 1000,
    },
    "POL-200": {
        "name": "Comprehensive Health Plan",
        "room_limit": 10000,
        "coverage": ["hospitalization", "surgery", "diagnostics", "maternity"],
        "waiting_period_days": 0,
        "deductible": 500,
    },
    "POL-300": {
        "name": "Senior Care Plan",
        "room_limit": 7000,
        "coverage": ["hospitalization", "surgery", "diagnostics"],
        "waiting_period_days": 90,
        "deductible": 1500,
    },
}


def get_policy(policy_id: str) -> dict | None:
    """Safely fetch policy configuration by ID."""
    if not policy_id:
        return None
    return POLICY.get(str(policy_id).strip())
