# backend/app/vector_search.py
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    # texts: list[str]
    embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embs.astype("float32")

def build_faiss_index(embeddings):
    d = embeddings.shape[1]
    idx = faiss.IndexFlatL2(d)   # simple L2 index
    idx.add(embeddings)
    return idx

def search_index(index, query_vec, k=10):
    # query_vec shape (d,) or (1,d)
    q = np.array([query_vec]).astype("float32")
    D, I = index.search(q, k)
    return D[0], I[0]
