import json
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

# Ensure src is importable regardless of launch directory
BASE = Path(__file__).parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from src.policies import POLICY
from src.workflow import process_claim

DATA = BASE / "data"

st.set_page_config(page_title="Agentic Insurance Claims Processing", page_icon="🛡️", layout="wide")
st.title("🛡️ Agentic AI — Health Insurance Claims Processing")
st.caption("Academic prototype • Synthetic data only • Human-in-the-loop decision support")

if "claim_history" not in st.session_state:
    sample_path = DATA / "synthetic_claims.csv"
    st.session_state.claim_history = pd.read_csv(sample_path).to_dict("records") if sample_path.exists() else []
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []


def run_predefined_m3_tests():
    """Runs the 10 repeatable software behavior checks defined in Chapter 4."""
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

    test_definitions = [
        {
            "test_id": "T01",
            "scenario": "Covered low-value claim",
            "claim": {**base_claim, "claim_id": "T01"},
            "expected": "Covered; estimate calculated; human sign-off required",
            "validator": lambda r: r["policy"]["covered"] is True and r["adjudication"]["estimated_payable_inr"] > 0 and r["routing"]["human_review_required"] is True,
        },
        {
            "test_id": "T02",
            "scenario": "Waiting period not met",
            "claim": {**base_claim, "claim_id": "T02", "policy_id": "POL-100", "policy_age_days": 20},
            "expected": "Coverage rule not satisfied; human review",
            "validator": lambda r: r["policy"]["covered"] is False and "Waiting period" in r["policy"]["reason"] and r["routing"]["human_review_required"] is True,
        },
        {
            "test_id": "T03",
            "scenario": "Unsupported benefit",
            "claim": {**base_claim, "claim_id": "T03", "policy_id": "POL-100", "claim_type": "maternity"},
            "expected": "Benefit not covered by configured policy; human review",
            "validator": lambda r: r["policy"]["covered"] is False and r["routing"]["human_review_required"] is True,
        },
        {
            "test_id": "T04",
            "scenario": "High-value claim",
            "claim": {**base_claim, "claim_id": "T04", "claim_amount": 250000.0},
            "expected": "High priority; human review",
            "validator": lambda r: r["routing"]["priority"] == "High" and any("High claim amount" in f for f in r["fraud"]["flags"]),
        },
        {
            "test_id": "T05",
            "scenario": "Synthetic watchlisted provider",
            "claim": {**base_claim, "claim_id": "T05", "provider_id": "PRV-999"},
            "expected": "Risk flag shown; no fraud determination",
            "validator": lambda r: any("watchlist" in f for f in r["fraud"]["flags"]),
        },
        {
            "test_id": "T06",
            "scenario": "Incomplete documents",
            "claim": {**base_claim, "claim_id": "T06", "documents_complete": False},
            "expected": "Intake incomplete; high-priority human review",
            "validator": lambda r: r["intake"]["status"] == "incomplete" and r["routing"]["priority"] == "High",
        },
        {
            "test_id": "T07",
            "scenario": "Long admission",
            "claim": {**base_claim, "claim_id": "T07", "admission_days": 12},
            "expected": "Long-admission indicator; reviewer assessment",
            "validator": lambda r: any("Long admission" in f for f in r["fraud"]["flags"]),
        },
        {
            "test_id": "T08",
            "scenario": "Unknown policy",
            "claim": {**base_claim, "claim_id": "T08", "policy_id": "POL-999"},
            "expected": "Policy not found; no estimate; human review",
            "validator": lambda r: r["policy"]["policy_found"] is False and r["adjudication"]["estimated_payable_inr"] == 0,
        },
        {
            "test_id": "T09",
            "scenario": "Prior similar claim indicator",
            "claim": {**base_claim, "claim_id": "T09", "prior_similar_claim": True},
            "expected": "Risk flag; no automatic denial",
            "validator": lambda r: any("Prior similar claim" in f for f in r["fraud"]["flags"]),
        },
        {
            "test_id": "T10",
            "scenario": "Standard checks clear",
            "claim": {**base_claim, "claim_id": "T10"},
            "expected": "Standard queue; mandatory human sign-off",
            "validator": lambda r: r["routing"]["priority"] == "Standard" and r["routing"]["human_review_required"] is True,
        },
    ]

    records = []
    for item in test_definitions:
        res = process_claim(item["claim"])
        is_pass = item["validator"](res)
        obs = (
            f"Covered={res['policy']['covered']}; "
            f"payable estimate=₹{res['adjudication']['estimated_payable_inr']:,.0f}; "
            f"risk={res['fraud']['risk_score']:.0%}; "
            f"priority={res['routing']['priority']}; "
            f"human review={res['routing']['human_review_required']}"
        )
        records.append({
            "Test ID": item["test_id"],
            "Scenario": item["scenario"],
            "Expected behavior": item["expected"],
            "Observed behavior": obs,
            "Status": "PASS" if is_pass else "FAIL",
        })
    return pd.DataFrame(records)


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Claims Workbench",
    "Synthetic Claims",
    "Governance & Audit",
    "Prototype Notes",
    "M3 Evaluation",
])

