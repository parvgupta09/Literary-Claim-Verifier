# Literary Claim Verification — NLI & Semantic Search

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-orange)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An NLP pipeline that verifies whether character-level claims about long-form literary texts are **consistent or contradictory** with the source material — combining semantic retrieval, heuristic reasoning, and natural language inference.

---

## 📖 Overview

This system checks the factual and logical validity of claims about characters in classic novels. Given a claim like *"Edmond Dantès was imprisoned in the Château d'If"*, the pipeline retrieves relevant passages from the novel, applies character-state heuristics, and uses BART-MNLI to classify the claim as **consistent** or **contradictory**.

**Target Books:**
- *The Count of Monte Cristo*
- *In Search of the Castaways*

---

## 🏗️ Pipeline Architecture

```
Raw Novel Text
      │
      ▼
Text Cleaning & Preprocessing
      │
      ▼
Paragraph Chunking (chunk_id, story_id, position)
      │
      ▼
Character Registry (spaCy NER + alias normalization)
      │
      ▼
Character Detection per Chunk (explicit + inferred mentions)
      │
      ▼
Paragraph Metadata (life state, imprisonment phase, roles, etc.)
      │
      ▼
Co-occurrence Index (character adjacency graph)
      │
      ▼
Retrieval (Sentence-BERT semantic search → top evidence chunks)
      │
      ▼
Reasoning (heuristics + BART-MNLI NLI scoring)
      │
      ▼
Prediction + Human-readable Rationale
```

---

## 📂 Project Structure

```
├── preprocessing/
│   ├── text_cleaning.py           # Strips Gutenberg boilerplate, chapter markers, noise
│   ├── paragraph_chunking.py      # Splits cleaned text into paragraph chunks
│   ├── character_registery.py     # Builds canonical character registry with alias maps
│   ├── character_detection.py     # Labels chunks with explicit/inferred character mentions
│   ├── paragraph_metadata.py      # Attaches heuristic state metadata per chunk per character
│   ├── build_indices.py           # Builds character co-occurrence adjacency graphs
│   ├── cleaned/                   # Cleaned book text files
│   ├── chunks/                    # Paragraph-level JSON chunks
│   ├── char_registry/             # Canonical character/alias maps
│   ├── characters/                # Character annotations per chunk
│   └── indices/                   # Co-occurrence graphs
├── nli_verifier.py                # Loads BART-MNLI, returns entailment/contradiction scores
├── retrieval.py                   # Semantic retrieval of relevant evidence chunks
├── reasoning.py                   # Decision engine combining heuristics + NLI
├── pathway_validator.py           # Batch runner — reads test.csv, writes test_results.csv
├── train.csv                      # Labeled claim set (80 rows)
├── test.csv                       # Unlabeled claim set (60 rows)
├── test_results.csv               # System predictions with rationales
└── test_results.xlsx              # Spreadsheet version of predictions
```

---

## 🛠️ Tech Stack

| Component | Tool |
|---|---|
| Named Entity Recognition | spaCy (`en_core_web_sm`) |
| Semantic Retrieval | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Natural Language Inference | BART-MNLI (`facebook/bart-large-mnli`) |
| Deep Learning Backend | PyTorch |
| Model Loading | Hugging Face Transformers |

---

## 📊 Dataset

| Split | Total Claims | In Search of the Castaways | Count of Monte Cristo |
|---|---|---|---|
| Train (labeled) | 80 | 49 | 31 |
| Test (unlabeled) | 60 | 37 | 23 |

**Label distribution (train):** 51 consistent / 29 contradictory

**Corpus scale:**
- Monte Cristo: 14,412 paragraph chunks, 10 canonical characters
- Castaways: 4,062 paragraph chunks, 6 canonical characters

---

## ⚙️ How To Run Locally

### 1. Install Dependencies

```bash
pip install torch transformers sentence-transformers spacy
python -m spacy download en_core_web_sm
```

> Note: First run will automatically download BART-MNLI and Sentence-BERT weights from Hugging Face.

### 2. Add Source Texts

Place the raw novel files in the repo root:
```
The Count of Monte Cristo.txt
In search of the castaways.txt
```

### 3. Run Preprocessing (in order)

```bash
python preprocessing/text_cleaning.py
python preprocessing/paragraph_chunking.py
python preprocessing/character_registery.py
python preprocessing/character_detection.py
python preprocessing/paragraph_metadata.py
python preprocessing/build_indices.py
```

### 4. Run Claim Verification

```bash
python pathway_validator.py
```

Output is saved to `test_results.csv` and `test_results.xlsx`.

---

## 📝 Output Format

Each prediction in `test_results.csv` contains:

| Column | Description |
|---|---|
| `story_id` | Book identifier |
| `prediction` | 1 = consistent, 0 = contradictory |
| `rationale` | Human-readable explanation of the decision |

---

## 🔍 How Reasoning Works

The `reasoning.py` decision engine combines three signals:

1. **Character-state heuristics** — checks if retrieved evidence marks the character as dead, paralyzed, or imprisoned
2. **Claim classification** — categorizes the claim as interpretive, concrete, or specific
3. **BART-MNLI NLI scoring** — counts entailment vs contradiction votes across top evidence chunks

A structured pathway trace is also returned alongside each decision for interpretability.

---

## ⚠️ Limitations

- Scripts use hard-coded relative paths — run order matters
- No `requirements.txt` yet (dependencies must be installed manually)
- Test set has no ground-truth labels, so held-out accuracy cannot be computed from this repo alone
- 31 out of 60 test predictions fell back to a *"no textual evidence found"* rationale, indicating retrieval gaps for some claims

---

## 📄 License

This project is licensed under the MIT License.

---

**Disclaimer:** This tool is built for literary analysis purposes only and is not intended for any form of automated fact-checking outside of fictional/literary contexts.
