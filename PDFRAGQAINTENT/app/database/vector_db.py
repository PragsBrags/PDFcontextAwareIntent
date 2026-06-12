from qdrant_client import QdrantClient
from qdrant_client.http import exceptions
from qdrant_client.http.models import Distance, VectorParams

from app.config import settings

qdrant_client = QdrantClient(
    url=settings.qdrant_url,
)

def init_vector_db(collection_name:str, vector_dim:int)->None:
    try:
        qdrant_client.get_collection(
            collection_name=settings.qdrant_collection,
            )
            
    except (exceptions.UnexpectedResponse, ValueError):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_dim,
                distance=Distance.COSINE
            )
        )

