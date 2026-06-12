import uuid
from typing import List
from qdrant_client.models import PointStruct
from database.vector_db import qdrant_client, init_vector_db
from config import settings

COLLECTION_NAME = settings.qdrant_collection


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
        
    init_vector_db(settings.qdrant_collection, len(embeddings[0]))
    qdrant_client.upsert(collection_name=COLLECTION_NAME, wait=True, points=points)


def search_relevant_chunks(query_embedding: List[float], top_k: int = 5) -> str:
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME, query=query_embedding, limit=top_k
    )

    chunks = [
        point.payload["text"]
        for point in search_result.points
        if point.payload and "text" in point.payload
    ]
    return "\n\n---\n\n".join(chunks)