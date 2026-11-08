"""
Orchestrates the sequential claim processing workflow across 5 specialized agent stages.
Operates purely using deterministic business rules, matching the M3 prototype specifications.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.policies import get_policy
from src.agents import (
    run_intake_agent,
    run_policy_agent,
    run_fraud_agent,
    run_adjudication_agent,
    run_supervisor_agent,
)


def process_claim(
    claim: dict,
    audit_log: Optional[List[dict]] = None,
) -> dict:
    """
    Executes the 5-stage claims processing workflow.
    
    Args:
        claim: Dictionary with claim fields.
        audit_log: Optional list to append the audit trail entry into.
        
    Returns:
        Structured output containing individual stage outputs and full execution trace.
    """
    trace = []

    # Stage 1: Intake Agent
    intake, note_intake = run_intake_agent(claim=claim)
    trace.append({
        "agent": "Intake Agent",
        "result": intake,
        "note": note_intake,
    })

    # Stage 2: Policy Agent
    policy = get_policy(str(claim.get("policy_id", "")))
    policy_result, note_policy = run_policy_agent(claim=claim, policy=policy)
    trace.append({
        "agent": "Policy Agent",
        "result": policy_result,
        "note": note_policy,
    })

    # Stage 3: Fraud Screening Agent
    fraud, note_fraud = run_fraud_agent(claim=claim)
    trace.append({
        "agent": "Fraud Screening Agent",
        "result": fraud,
        "note": note_fraud,
    })

    # Stage 4: Adjudication Agent
    adjudication, note_adj = run_adjudication_agent(
        claim=claim,
        policy_result=policy_result,
        policy=policy,
    )
    trace.append({
        "agent": "Adjudication Agent",
        "result": adjudication,
        "note": note_adj,
    })

    # Stage 5: Supervisor Agent
    route, note_sup = run_supervisor_agent(
        claim=claim,
        intake_result=intake,
        policy_result=policy_result,
        fraud_result=fraud,
    )
    trace.append({
        "agent": "Supervisor Agent",
        "result": route,
        "note": note_sup,
    })

    output = {
        "claim_id": claim.get("claim_id", ""),
        "intake": intake,
        "policy": policy_result,
        "fraud": fraud,
        "adjudication": adjudication,
        "routing": route,
        "trace": trace,
    }

    if audit_log is not None:
        audit_log.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "claim_id": claim.get("claim_id", ""),
            "human_review_required": True,
            "priority": route["priority"],
            "trace": json.dumps(trace, ensure_ascii=False),
        })

    return output
