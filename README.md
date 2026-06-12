# PDF RAG QA Intent

Small FastAPI service for PDF/Text retrieval-augmented QA with intent extraction (booking interviews).

## Features
- Upload PDF/TXT files and split them into chunks
- Create embeddings using Ollama
- Store vectors in Qdrant
- Keep simple chat history in Redis
- Use Ollama chat for LLM responses and a simple booking tool integration that writes to SQL DB

## Requirements
- Python 3.10+
- Redis server
- Qdrant server
- Optional SQL DB (SQLite/Postgres/MySQL)
- Ollama running locally or accessible (for embed/chat endpoints)

## Quick setup
1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file in `app/` with these environment variables (example):

```
DATABASE_URL=sqlite:///./db.sqlite3
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=document_chunks
EMBEDDING_MODEL=embeddinggemma
CHAT_MODEL=llama3.1
```

3. Run the API server:

```bash
uvicorn app.app:app --reload --port 8000
```

4. Endpoints
- `POST /upload` - Upload file (form `file`, optional `chunking` and `embedding_model`)
- `POST /query` - Query RAG (form `session_id`, `query`)

## Notes
- The project expects an Ollama service for embedding and chat. Configure `EMBEDDING_MODEL` and `CHAT_MODEL` in `.env`.
- Adjust DB driver in `DATABASE_URL` if using Postgres/MySQL.
- This README is generated from code analysis; review environment variable names in `app/config.py`.
