import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

BOOK1_INPUT = os.path.join(os.path.dirname(BASE_DIR), "The Count of Monte Cristo.txt")
BOOK1_OUTPUT = os.path.join(CLEANED_DIR, "clean_monte_cristo.txt")

BOOK1_START = "VOLUME ONE"
BOOK1_END = "*** END OF THE PROJECT GUTENBERG EBOOK THE COUNT OF MONTE CRISTO ***"

def remove_contents_block(text: str):
    return re.sub(
        r"CONTENTS\.?.*?\n\s*\n",
        "\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
        count=1
    )

def clean_monte_cristo():
    with open(BOOK1_INPUT, "r", encoding="utf-8") as f:
        text = f.read()

    text = remove_contents_block(text)

    start_idx = text.find(BOOK1_START)
    end_idx = text.find(BOOK1_END)

    if start_idx == -1 or end_idx == -1:
        raise ValueError("Monte Cristo start/end marker missing")

    text = text[start_idx:end_idx]
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if re.match(r"^\d+[a-zA-Z]?$", line):
            continue

        if re.match(r"^VOLUME\s+(ONE|TWO|THREE|FOUR|FIVE|[IVXLCDM]+)$", line, re.IGNORECASE):
            continue

        if re.match(r"^Chapter\s+\d+\.\s+.+", line):
            continue

        lines.append(line)

    with open(BOOK1_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Monte Cristo cleaning complete.")

BOOK2_INPUT = os.path.join(os.path.dirname(BASE_DIR), "In search of the castaways.txt")
BOOK2_OUTPUT = os.path.join(CLEANED_DIR, "clean_castaways.txt")

BOOK2_START = "IN SEARCH OF THE CASTAWAYS."
BOOK2_END = "*** END OF THE PROJECT GUTENBERG EBOOK 46597 ***"

CASTAWAYS_CHAPTER_TITLES = {
    "THE SHARK.",
    "THE THREE DOCUMENTS.",
    "THE CAPTAIN'S CHILDREN.",
    "LADY GLENARVAN'S PROPOSAL.",
    "THE DEPARTURE OF THE DUNCAN.",
    "AN UNEXPECTED PASSENGER.",
    "JACQUES PAGANEL IS UNDECEIVED.",
    "THE GEOGRAPHER'S RESOLUTION.",
    "THROUGH THE STRAIT OF MAGELLAN.",
    "THE COURSE DECIDED.",
    "TRAVELING IN CHILI.",
    "ELEVEN THOUSAND FEET ALOFT.",
    "A SUDDEN DESCENT.",
    "PROVIDENTIALLY RESCUED.",
    "THALCAVE.",
    "NEWS OF THE LOST CAPTAIN.",
    "A SERIOUS NECESSITY.",
    "IN SEARCH OF WATER.",
    "THE RED WOLVES.",
    "STRANGE SIGNS.",
    "A FALSE TRAIL.",
    "THE FLOOD.",
    "A SINGULAR ABODE.",
    "PAGANEL'S DISCLOSURE.",
    "BETWEEN FIRE AND WATER.",
    "THE RETURN ON BOARD.",
    "A NEW DESTINATION.",
    "TRISTAN D'ACUNHA AND THE ISLE OF AMSTERDAM.",
    "THE STORM ON THE INDIAN OCEAN.",
    "A HOSPITABLE COLONIST.",
    "THE QUARTERMASTER OF THE BRITANNIA.",
    "PREPARATIONS FOR THE JOURNEY.",
    "AN ACCIDENT.",
    "AUSTRALIAN EXPLORERS.",
    "CRIME OR CALAMITY?",
    "FRESH FACES.",
    "A WARNING.",
    "WEALTH IN THE WILDERNESS.",
    "SUSPICIOUS OCCURRENCES.",
    "A STARTLING DISCOVERY.",
    "THE PLOT UNVEILED.",
    "FOUR DAYS OF ANGUISH.",
    "HELPLESS AND HOPELESS.",
    "A ROUGH CAPTAIN.",
    "THE WRECK OF THE MACQUARIE.",
    "VAIN EFFORTS.",
    "A DREADED COUNTRY.",
    "INTRODUCTION TO THE CANNIBALS.",
    "A MOMENTOUS INTERVIEW.",
    "THE CHIEF'S FUNERAL.",
    "STRANGELY LIBERATED.",
    "THE SACRED MOUNTAIN.",
    "A BOLD STRATAGEM.",
    "FROM PERIL TO SAFETY.",
    "WHY THE DUNCAN WENT TO NEW ZEALAND.",
    "AYRTON'S OBSTINACY.",
    "A DISCOURAGING CONFESSION.",
    "A CRY IN THE NIGHT.",
    "CAPTAIN GRANT'S STORY.",
    "PAGANEL'S LAST ENTANGLEMENT."
}

def clean_castaways():
    with open(BOOK2_INPUT, "r", encoding="utf-8") as f:
        text = f.read()

    text = remove_contents_block(text)

    start_idx = text.find(BOOK2_START)
    end_idx = text.find(BOOK2_END)

    if start_idx == -1 or end_idx == -1:
        raise ValueError("Castaways start/end marker missing")

    text = text[start_idx:end_idx]
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if re.match(r"^\d+[a-zA-Z]?$", line):
            continue

        if re.match(r"^\[Illustration\]$", line):
            continue

        if re.match(r"^\[Sidenote:.*\]$", line):
            continue

        if re.match(r"^CHAPTER\s+[IVXLCDM]+\.$", line):
            continue

        if line.upper() in CASTAWAYS_CHAPTER_TITLES:
            continue

        lines.append(line)

    with open(BOOK2_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Castaways cleaning complete.")

def main():
    clean_monte_cristo()
    clean_castaways()

if __name__ == "__main__":
    main()