# ----------------------------------------------------
# TAB 1: Claims Workbench
# ----------------------------------------------------
with tab1:
    st.subheader("Submit a synthetic claim")
    with st.form("claim_form"):
        c1, c2, c3 = st.columns(3)
        claim_id = c1.text_input("Claim ID", value=f"CLM-{len(st.session_state.claim_history)+1:04d}")
        policy_id = c2.selectbox("Policy", list(POLICY.keys()))
        claim_type = c3.selectbox("Claim category", ["hospitalization", "surgery", "diagnostics", "maternity"])
        
        c4, c5, c6 = st.columns(3)
        claim_amount = c4.number_input("Claim amount (₹)", min_value=0.0, value=85000.0, step=5000.0)
        admission_days = c5.number_input("Admission days", min_value=0, value=3, step=1)
        policy_age_days = c6.number_input("Policy age (days)", min_value=0, value=365, step=30)
        
        c7, c8, c9 = st.columns(3)
        provider_id = c7.text_input("Provider ID", value="PRV-101")
        patient_id = c8.text_input("Synthetic patient ID", value="PAT-001")
        documents_complete = c9.checkbox("Required documents complete", value=True)
        
        prior_similar_claim = st.checkbox("Prior similar claim indicated", value=False)
        submitted = st.form_submit_button("Run agent workflow", type="primary")

    if submitted:
        claim = {
            "claim_id": claim_id.strip() or f"CLM-{len(st.session_state.audit_log)+1:04d}",
            "policy_id": policy_id,
            "claim_type": claim_type,
            "claim_amount": claim_amount,
            "admission_days": admission_days,
            "policy_age_days": policy_age_days,
            "provider_id": provider_id,
            "patient_id": patient_id,
            "documents_complete": documents_complete,
            "prior_similar_claim": prior_similar_claim,
        }
        result = process_claim(claim, audit_log=st.session_state.audit_log)
        st.session_state.latest_result = result

    if "latest_result" in st.session_state:
        r = st.session_state.latest_result
        st.divider()
        st.subheader(f"Workflow result — {r['claim_id']}")

        m1, m2, m3 = st.columns(3)
        m1.metric("Recommended payable (₹)", f"₹{r['adjudication']['estimated_payable_inr']:,.0f}")
        m2.metric("Rule-based fraud risk", f"{r['fraud']['risk_score']:.0%}")
        m3.metric("Priority", r["routing"]["priority"])

        st.warning("Human review required. This demo does not approve, reject, or pay claims.")
        st.write("**Recommendation:**", r["adjudication"]["recommendation"])
        st.write("**Routing reasons:**", ", ".join(r["routing"]["reason"]))

        with st.expander("View agent-by-agent trace", expanded=True):
            for step in r["trace"]:
                st.markdown(f"**{step['agent']}** — {step['note']}")
                st.json(step["result"])

