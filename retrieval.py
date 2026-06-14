import json
import os
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

_BOOK_CACHE = {}

def normalize_book_key(book_name: str) -> str:
    b = book_name.lower()
    if "monte" in b:
        return "monte_cristo"
    if "castaway" in b:
        return "castaways"
    raise ValueError(f"Unknown book_name: {book_name}")

def load_book_chunks(book_name):
    book_key = normalize_book_key(book_name)

    if book_key in _BOOK_CACHE:
        return _BOOK_CACHE[book_key]

    char_path = os.path.join(
        BASE_DIR,
        "preprocessing",
        "characters",
        f"{book_key}_characters_with_metadata.json"
    )

    with open(char_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]
    embs = embedder.encode(texts, convert_to_tensor=True)

    _BOOK_CACHE[book_key] = (chunks, embs)
    return chunks, embs

def retrieve_evidence(
    target_character,
    claim_text,
    co_occurrence_index,
    book_name,
    top_k=6
):
    ALL_CHUNKS, ALL_EMBS = load_book_chunks(book_name)

    target_id = target_character.lower().strip().replace(" ", "_")

    candidates, indices = [], []
    for i, c in enumerate(ALL_CHUNKS):
        if target_id in c.get("characters_final", []):
            candidates.append(c)
            indices.append(i)

    if not candidates:
        return []

    claim_emb = embedder.encode(claim_text, convert_to_tensor=True)
    sims = util.cos_sim(claim_emb, ALL_EMBS[indices])[0].tolist()

    scored = []
    co_chars = set(co_occurrence_index.get(target_id, []))

    for c, sim in zip(candidates, sims):
        score = sim
        if sim > 0.20:
            if target_id in c.get("characters_explicit", []):
                score += 0.25
            score += 0.04 * len(co_chars.intersection(set(c.get("characters_final", []))))
        scored.append((c, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, s in scored if s > 0.25][:top_k]
