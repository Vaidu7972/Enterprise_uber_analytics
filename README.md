# UberOps AI — Enterprise Agentic Data Intelligence & Support Platform

> **UberOps AI** is an end-to-end Enterprise Data Engineering + Business Intelligence + RAG + Predictive Machine Learning + LangGraph Multi-Agent AI Platform built over a PostgreSQL Gold Data Warehouse.

---

## 🌟 Architecture Overview

```text
                                USER / MANAGER
                                      │
                                      ▼
                               STREAMLIT UI
                                      │
                                      ▼
                          LANGGRAPH SUPERVISOR AGENT
                                      │
                             Intent Classification
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
    GENERAL AI                    DATA AGENT                 SUPPORT AGENT
         │                            │                            │
  Gemini 3.6 Flash                 SQL Tool                   Hybrid RAG Engine
                                      │                            │
                                      ▼                            ▼
                               PostgreSQL Gold                 ChromaDB
                                      │                            │
                                      └─────────────┬──────────────┘
                                                    ▼
                                                 ML AGENT
                                                    │
                                           RandomForest Risk Model
                                                    │
                                                    ▼
                                              INSIGHT ENGINE
                                                    │
                                         RECOMMENDATION ENGINE
                                                    │
                                        HUMAN-IN-THE-LOOP APPROVAL
                                                    │
                                                    ▼
                                      Persisted Audit Log & Reports
```

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Data Engineering** | Python, Pandas, PostgreSQL, SQLAlchemy, psycopg2, Parquet, JSON, XML, Airflow, Docker |
| **GenAI / LLM** | Google Gemini (`google-genai`), System Instructions, Structured Pydantic Outputs |
| **Hybrid RAG** | `pypdf`, Gemini Embeddings (`gemini-embedding-001`), ChromaDB Vector Store, Semantic + Keyword Retrieval |
| **Predictive ML** | `scikit-learn` (RandomForestClassifier), `joblib`, Feature Engineering, Real Warehouse Inference |
| **Multi-Agent Orchestration** | LangGraph, AgentState, Supervisor Routing, Retry/Error Recovery, Human-In-The-Loop Workflow |
| **User Interface** | Streamlit (7-Tab Enterprise Dark Mode Dashboard) |
| **Reporting & Audit** | ReportLab (PDF Export), PostgreSQL Audit Tables (`gold.agent_audit_logs`, `gold.action_logs`) |

---

## 🚀 Key Features

1. **Bronze → Silver → Gold Data Pipeline**: Preserves transactional integrity across customers, drivers, weather, and trips.
2. **Centralized SaaS Theme System (Dark + Light Mode)**: Enterprise visual identity featuring full dark mode and light mode switching. Light mode features off-white backgrounds, white cards, dark readable typography, and styled dataframes, charts, and inputs.
3. **Dynamic Schema Discovery & Entity-Aware SQL Safety**: Data Agent extracts entities (`driver_id`, `customer_id`, location `Pune`, comparison intents) before matching templates, inspecting real PostgreSQL `information_schema.columns` with read-only query safety and a 5000ms query timeout.
4. **Hybrid RAG Support Agent**: Combines semantic vector similarity with keyword matching to answer operational policy questions with exact source attribution.
5. **Non-Leaky Predictive Driver Risk ML Engine**: Refactored machine learning model using Period T (Jan 1–20) historical features to predict future Period T+1 (Jan 21–31) performance deterioration, eliminating target leakage and producing realistic, interview-ready metrics.
6. **LangGraph Multi-Agent Orchestration**: StateGraph coordination across General AI, Data Agent, Support Agent, and ML Agent with automatic fallback and error retries.
7. **Insight & Recommendation Engines**: Computes quantitative variance and formulates actionable business recommendations.
8. **True Human-In-The-Loop Action Approval**: Sensitive operational recommendations (e.g. driver coaching assignment) are registered as `PENDING_APPROVAL` in PostgreSQL. Managers review pending items in the Action Center UI and execute `APPROVE` or `REJECT` workflows.
9. **Differentiated PDF, HTML, & CSV Reports**: Multi-format reporting tailored specifically to Executive Performance, Revenue Analysis, Driver Performance, AI Investigation, and Data Quality requirements.
10. **Multimodal Vehicle Damage Analyzer**: Integrates Gemini Multimodal Vision to inspect vehicle damage photos, cross-referencing Support SOPs with advisory disclaimers.

---

## 💻 Quick Start & Running Instructions

### 1. Prerequisites
- Python 3.12+
- PostgreSQL database running on `localhost:5432` with database `uber_dw`

### 2. Environment Configuration
Ensure `.env` contains:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=uber_dw
DB_USER=postgres
DB_PASSWORD=root
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

### 3. Build RAG Index
```bash
.venv312\Scripts\python.exe -m agentic_ai.rag.build_index
```

### 4. Train Non-Leaky Predictive ML Model
```bash
.venv312\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); from agentic_ai.ml.train_model import train_and_persist_model; train_and_persist_model()"
```

### 5. Run Streamlit Application
```bash
.venv312\Scripts\streamlit.exe run streamlit_app.py
```

### 6. Run Master Automated Tests
```bash
.venv312\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); import unittest; from tests.run_all_tests import TestUberOpsPlatform; suite = unittest.TestLoader().loadTestsFromTestCase(TestUberOpsPlatform); runner = unittest.TextTestRunner(verbosity=2); res = runner.run(suite); sys.exit(0 if res.wasSuccessful() else 1)"
```

---

## ❓ Sample Prompts Across Agents

* **General AI**: `What is ETL in data engineering?`
* **Data Agent**: `What is the rating of driver D101?` | `Show drivers from Pune` | `What is total revenue in the warehouse?` | `Show top 5 drivers by revenue.`
* **Support Agent (RAG)**: `What documents are required for driver onboarding?` | `What should a driver do after an accident?`
* **ML Agent**: `Which drivers are at high risk of underperforming?` | `What is the risk level of driver D101?`
* **Multi-Agent**: `Why is driver D101 underperforming, is this likely to continue, and what training should be recommended?`