# ----------------------------------------------------
# TAB 2: Synthetic Claims
# ----------------------------------------------------
with tab2:
    st.subheader("Provided synthetic sample")
    df = pd.DataFrame(st.session_state.claim_history)
    if df.empty:
        st.info("No sample data available.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download synthetic claims CSV",
            df.to_csv(index=False).encode("utf-8"),
            "synthetic_claims.csv",
            "text/csv",
        )

# ----------------------------------------------------
# TAB 3: Governance & Audit
# ----------------------------------------------------
with tab3:
    st.subheader("Governance controls represented in the demo")
    controls = [
        ("Human-in-the-loop", "Every claim routes to a human reviewer; no automatic rejection or payout."),
        ("Fraud fairness / due process", "Fraud rules generate explainable flags only; no claim is labelled fraudulent."),
        ("Explainability", "Each agent returns a structured result and an audit trace with rule reasons."),
        ("Data minimization", "The bundled sample is synthetic; do not enter real patient identifiers or medical records."),
        ("Deterministic policy checks", "Coverage/waiting-period/limits are coded rules for this demo, not legal policy interpretation."),
        ("Reviewer accountability", "The audit table records run time, claim ID, priority and workflow trace. Reviewer identity/override capture is a future extension."),
        ("Prompt injection / LLM security", "This prototype uses no external LLM or retrieval corpus; these controls must be added and tested before connecting one."),
    ]
    for title, description in controls:
        st.markdown(f"- **{title}:** {description}")

    st.subheader("Run audit log")
    logs = pd.DataFrame(st.session_state.audit_log)
    if logs.empty:
        st.info("No claims have been run in this session.")
    else:
        st.dataframe(logs.drop(columns=["trace"]), use_container_width=True, hide_index=True)
        st.download_button(
            "Download audit log",
            logs.to_csv(index=False).encode("utf-8"),
            "audit_log.csv",
            "text/csv",
        )

# ----------------------------------------------------
# TAB 4: Prototype Notes
# ----------------------------------------------------
with tab4:
    st.subheader("Important scope and limitations")
    st.markdown("""
- This is an **executable academic prototype**, not a production insurance system.
- Agent roles are implemented as sequential Python functions with structured outputs. It is accurately described as a **multi-agent-inspired orchestrated workflow**, not independent autonomous agents.
- The policy terms and watchlist are illustrative and synthetic. They do not represent an insurer's actual policy.
- The fraud score is a transparent heuristic, not a trained fraud model. No performance/accuracy claims should be made without a labelled evaluation dataset.
- No Gemini/Antigravity API is required to run this version. An LLM can be added later for document extraction or grounded policy Q&A, with source citations and safety controls.
- Production readiness would require secure authentication, access control, encryption, real insurer policy integration, validated data, model monitoring, legal/compliance review, incident response, and tested reviewer override.
""")
    st.code("python -m pip install -r requirements.txt\nstreamlit run app.py", language="bash")

# ----------------------------------------------------
# TAB 5: M3 Evaluation
# ----------------------------------------------------
with tab5:
    st.subheader("M3 Prototype Evaluation")
    st.caption(
        "Run the 10 repeatable checks against the current rule-based workflow. "
        "These are software behavior checks, not claims accuracy or fraud-detection performance metrics."
    )

    if "m3_test_results" not in st.session_state:
        st.session_state.m3_test_results = run_predefined_m3_tests()

    if st.button("Run all 10 prototype tests", type="primary"):
        with st.spinner("Executing 10 prototype software behavior checks..."):
            st.session_state.m3_test_results = run_predefined_m3_tests()

    res_df = st.session_state.m3_test_results
    total_tests = len(res_df)
    passed_tests = int((res_df["Status"] == "PASS").sum())
    failed_tests = total_tests - passed_tests

    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.metric("Tests executed", total_tests)
    col_t2.metric("Passed", passed_tests)
    col_t3.metric("Failed", failed_tests)

    st.dataframe(res_df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download observed test results (CSV)",
        res_df.to_csv(index=False).encode("utf-8"),
        "m3_observed_test_results.csv",
        "text/csv",
    )
    st.caption("Use these observed results and summaries in Chapter 4 (built-in prototype behavior tests) for academic assessment records.")
