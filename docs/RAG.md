# Hybrid RAG System Documentation

## 📚 RAG Pipeline Overview

1. **Support Documents (`data/support_docs/`)**:
   - `cancellation_policy.txt`
   - `driver_onboarding_policy.txt`
   - `incident_response_sop.txt`
   - `driver_performance_policy.txt`
   - `customer_support_faq.txt`
   - `training_policy.txt`

2. **Document Loading & Chunking (`document_loader.py`, `chunker.py`)**:
   - Supports `.txt` and `.pdf` files via `pypdf`.
   - Text chunking (chunk size 220 words, overlap 40 words).
   - Preserves source file name, page number, and chunk index metadata.

3. **Gemini Embeddings & ChromaDB (`embedding_service.py`, `vector_store.py`)**:
   - Generates 768-dimensional embeddings using `gemini-embedding-001`.
   - Persists vector collection `uberops_support_docs` in `vector_store/chroma_db/`.

4. **Hybrid Retrieval Algorithm (`vector_store.py`)**:
   - Candidates retrieved via vector cosine similarity search (`0.7` weight).
   - Candidate documents ranked with keyword match overlap (`0.3` weight).
   - Top `k` chunks returned with distance scores and source attribution.
