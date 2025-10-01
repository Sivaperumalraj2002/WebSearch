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
  
## Project Structure
project-root/ \n
├─ venv (Virtual Environment Python 3.12.10. But, it is not included in git repository.) \n
├─ backend/ \n
│ ├─ app/ \n
│ │ ├─ main.py # FastAPI endpoints \n
│ │ ├─ extractor.py # HTML parsing + chunking \n
│ │ ├─ vector_search.py # FAISS search \n
│ │ ├─ vector_store_weaviate.py # Weaviate integration \n
│ ├─ requirements.txt \n
├─ frontend/ (React Vite app) \n
├─ docker-compose.yml (Weaviate setup) \n
├─ slides \n
  ├─ Fullstack Developer - Async test(3 hrs) .docx \n
  ├─ slides.pdf \n



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




