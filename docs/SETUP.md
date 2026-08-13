# UberOps AI Setup & Deployment Guide

## ⚙️ Environment Setup

1. **Activate Virtual Environment**:
   ```bash
   .venv312\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   .venv312\Scripts\pip.exe install -r requirements.txt
   ```

3. **Database Configuration**:
   Ensure PostgreSQL server is running on `localhost:5432` with credentials specified in `.env`.

4. **Build Vector RAG Index**:
   ```bash
   .venv312\Scripts\python.exe -m agentic_ai.rag.build_index
   ```

5. **Train ML Risk Model**:
   ```bash
   .venv312\Scripts\python.exe -m agentic_ai.ml.train_model
   ```

6. **Launch Streamlit Dashboard**:
   ```bash
   .venv312\Scripts\streamlit.exe run streamlit_app.py
   ```

7. **Run Test Suite**:
   ```bash
   .venv312\Scripts\python.exe tests/run_all_tests.py
   ```
