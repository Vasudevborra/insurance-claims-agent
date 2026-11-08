"""
Agent architecture with 5 specialized deterministic agent roles:
1. Intake Agent: Validates mandatory fields and document completeness.
2. Policy Agent: Checks waiting periods, covered categories, and room limits.
3. Fraud Screening Agent: Flags rule-based risk indicators.
4. Adjudication Agent: Calculates estimated payable amount and recommendation.
5. Supervisor Agent: Determines priority and mandates human-in-the-loop review routing.
"""

from typing import Tuple, Optional
from src.rules import (
    validate_intake,
    check_coverage,
    evaluate_fraud_risk,
    calculate_adjudication,
    determine_supervisor_routing,
)


def run_intake_agent(claim: dict) -> Tuple[dict, str]:
    """Runs the Intake Agent stage."""
    result = validate_intake(claim)
    note = "Validated required fields and document-completeness flag."
    return result, note


def run_policy_agent(claim: dict, policy: Optional[dict]) -> Tuple[dict, str]:
    """Runs the Policy Coverage Agent stage."""
    result = check_coverage(claim, policy)
    note = "Matched claim category and policy waiting-period/limit rules."
    return result, note


def run_fraud_agent(claim: dict) -> Tuple[dict, str]:
    """Runs the Fraud Screening Agent stage."""
    result = evaluate_fraud_risk(claim)
    note = "Rule-based risk indicators; flags are not findings of fraud."
    return result, note


def run_adjudication_agent(claim: dict, policy_result: dict, policy: Optional[dict]) -> Tuple[dict, str]:
    """Runs the Adjudication Agent stage."""
    result = calculate_adjudication(claim, policy_result, policy)
    note = "Produces a recommendation for a reviewer; does not approve or reject a claim."
    return result, note


def run_supervisor_agent(
    claim: dict,
    intake_result: dict,
    policy_result: dict,
    fraud_result: dict,
) -> Tuple[dict, str]:
    """Runs the Supervisor Agent routing stage."""
    result = determine_supervisor_routing(claim, intake_result, policy_result, fraud_result)
    note = "Routes all cases to a human; no autonomous rejection or payout."
    return result, note
