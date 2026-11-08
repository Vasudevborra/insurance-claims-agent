"""
Deterministic business rules for each stage of claim processing.
Each function represents a specific capability or rule check.
"""

REQUIRED_FIELDS = [
    "claim_id",
    "policy_id",
    "claim_type",
    "claim_amount",
    "admission_days",
    "policy_age_days",
    "provider_id",
    "patient_id",
    "documents_complete",
]

# Synthetic watchlist for provider screening
WATCHLIST_PROVIDERS = {"PRV-999", "PRV-888"}


def validate_intake(claim: dict) -> dict:
    """
    Stage 1: Intake validation.
    Checks that all required fields are filled and documents are flagged as complete.
    """
    missing = [k for k in REQUIRED_FIELDS if claim.get(k) in (None, "")]
    is_docs_complete = bool(claim.get("documents_complete"))
    status = "complete" if (not missing and is_docs_complete) else "incomplete"

    return {
        "status": status,
        "missing": missing,
    }


def check_coverage(claim: dict, policy: dict | None) -> dict:
    """
    Stage 2: Policy coverage check.
    Verifies policy existence, waiting period requirements, and covered treatment categories.
    """
    if not policy:
        return {
            "policy_found": False,
            "covered": False,
            "reason": "Policy not found",
            "eligible_limit": 0,
        }

    claim_type = str(claim.get("claim_type", "")).strip().lower()
    policy_age = int(claim.get("policy_age_days", 0))
    waiting_period = policy.get("waiting_period_days", 0)
    covered_categories = policy.get("coverage", [])

    is_waiting_period_met = policy_age >= waiting_period
    is_category_covered = claim_type in covered_categories
    is_covered = is_waiting_period_met and is_category_covered

    if is_covered:
        reason = "Covered benefit and waiting period satisfied"
    elif not is_waiting_period_met:
        reason = "Waiting period not satisfied"
    else:
        reason = "Claim type not listed in policy coverage"

    admission_days = max(1, int(claim.get("admission_days", 1)))
    eligible_limit = policy.get("room_limit", 0) * admission_days

    return {
        "policy_found": True,
        "covered": is_covered,
        "reason": reason,
        "eligible_limit": eligible_limit,
    }


def evaluate_fraud_risk(claim: dict) -> dict:
    """
    Stage 3: Fraud screening.
    Applies heuristic risk indicators (flags only, never declares fraud).
    """
    flags = []
    amount = float(claim.get("claim_amount", 0))
    admission_days = int(claim.get("admission_days", 0))
    provider_id = str(claim.get("provider_id", "")).strip().upper()
    prior_similar = bool(claim.get("prior_similar_claim"))

    if amount >= 200000:
        flags.append("High claim amount (≥ ₹2,00,000)")
    if admission_days >= 10:
        flags.append("Long admission (≥ 10 days)")
    if provider_id in WATCHLIST_PROVIDERS:
        flags.append("Provider on synthetic watchlist")
    if prior_similar:
        flags.append("Prior similar claim indicated")

    fraud_score = min(1.0, 0.25 * len(flags))

    return {
        "risk_score": round(fraud_score, 2),
        "flags": flags,
        "status": "review flag" if flags else "no rule-based flag",
    }


def calculate_adjudication(claim: dict, policy_result: dict, policy: dict | None) -> dict:
    """
    Stage 4: Adjudication recommendation.
    Calculates eligible payable amount subtracting deductible.
    """
    amount = float(claim.get("claim_amount", 0))
    is_covered = policy_result.get("covered", False)
    eligible_limit = float(policy_result.get("eligible_limit", 0))

    if is_covered and policy:
        eligible = min(amount, eligible_limit)
        deductible = policy.get("deductible", 0)
        recommended = max(0.0, eligible - deductible)
        recommendation = "Potentially payable"
    else:
        recommended = 0.0
        recommendation = "Not eligible under configured rules"

    return {
        "recommendation": recommendation,
        "estimated_payable_inr": round(recommended, 2),
        "basis": policy_result.get("reason", ""),
    }


def determine_supervisor_routing(
    claim: dict,
    intake_result: dict,
    policy_result: dict,
    fraud_result: dict,
) -> dict:
    """
    Stage 5: Supervisor routing.
    Determines priority and mandates human review for all claims in this prototype.
    """
    amount = float(claim.get("claim_amount", 0))
    high_value = amount >= 100000
    has_flags = bool(fraud_result.get("flags"))
    is_incomplete = intake_result.get("status") != "complete"
    is_uncovered = not policy_result.get("covered", False)

    requires_human = is_incomplete or high_value or has_flags or is_uncovered

    reasons = []
    if is_incomplete:
        reasons.append("Incomplete intake/documents")
    if high_value:
        reasons.append("High-value claim")
    if has_flags:
        reasons.append("Fraud-risk flag(s)")
    if is_uncovered:
        reasons.append("Coverage rule not satisfied")
    if not reasons:
        reasons.append("Mandatory human sign-off for all claim outcomes in this prototype")

    is_high_priority = high_value or has_flags or is_incomplete
    priority = "High" if is_high_priority else "Standard"
    authority = "Human reviewer" if requires_human else "Human reviewer (standard queue)"

    return {
        "decision_authority": authority,
        "priority": priority,
        "human_review_required": True,
        "reason": reasons,
    }
