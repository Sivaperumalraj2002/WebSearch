from bs4 import BeautifulSoup
import requests
from transformers import AutoTokenizer

usefull_tag = ["p","div","li","article","section","h1","h2","h3","h4","h5","h6","td","pre"]

def fetch_html(url, timeout=20):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_elements(html):
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts & styles
    for s in soup(["script","style","noscript","iframe"]):
        s.decompose()
    body = soup.body or soup
    elems = []
    for tag in body.find_all(usefull_tag):
        text = tag.get_text(separator=" ", strip=True)
        if not text:
            continue
        elems.append({"text": text, "html": str(tag)})
    return elems



tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", use_fast=True)

def chunk_elements(elements, max_tokens=500):
    chunks = []
    cur_texts = []
    cur_htmls = []
    cur_token_count = 0

    for el in elements:
        tok_ids = tokenizer.encode(el["text"], add_special_tokens=False)
        tcount = len(tok_ids)
        if tcount > max_tokens:
            # element itself too large
            words = el["text"].split()
            cur = []
            for w in words:
                cur.append(w)
                tok_c = len(tokenizer.encode(" ".join(cur), add_special_tokens=False))
                if tok_c >= max_tokens:
                    txt = " ".join(cur)
                    chunks.append({"text": txt, "html": el["html"]})
                    cur = []
            if cur:
                chunks.append({"text": " ".join(cur), "html": el["html"]})
            continue

        if cur_token_count + tcount <= max_tokens:
            cur_texts.append(el["text"])
            cur_htmls.append(el["html"])
            cur_token_count += tcount
        else:
            # flush
            chunks.append({"text": " ".join(cur_texts), "html": "\n".join(cur_htmls)})
            # start new chunk
            cur_texts = [el["text"]]
            cur_htmls = [el["html"]]
            cur_token_count = tcount

    if cur_texts:
        chunks.append({"text": " ".join(cur_texts), "html": "\n".join(cur_htmls)})

    return chunks
