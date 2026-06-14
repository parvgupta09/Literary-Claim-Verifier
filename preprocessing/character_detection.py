import os
import re
import json
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
REGISTRY_DIR = os.path.join(BASE_DIR, "char_registry")
OUTPUT_DIR = os.path.join(BASE_DIR, "characters")

os.makedirs(OUTPUT_DIR, exist_ok=True)

BOOKS = [
    {
        "story_id": "count_of_monte_cristo",
        "chunks_file": "monte_cristo_chunks.json",
        "registry_file": "count_of_monte_cristo.json",
        "output_file": "monte_cristo_characters.json"
    },
    {
        "story_id": "in_search_of_the_castaways",
        "chunks_file": "castaways_chunks.json",
        "registry_file": "in_search_of_the_castaways.json",
        "output_file": "in_search_of_the_castaways_characters.json"
    }
]

HYBRID_WINDOW = 2
PRONOUNS = {"he", "him", "his", "she", "her", "hers"}

def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))

def load_registry(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {
        cid: [normalize(v) for v in variants]
        for cid, variants in raw.items()
    }

def detect_explicit(text, registry):
    found = set()
    norm_text = normalize(text)
    for char_id, variants in registry.items():
        for name in variants:
            pattern = r"\b" + re.escape(name) + r"\b"
            if re.search(pattern, norm_text):
                found.add(char_id)
                break
    return sorted(found)

def should_infer(text):
    words = normalize(text).split()
    return len(words) < 120 and any(p in words for p in PRONOUNS)

def infer_from_context(chunks, idx):
    for i in range(idx - 1, max(idx - HYBRID_WINDOW - 1, -1), -1):
        if chunks[i].get("characters_explicit"):
            return chunks[i]["characters_explicit"]
    for i in range(idx + 1, min(idx + HYBRID_WINDOW + 1, len(chunks))):
        if chunks[i].get("characters_explicit"):
            return chunks[i]["characters_explicit"]
    return []

def process_book(book):
    chunks_path = os.path.join(CHUNKS_DIR, book["chunks_file"])
    registry_path = os.path.join(REGISTRY_DIR, book["registry_file"])
    output_path = os.path.join(OUTPUT_DIR, book["output_file"])

    if not os.path.exists(chunks_path):
        print(f"Skipping {book['story_id']}: {chunks_path} not found.")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    registry = load_registry(registry_path)
    print(f"\nDetecting characters → {book['story_id']}")

    for idx, chunk in enumerate(chunks):
        chunk["characters_explicit"] = detect_explicit(chunk["text"], registry)
        chunk["characters_inferred"] = []

    for idx, chunk in enumerate(chunks):
        if chunk["characters_explicit"]:
            continue
        if should_infer(chunk["text"]):
            chunk["characters_inferred"] = infer_from_context(chunks, idx)

    for chunk in chunks:
        chunk["characters_final"] = sorted(
            set(chunk["characters_explicit"]) |
            set(chunk["characters_inferred"])
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved → {output_path}")

def main():
    for book in BOOKS:
        process_book(book)

if __name__ == "__main__":
    main()
