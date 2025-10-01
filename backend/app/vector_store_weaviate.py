import weaviate
from weaviate.classes.config import Property, DataType, Configure
from sentence_transformers import SentenceTransformer
import numpy as np
import hashlib

# Global client variable
client = None

def get_client():
    # get or create client
    global client
    if client is None or not client.is_ready():
        try:
            client = weaviate.connect_to_local(host="localhost", port=8080)
        except Exception as e:
            raise Exception(f"Failed to connect to Weaviate: {e}")
    return client

def close_client():
    # close client
    global client
    if client is not None:
        try:
            client.close()
        except Exception:
            pass  # Ignore errors when closing
        finally:
            client = None

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
EMBED_DIM = 384

CLASS_NAME = "Chunk"

def ensure_schema():
    # ensure that the Weaviate schema for class Chunk exists.
    client = get_client()
    try:
        if not client.collections.exists(CLASS_NAME):
            client.collections.create(
                CLASS_NAME,
                vectorizer_config=Configure.Vectorizer.none(),  # own vectors
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="html", data_type=DataType.TEXT),
                    Property(name="url", data_type=DataType.TEXT),
                ]
            )
    except Exception as e:
        raise Exception(f"Failed to ensure schema: {e}")

def embed_texts(texts):
    embs = embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embs.astype(np.float32)

def deterministic_id(url, idx):
    # Create stable IDs so we don't duplicate chunks every call.
    import uuid
    h = hashlib.sha256(f"{url}-{idx}".encode()).hexdigest()
    # Convert SHA256 hash to UUID format
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, h))

def upsert_chunks(chunks, url):
    try:
        ensure_schema()
        texts = [c["text"] for c in chunks]
        vectors = embed_texts(texts)
        client = get_client()
        coll = client.collections.get(CLASS_NAME)

        objects = []
        for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
            # Use DataObject for inserting with custom vectors
            from weaviate.classes.data import DataObject
            
            obj = DataObject(
                properties={
                    "text": chunk["text"],
                    "html": chunk["html"],
                    "url": url
                },
                vector=vec.tolist(),
                uuid=deterministic_id(url, i)
            )
            objects.append(obj)

        coll.data.insert_many(objects)
    except Exception as e:
        raise Exception(f"Failed to upsert chunks: {e}")

def search_query(query, top_k=10):
    try:
        ensure_schema()
        qv = embed_texts([query])[0]
        client = get_client()
        coll = client.collections.get(CLASS_NAME)
        results = coll.query.near_vector(
            near_vector=qv.tolist(),
            limit=top_k,
            return_metadata=["distance"],
            return_properties=["text", "html", "url"]
        )
        formatted = []
        for r in results.objects:
            formatted.append({
                "id": r.uuid,
                "score": r.metadata.distance,  # smaller = closer
                "text": r.properties.get("text"),
                "html": r.properties.get("html"),
                "url": r.properties.get("url"),
            })
        return formatted
    except Exception as e:
        raise Exception(f"Failed to search query: {e}")
