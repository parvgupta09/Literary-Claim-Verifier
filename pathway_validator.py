import json
import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval import retrieve_evidence
from reasoning import check_consistency
from nli_verifier import nli_classify

def load_cooccurrence_indices():
    indices = {}
    possible_base_dirs = [
        "preprocessing/indices",
        "./preprocessing/indices",
        "../preprocessing/indices",
        "indices"
    ]
    
    for base_dir in possible_base_dirs:
        try:
            for book_key in ["monte_cristo", "castaways"]:
                path = f"{base_dir}/{book_key}_co_occurrence.json"
                if os.path.exists(path):
                    with open(path, "r") as f:
                        indices[book_key] = json.load(f)
            
            if len(indices) == 2:
                return indices
        except Exception:
            continue
    
    raise FileNotFoundError(
        "Could not find co-occurrence indices!\n"
        "Expected files:\n"
        "  - preprocessing/indices/monte_cristo_co_occurrence.json\n"
        "  - preprocessing/indices/castaways_co_occurrence.json\n"
        "Please run 6_build_indices.py first!"
    )

CO_OCCURRENCE_CACHE = load_cooccurrence_indices()

def normalize_book_key(book_name):
    b = book_name.lower()
    if "monte" in b:
        return "monte_cristo"
    if "castaway" in b:
        return "castaways"
    raise ValueError(f"Unknown book: {book_name}")

def validate_single_claim(claim_id, book_name, char, content):
    try:
        book_key = normalize_book_key(book_name)
        co_occurrence = CO_OCCURRENCE_CACHE[book_key]
        
        pred_bool, pathway, table, rationale = check_consistency(
            target_character=char,
            claim_text=content,
            co_occurrence_index=co_occurrence,
            book_name=book_name
        )
        
        predicted_label = 1 if pred_bool else 0
        
        return {
            "story_id": claim_id,
            "prediction": predicted_label,
            "rationale": rationale
        }
        
    except Exception as e:
        return {
            "story_id": claim_id,
            "prediction": 0,
            "rationale": f"ERROR: {str(e)}"
        }

def run_pathway_test(input_csv: str, output_csv: str):
    results = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            result = validate_single_claim(
                claim_id=int(row['id']),
                book_name=row['book_name'],
                char=row['char'],
                content=row['content']
            )
            results.append(result)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['story_id', 'prediction', 'rationale'])
        writer.writeheader()
        writer.writerows(results)
    
    print("Predictions complete")

if __name__ == "__main__":
    INPUT_CSV = "test.csv"
    OUTPUT_CSV = "test_results.csv"
    
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found!")
    else:
        run_pathway_test(INPUT_CSV, OUTPUT_CSV)