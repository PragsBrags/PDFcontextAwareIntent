from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from pathlib import Path

from app.config import settings
from app.services.ingestion import load_document, split_document_chunking, embedding_chunks
from app.services.rag import insert_chunks, search_relevant_chunks
from app.database.redis_cache import get_redis_client
from app.database.session import DatabaseConnection
from app.models.documents import Document


app = FastAPI(title="PDF RAG QA Intent")


# minimal database configuration
db_config = {
    "service": False,
    "create_tables": False,
    "echo": False,
    "pool_size": 5,
    "max_overflow": 10,
}

db_conn = DatabaseConnection(db_config)


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking: str = Form("recursive"),
    embedding_model: Optional[str] = Form(None),
):
    # save uploaded file to a temp location
    temp_dir = Path("./tmp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = temp_dir / f"{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        documents = load_document(str(file_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunks = split_document_chunking(documents, chunking)
    model = embedding_model or settings.embedding_model
    embeddings = embedding_chunks(chunks, model)

    # persist chunks to vector DB
    insert_chunks([c.page_content if hasattr(c, "page_content") else str(c) for c in chunks], embeddings, file_id, chunking)

    # store document record in DB if available
    if db_conn.session_factory:
        with db_conn.session() as s:
            doc = Document(file_name=file.filename, file_type=Path(file.filename).suffix, chunking_strategy=chunking)
            s.add(doc)
            s.flush()

    return JSONResponse({"status": "ok", "file_id": file_id})


@app.post("/query")
async def query_rag(session_id: str = Form(...), query: str = Form(...)):
    redis = get_redis_client()
    # get embeddings
    embeddings = embedding_chunks([query], settings.embedding_model)
    # use first embedding
    resp = search_relevant_chunks(embeddings[0])

    # append interaction to chat history
    from app.services.memory import append_to_history

    append_to_history(redis, session_id, query, resp)

    return JSONResponse({"answer": resp})
