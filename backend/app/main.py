# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .extractor import fetch_html, parse_elements, chunk_elements, tokenizer
from .vector_search import embed_texts, build_faiss_index, search_index, model
import numpy as np

app = FastAPI()

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
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

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/search")
async def search(req: SearchRequest):
    print(req)
    try:
        html = fetch_html(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to fetch url: {e}")

    elements = parse_elements(html)
    chunks = chunk_elements(elements, max_tokens=500)
    texts = [c["text"] for c in chunks]
    if not texts:
        return {"results": []}

    # embeddings
    embeddings = embed_texts(texts)
    index = build_faiss_index(embeddings)

    # query embedding
    q_emb = model.encode([req.query], convert_to_numpy=True)[0].astype("float32")
    D, I = search_index(index, q_emb, k=min(10, len(texts)))

    results = []
    for dist, idx in zip(D, I):
        score = float(dist)   # lower = closer for L2
        results.append({
            "text": texts[idx],
            "html": chunks[idx]["html"],
            "score": score
        })

    # Sort by score ascending (closest first)
    results = sorted(results, key=lambda r: r["score"])
    return {"results": results[:10]}
