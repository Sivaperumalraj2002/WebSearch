# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .extractor import fetch_html, parse_elements, chunk_elements, tokenizer
from .vector_search import embed_texts, build_faiss_index, search_index, model
import numpy as np

from .vector_store_weaviate import upsert_chunks, search_query

app = FastAPI()

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    url: str
    query: str

# search with Weaviate
@app.post("/searchWeaviate")
async def search_weaviate(req: SearchRequest):
    try:
        html = fetch_html(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    try:
        elements = parse_elements(html)
        chunks = chunk_elements(elements, max_tokens=500)
        if not chunks:
            return {"results": []}

        # Index into Weaviate
        upsert_chunks(chunks, req.url)

        # Semantic search
        hits = search_query(req.query, top_k=10)

        return {"results": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weaviate operation failed: {e}")

# health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# search with FAISS
@app.post("/searchFAISS")
async def search_faiss(req: SearchRequest):
    print(req)
    try:
        html = fetch_html(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to fetch url: {e}")

    elements = parse_elements(html)
    chunks = chunk_elements(elements, max_tokens=500)
    # print(chunks)
    texts = [c["text"] for c in chunks]
    if not texts:
        return {"results": []}

    # embeddings
    embeddings = embed_texts(texts)
    # print(len(embeddings[0]))
    index = build_faiss_index(embeddings)

    # query embedding
    q_emb = model.encode([req.query], convert_to_numpy=True)[0].astype("float32")
    D, I = search_index(index, q_emb, k=min(10, len(texts)))

    results = []
    for dist, idx in zip(D, I):
        # lower value loser for L2
        score = float(dist)   
        results.append({
            "text": texts[idx],
            "html": chunks[idx]["html"],
            "score": score
        })

    results = sorted(results, key=lambda r: r["score"])
    return {"results": results[:10]}
