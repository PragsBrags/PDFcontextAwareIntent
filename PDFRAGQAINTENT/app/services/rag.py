import uuid

from qdrant_client.models import PointStruct
from database.vector_db import qdrant_client

COLLECTION_NAME = 'chunking'

async def insert_chunks(
    chunks: List[str],
    embeddings: List[List[float]],
    document_id: str,
    strategy_name: str,
) -> None:
    points = []

    for id, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        payload = {
            "doc_id": document_id,
            "chunk": chunk,
            "strategy": strategy_name,
            "index": id,
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload
            )
        )
    
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=points
    )

async def search_relevant_chunks(
    query_embedding: List[float],
    top_k: int = 5
) -> str :

    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )

    relevant_chunks = [hit.payload["text"] for hit in search_result if hit.payload and "text" in hit.payload]

    return "\n\n---\n\n".joinrelevant_chunks