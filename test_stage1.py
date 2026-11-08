"""
Stage 1 verification test suite.
Validates the modularized core logic against the 10 defined test scenarios.
"""

import sys
from pathlib import Path

# Add current folder to sys.path
BASE = Path(__file__).parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from src.policies import POLICY, get_policy
from src.workflow import process_claim


def run_all_tests():
    print("==================================================")
    print("Running Stage 1 Verification Suite")
    print("==================================================")

    # Base valid claim template
    base_claim = {
        "claim_id": "TEST-001",
        "policy_id": "POL-200",
        "claim_type": "hospitalization",
        "claim_amount": 45000.0,
        "admission_days": 2,
        "policy_age_days": 365,
        "provider_id": "PRV-101",
        "patient_id": "PAT-001",
        "documents_complete": True,
        "prior_similar_claim": False,
    }

    tests_passed = 0

    # T01: Covered claim with estimate calculated
    res_t01 = process_claim({**base_claim, "claim_id": "T01"})
    assert res_t01["policy"]["covered"] is True, "T01 failed: should be covered"
    assert res_t01["adjudication"]["estimated_payable_inr"] > 0, "T01 failed: payable should be > 0"
    assert res_t01["routing"]["human_review_required"] is True, "T01 failed: human review required"
    print(" [PASS] T01: Covered low-value claim")
    tests_passed += 1

    # T02: Waiting period not met
    res_t02 = process_claim({**base_claim, "claim_id": "T02", "policy_id": "POL-100", "policy_age_days": 20})
    assert res_t02["policy"]["covered"] is False, "T02 failed: should not be covered"
    assert "Waiting period not satisfied" in res_t02["policy"]["reason"], "T02 failed: reason mismatch"
    print(" [PASS] T02: Waiting period not met")
    tests_passed += 1

    # T03: Unsupported benefit (maternity on POL-100)
    res_t03 = process_claim({**base_claim, "claim_id": "T03", "policy_id": "POL-100", "claim_type": "maternity"})
    assert res_t03["policy"]["covered"] is False, "T03 failed: should not be covered"
    assert "not listed in policy coverage" in res_t03["policy"]["reason"], "T03 failed: reason mismatch"
    print(" [PASS] T03: Unsupported benefit category")
    tests_passed += 1

    # T04: High-value claim (>= 200,000)
    res_t04 = process_claim({**base_claim, "claim_id": "T04", "claim_amount": 250000.0})
    assert res_t04["routing"]["priority"] == "High", "T04 failed: should be High priority"
    assert any("High claim amount" in f for f in res_t04["fraud"]["flags"]), "T04 failed: flag missing"
    print(" [PASS] T04: High-value claim priority")
    tests_passed += 1

    # T05: Watchlisted synthetic provider (PRV-999)
    res_t05 = process_claim({**base_claim, "claim_id": "T05", "provider_id": "PRV-999"})
    assert any("watchlist" in f for f in res_t05["fraud"]["flags"]), "T05 failed: provider flag missing"
    print(" [PASS] T05: Watchlisted synthetic provider")
    tests_passed += 1

    # T06: Incomplete documents
    res_t06 = process_claim({**base_claim, "claim_id": "T06", "documents_complete": False})
    assert res_t06["intake"]["status"] == "incomplete", "T06 failed: intake status mismatch"
    assert res_t06["routing"]["priority"] == "High", "T06 failed: incomplete should be high priority"
    print(" [PASS] T06: Incomplete documents")
    tests_passed += 1

    # T07: Long admission (>= 10 days)
    res_t07 = process_claim({**base_claim, "claim_id": "T07", "admission_days": 12})
    assert any("Long admission" in f for f in res_t07["fraud"]["flags"]), "T07 failed: admission flag missing"
    print(" [PASS] T07: Long admission risk indicator")
    tests_passed += 1

    # T08: Unknown policy ID
    res_t08 = process_claim({**base_claim, "claim_id": "T08", "policy_id": "POL-999"})
    assert res_t08["policy"]["policy_found"] is False, "T08 failed: policy should not be found"
    assert res_t08["adjudication"]["estimated_payable_inr"] == 0, "T08 failed: payable should be 0"
    print(" [PASS] T08: Unknown policy handled safely")
    tests_passed += 1

    # T09: Prior similar claim
    res_t09 = process_claim({**base_claim, "claim_id": "T09", "prior_similar_claim": True})
    assert any("Prior similar claim" in f for f in res_t09["fraud"]["flags"]), "T09 failed: prior claim flag missing"
    print(" [PASS] T09: Prior similar claim flag")
    tests_passed += 1

    # T10: All standard checks clear
    res_t10 = process_claim({**base_claim, "claim_id": "T10", "claim_amount": 15000.0, "admission_days": 1})
    assert res_t10["routing"]["priority"] == "Standard", "T10 failed: priority should be Standard"
    assert res_t10["routing"]["human_review_required"] is True, "T10 failed: human sign-off still mandatory"
    print(" [PASS] T10: Clean claim routed to standard human review")
    tests_passed += 1

    print("==================================================")
    print(f"Results: {tests_passed}/10 tests passed successfully!")
    print("Stage 1 modular refactoring verified!")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
