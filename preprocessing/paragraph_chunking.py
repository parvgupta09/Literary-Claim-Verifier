import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned")
CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
os.makedirs(CHUNKS_DIR, exist_ok=True)

BOOKS = [
    {
        "story_id": "count_of_monte_cristo",
        "input_file": "clean_monte_cristo.txt",
        "output_file": "monte_cristo_chunks.json"
    },
    {
        "story_id": "in_search_of_the_castaways",
        "input_file": "clean_castaways.txt",
        "output_file": "castaways_chunks.json"
    }
]

def split_paragraphs(text: str):
    lines = text.splitlines()
    paragraphs = []
    buffer = []

    for line in lines:
        if re.match(r"^\s*\d+[a-zA-Z]?\s*$", line):
            continue

        if line.strip() == "":
            if buffer:
                paragraphs.append(" ".join(buffer).strip())
                buffer = []
        else:
            buffer.append(line.strip())

    if buffer:
        paragraphs.append(" ".join(buffer).strip())

    return paragraphs

def chunk_book(book):
    story_id = book["story_id"]
    input_path = os.path.join(CLEANED_DIR, book["input_file"])
    output_path = os.path.join(CHUNKS_DIR, book["output_file"])

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing cleaned file: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    paragraphs = split_paragraphs(text)

    chunks = []
    for idx, para in enumerate(paragraphs, start=1):
        chunks.append({
            "chunk_id": f"{story_id}_p{idx}",
            "story_id": story_id,
            "global_position": idx,
            "text": para
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"{story_id}: {len(chunks)} chunks written → {output_path}")

def main():
    for book in BOOKS:
        chunk_book(book)

if __name__ == "__main__":
    main()
