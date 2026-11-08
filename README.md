# Insurance Claiming Process Agents

> **Academic Prototype (Module M3)**  
> *Agentic AI for Health Insurance Claims Processing at a Mid-Size Indian Insurer*  
> *Executable Streamlit Prototype • Synthetic Data Only • Human-in-the-Loop Decision Support*

---

## 📌 Project Overview

Health insurance claims processing in India is document-intensive, time-sensitive, and tightly regulated. Under IRDAI guidelines, insurers must decide cashless authorization requests within 1 hour and final discharge authorizations within 3 hours, while actively preventing fraud, waste, and abuse.

This project implements an **orchestrated multi-agent claims workflow** as a lightweight local Python application using **Streamlit**. The system assists claims operations by performing automated intake validation, deterministic policy coverage checks, heuristic fraud screening, and adjudication calculations—while strictly routing every claim to an accountable human reviewer.

---

## 🤖 Specialized Agent Roles

The system is structured into five specialized agent roles that mimic real insurer processing desks:

1. **Intake Agent (`Intake Agent`)**: Validates mandatory claim fields (claim ID, policy, amounts, dates, IDs) and verifies that all required claim documents are marked present.
2. **Policy Agent (`Policy Agent`)**: Evaluates policy terms, checks waiting-period compliance (e.g., 30 days for POL-100, 90 days for POL-300), validates covered treatment categories, and computes room-rent sub-limits.
3. **Fraud Screening Agent (`Fraud Screening Agent`)**: Screens claims against explainable risk indicators (claims $\ge$ ₹2,00,000, stays $\ge$ 10 days, synthetic watchlisted provider IDs, and prior similar claims). Generates transparent risk flags without declaring fraud.
4. **Adjudication Agent (`Adjudication Agent`)**: Computes the recommended payable estimate by applying eligible limits and plan deductibles, recommending either *"Potentially payable"* or *"Not eligible under configured rules"*.
5. **Supervisor Agent (`Supervisor Agent`)**: Enforces risk-tiered human-in-the-loop governance. Sets case priority (High vs. Standard) and ensures **zero autonomous rejections or payouts** by routing 100% of claims to human officers.

---

## 🖥️ Application Features (5 Interactive Tabs)

The Streamlit interface provides five comprehensive workbench tabs:

* **Tab 1: Claims Workbench**: Submit new claims or select synthetic test claims, run the agent workflow, inspect metric cards (Recommended payable, Rule-based fraud risk, Priority), and view the full step-by-step agent execution trace.
* **Tab 2: Synthetic Claims**: Browse the full synthetic dataset of 40 fictitious claims and export them to a CSV file.
* **Tab 3: Governance & Audit**: Review governance controls (human-in-the-loop, due process, data minimization, explainability) and inspect or download the session audit log.
* **Tab 4: Prototype Notes**: Outlines academic scope, limitations, technology choices, and future production milestones.
* **Tab 5: M3 Evaluation**: Interactive evaluation screen that runs the 10 repeatable software behavior tests (T01 to T10) described in Chapter 4, displaying summary cards (10 Executed, 10 Passed, 0 Failed), full behavior comparisons, and CSV export.

---

## 📁 Repository Structure

```text
insurance_claims_agent_demo/
├── .gitignore               # Excludes virtual environments, caches, and backups
├── README.md                # Project documentation and setup guide
├── requirements.txt         # Minimal Python dependencies (streamlit, pandas)
├── app.py                   # Main Streamlit web application (5 tabs)
├── test_stage1.py           # Automated command-line test runner (10/10 PASS)
├── data/
│   ├── synthetic_claims.csv # 40 fictitious claim records for demonstration
│   ├── test_cases.csv       # 10 predefined test scenario definitions
│   └── policy_reference.md  # Synthetic policy terms (POL-100, POL-200, POL-300)
└── src/
    ├── __init__.py          # Package initialization
    ├── policies.py          # Policy plan definitions and limits
    ├── rules.py             # Deterministic business logic for all agent roles
    ├── agents.py            # Individual agent stage runners and trace notes
    └── workflow.py          # 5-stage sequential workflow orchestrator
```

---

## 🚀 Quick Start & Setup Instructions

### Prerequisites
* Python 3.10 or higher installed on your computer.

### 1. Clone or Download the Repository
Open your terminal (PowerShell, CMD, or bash) and navigate to the project directory:
```bash
cd insurance_claims_agent_demo
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages using the clean `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
Launch the local web dashboard:
```bash
python -m streamlit run app.py
```
Streamlit will automatically open the application in your default web browser at `http://localhost:8501`.

---

## 🧪 Running the Verification Test Suite

To verify system behavior against the 10 predefined test scenarios without opening the browser, run:

```bash
python test_stage1.py
```

### Expected Output:
```text
==================================================
Running Stage 1 Verification Suite
==================================================
 [PASS] T01: Covered low-value claim
 [PASS] T02: Waiting period not met
 [PASS] T03: Unsupported benefit category
 [PASS] T04: High-value claim priority
 [PASS] T05: Watchlisted synthetic provider
 [PASS] T06: Incomplete documents
 [PASS] T07: Long admission risk indicator
 [PASS] T08: Unknown policy handled safely
 [PASS] T09: Prior similar claim flag
 [PASS] T10: Clean claim routed to standard human review
==================================================
Results: 10/10 tests passed successfully!
Stage 1 modular refactoring verified!
==================================================
```

---

## 🛡️ Governance & Scope Limitations

* **Synthetic Data Only**: All patient IDs, provider IDs, policy details, and amounts are entirely fictional. No real customer personal data (DPDP Act 2023) or insurer confidential records are used.
* **Deterministic Rules (M3 Scope)**: The current workflow is implemented in deterministic Python functions. It does not require external LLM calls or cloud API keys.
* **Decision Support Only**: The system acts strictly as an advisory assistant. It displays clear notices that it cannot issue binding claim rejections or approve payments autonomously; full decision accountability remains with human claims officers.
* **Future Production Roadmap**: Full production deployment would require core claim system integration (e.g., NHCX), OCR for scanned hospital invoices, policy vector retrieval (RAG), and reviewer authentication.
