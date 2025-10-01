# Website DOM Search (SPA + FastAPI + FAISS + Weaviate)

## Overview
This project is a **single-page application (SPA)** that allows users to:
- Enter a **website URL** and a **search query**.
- Extract and clean the HTML content of the given page.
- Split the content into **500-token chunks**.
- Index the chunks in a **vector database** (FAISS or Weaviate).
- Perform **semantic search** to return the top 10 most relevant chunks.

## Tech Stack
- **Frontend**: React (Vite), Axios
- **Backend**: FastAPI (Python)
- **HTML Parsing**: BeautifulSoup
- **Tokenization & Embeddings**: Hugging Face `sentence-transformers`
- **Vector DBs**:
  - **FAISS** (local in-memory, no Docker required)
  - **Weaviate** (via Docker, REST API)
  
project-root/
├── .gitignore
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── extractor.py         # HTML parsing + chunking
│   │   ├── vector_search.py     # FAISS search
│   │   └── vector_store_weaviate.py  # Weaviate integration
│   ├── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── components/
├── docker-compose.yml           # Weaviate setup
└── slides/
    ├── Fullstack Developer - Async test(3 hrs).docx
    └── slides.pdf




## Setup Instructions

### 1. Clone repo & install dependencies
```bash
git clone <repo-url>
cd project-root

## Backend Process

### Virual Environment
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt 
uvicorn app.main:app --reload --port 8000 -> To run the server

### Endpoints available:

POST /searchFAISS → search using local FAISS
POST /searchWeaviate → search using Weaviate

## Frontent Setup
cd frontend
npm install
npm run dev

Open app in browser → http://localhost:5173 or http://localhost:5174

## Weaviate setup (Docker)
First install the Docker Desktop in local machine.
```bash
docker-compose up -d 

## API Usage
```bash
curl -X POST "http://localhost:8000/searchFAISS" \
 -H "Content-Type: application/json" \
 -d '{"url":"https://example.com", "query":"example"}'

### Response Format.
{
  "results": [
    {
      "id": "chunk-id",
      "score": 0.123,
      "text": "Extracted text snippet...",
      "html": "<p>Extracted HTML...</p>",
      "url": "https://example.com"
    }
  ]
}




