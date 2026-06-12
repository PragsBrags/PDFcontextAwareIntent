import uuid
from typing import List
from qdrant_client.models import PointStruct
from app.database.vector_db import qdrant_client


COLLECTION_NAME = "chunking"


def insert_chunks(
    chunks: List[str],
    embeddings: List[List[float]],
    document_id: str,
    strategy_name: str,
) -> None:
    points: List[PointStruct] = []

    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        payload = {
            "doc_id": document_id,
            "text": chunk,
            "strategy": strategy_name,
            "index": idx,
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload,
            )
        )

    qdrant_client.upsert(collection_name=COLLECTION_NAME, wait=True, points=points)


def search_relevant_chunks(query_embedding: List[float], top_k: int = 5) -> str:
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME, query_vector=query_embedding, limit=top_k
    )

    chunks = [hit.payload["text"] for hit in search_result if hit.payload and "text" in hit.payload]
    return "\n\n---\n\n".join(chunks)