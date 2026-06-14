import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOOKS = [
    {
        "input": os.path.join(BASE_DIR, "characters", "monte_cristo_characters.json"),
        "output": os.path.join(BASE_DIR, "characters", "monte_cristo_characters_with_metadata.json"),
        "story_id": "count_of_monte_cristo"
    },
    {
        "input": os.path.join(BASE_DIR, "characters", "in_search_of_the_castaways_characters.json"),
        "output": os.path.join(BASE_DIR, "characters", "castaways_characters_with_metadata.json"),
        "story_id": "in_search_of_the_castaways"
    }
]

def detect_imprisonment_phase(text):
    t = text.lower()
    if any(x in t for x in ["château d’if", "chateau d'if", "prison", "cell", "dungeon", "imprisoned"]):
        return "during_imprisonment"
    if any(x in t for x in ["released", "escaped", "after his release"]):
        return "post_imprisonment"
    return "unknown"

def detect_life_state(text):
    t = text.lower()
    if any(x in t for x in ["died", "dead", "corpse", "expired", "his death", "buried"]):
        return "dead"
    return "alive"

def detect_physical_state(text):
    t = text.lower()
    if any(x in t for x in ["paralyzed", "paralysed", "speechless", "unable to move"]):
        return "paralyzed"
    return "active"

def detect_roles(text):
    t = text.lower()
    roles = set()
    if any(x in t for x in ["taught", "instructed", "mentor", "explained"]):
        roles.add("mentor")
    if any(x in t for x in ["political", "bonapartist", "royalist", "conspiracy"]):
        roles.add("political_actor")
    if any(x in t for x in ["prisoner", "cellmate"]):
        roles.add("prisoner")
    return list(roles)

def infer_biography_density(text):
    t = text.lower()
    if any(x in t for x in ["born", "childhood", "grew up", "family", "father", "mother"]):
        return "high"
    if any(x in t for x in ["reputed", "known as", "described as"]):
        return "medium"
    return "low"

def infer_canon_coverage(text):
    t = text.lower()
    return {
        "childhood": "explicit" if any(x in t for x in ["born", "childhood", "youth"]) else "unknown",
        "political_activity": "explicit" if any(x in t for x in ["revolution", "political", "bonapartist", "royalist"]) else "unknown",
        "family_life": "explicit" if any(x in t for x in ["father", "mother", "wife", "son", "daughter"]) else "unknown",
        "foreign_travel": "explicit" if any(x in t for x in ["india", "vienna", "lisbon", "parma"]) else "unknown"
    }

def infer_event_scope(text):
    t = text.lower()
    return {
        "foreign_travel": False if "prison" in t else "unknown",
        "political_action": True if "political" in t else "unknown",
        "violent_action": True if any(x in t for x in ["killed", "murdered", "assassinated"]) else "unknown",
        "secret_societies": "unknown"
    }

def attach_metadata(chunk):
    text = chunk["text"]
    characters = chunk.get("characters_final", [])
    metadata = {}

    for char in characters:
        metadata[char] = {
            "temporal_phase": detect_imprisonment_phase(text),
            "life_state": detect_life_state(text),
            "physical_state": detect_physical_state(text),
            "roles": detect_roles(text),
            "biography_density": infer_biography_density(text),
            "canon_coverage": infer_canon_coverage(text),
            "event_scope": infer_event_scope(text)
        }

    chunk["character_state_metadata"] = metadata
    return chunk

def process_book(book):
    print(f"\nProcessing metadata → {book['story_id']}")

    if not os.path.exists(book["input"]):
        print(f"❌ File not found: {book['input']}")
        return

    with open(book["input"], "r", encoding="utf-8") as f:
        chunks = json.load(f)

    enriched = [attach_metadata(chunk) for chunk in chunks]

    with open(book["output"], "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved → {book['output']}")

def main():
    for book in BOOKS:
        process_book(book)

if __name__ == "__main__":
    main()
