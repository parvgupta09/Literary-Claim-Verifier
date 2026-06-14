import os
import json
import unicodedata
from collections import Counter
import spacy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned")
CHAR_REG_DIR = os.path.join(BASE_DIR, "char_registry")

os.makedirs(CHAR_REG_DIR, exist_ok=True)

BOOKS = [
    {
        "story_id": "count_of_monte_cristo",
        "input_file": "clean_monte_cristo.txt",
        "output_file": "count_of_monte_cristo.json"
    },
    {
        "story_id": "in_search_of_the_castaways",
        "input_file": "clean_castaways.txt",
        "output_file": "in_search_of_the_castaways.json"
    }
]

TOP_K = 10
CHUNK_SIZE = 10_000
nlp = spacy.load("en_core_web_sm")

STORY_ALIASED_MAPS = {
    "count_of_monte_cristo": {
        "dantes": ["edmond", "dantes", "monte cristo", "the count", "busoni", "wilmore", "sinbad"],
        "faria": ["faria", "abbe", "abbé", "madman"],
        "villefort": ["villefort", "m. de villefort", "procureur"],
        "noirtier": ["noirtier", "m. noirtier", "grandfather"],
        "mercedes": ["mercedes", "countess morcerf"],
        "fernand": ["fernand", "mondego", "morcerf"],
        "danglars": ["danglars", "baron"],
        "caderousse": ["caderousse", "gaspard"],
        "albert": ["albert", "viscount"],
        "maximilian": ["maximilian", "morrel"]
    },
    "in_search_of_the_castaways": {
        "glenarvan": ["glenarvan", "lord edward", "edward"],
        "paganel": ["paganel", "jacques"],
        "mary_grant": ["mary", "miss grant"],
        "robert": ["robert", "robert grant"],
        "john_mangles": ["john", "captain mangles"],
        "ayrton": ["ayrton", "tom"],
        "major_mcnabbs": ["major", "mcnabbs"]
    }
}

def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))

def extract_person_names(text: str):
    names = []
    text_chunks = [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

    for doc in nlp.pipe(text_chunks, batch_size=4, disable=["tagger", "parser", "lemmatizer"]):
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(normalize(ent.text))
    return names

def build_registry(names, story_id, top_k=TOP_K):
    counter = Counter(names)
    
    if story_id in STORY_ALIASED_MAPS:
        print(f"Applying Alias Map for: {story_id}")
        manual_map = STORY_ALIASED_MAPS[story_id]
        registry = {}
        for char_id, aliases in manual_map.items():
            if any(name in counter for name in aliases):
                registry[char_id] = aliases
        return registry

    print(f"No map found for {story_id}. Using Top-{top_k} names.")
    most_common = counter.most_common(top_k)
    return {name.replace(" ", "_"): [name] for name, count in most_common}

def process_book(book):
    input_path = os.path.join(CLEANED_DIR, book["input_file"])
    output_path = os.path.join(CHAR_REG_DIR, book["output_file"])

    if not os.path.exists(input_path):
        print(f"Skipping {book['story_id']}: File not found at {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"\n--- Processing {book['story_id']} ---")
    names = extract_person_names(text)
    registry = build_registry(names, book["story_id"], top_k=TOP_K)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"Success! {len(registry)} characters registered to {output_path}")

def main():
    for book in BOOKS:
        process_book(book)

if __name__ == "__main__":
    main()
