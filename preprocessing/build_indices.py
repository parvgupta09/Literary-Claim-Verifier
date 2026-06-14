import os
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOOKS = [
    {
        "input": os.path.join(BASE_DIR, "characters", "monte_cristo_characters_with_metadata.json"),
        "output": os.path.join(BASE_DIR, "indices", "monte_cristo_co_occurrence.json"),
        "story_id": "count_of_monte_cristo"
    },
    {
        "input": os.path.join(BASE_DIR, "characters", "castaways_characters_with_metadata.json"),
        "output": os.path.join(BASE_DIR, "indices", "castaways_co_occurrence.json"),
        "story_id": "in_search_of_the_castaways"
    }
]

os.makedirs(os.path.join(BASE_DIR, "indices"), exist_ok=True)

def build_co_occurrence(chunks):
    co_occurrence = defaultdict(set)

    for chunk in chunks:
        chars = chunk.get("characters_final", [])
        for c in chars:
            for other in chars:
                if c != other:
                    co_occurrence[c].add(other)

    return {k: sorted(v) for k, v in co_occurrence.items()}

def process_book(book):
    print(f"\nBuilding co-occurrence → {book['story_id']}")

    with open(book["input"], "r", encoding="utf-8") as f:
        chunks = json.load(f)

    co_occurrence = build_co_occurrence(chunks)

    with open(book["output"], "w", encoding="utf-8") as f:
        json.dump(co_occurrence, f, indent=2, ensure_ascii=False)

    print(f"Saved → {book['output']}")

def main():
    for book in BOOKS:
        process_book(book)

if __name__ == "__main__":
    main()
