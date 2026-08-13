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
2. **Dynamic Schema Discovery & Read-Only SQL Safety**: Data Agent queries real PostgreSQL `information_schema.columns` and enforces strict read-only query security.
3. **Hybrid RAG Support Agent**: Combines semantic vector similarity with keyword matching to answer operational policy questions with exact source attribution.
4. **Predictive Driver Risk ML Engine**: Real machine learning model predicting driver underperformance risk using driver rating, trip volume, revenue, and trip duration metrics.
5. **LangGraph Multi-Agent Orchestration**: StateGraph coordination across General AI, Data Agent, Support Agent, and ML Agent with automatic fallback and error retries.
6. **Insight & Recommendation Engines**: Computes quantitative variance and formulates actionable business recommendations.
7. **Human-In-The-Loop Action Approval**: Sensitive operational recommendations (e.g. driver coaching assignment) require explicit manager approval before persisting.
8. **Exportable PDF Reports**: One-click generation of formal executive PDF investigation reports.

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

### 4. Train Predictive ML Model
```bash
.venv312\Scripts\python.exe -m agentic_ai.ml.train_model
```

### 5. Run Streamlit Application
```bash
.venv312\Scripts\streamlit.exe run streamlit_app.py
```

### 6. Run Master Automated Tests
```bash
.venv312\Scripts\python.exe tests/run_all_tests.py
```

---

## ❓ Sample Prompts Across Agents

* **General AI**: `What is ETL in data engineering?`
* **Data Agent**: `What is total revenue in the warehouse?` | `Show top 5 drivers by revenue.`
* **Support Agent (RAG)**: `What documents are required for driver onboarding?` | `What should a driver do after an accident?`
* **ML Agent**: `Which drivers are at high risk of underperforming?`
* **Multi-Agent**: `Why is driver D101 underperforming, is this likely to continue, and what training should be recommended?`
