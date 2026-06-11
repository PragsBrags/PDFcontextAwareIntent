from qdrant_client import QdrantClient
from qdrant_client.http import exceptions
from qdrant_client.http.models import Distance, VectorParams

qdrant_client = QdrantClient(
    url=URL_QDRANT,
)

def init_vector_db(collection_name:str, vector_dim:int)->None:
    try:
        qdrant_client.get_collection(
            collection_name=collection_name,
            )
            
    except (exceptions.UnexpectedResponse, ValueError):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_dim,
                distance=Distance.COSINE
            )
        )

