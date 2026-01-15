import os
import re

def clean_line(line):
    # 1. Strip leading/trailing whitespace
    line = line.strip()

    # 2. Convert to string if not already (just in case)
    if not line:
        return None

    # 3. Handle Parentheses: ( Name ) -> Name
    # If the line is wrapped in parens, take inside.
    if line.startswith('(') and line.endswith(')'):
        line = line[1:-1].strip()

    # Handle unclosed parentheses like "( RAF" or "( PKK"
    if '(' in line:
        line = line.split('(')[0].strip()

    # 4. Strip suffixes starting with apostrophe or curly quotes
    # This covers: 'nin, 'de, 'den, 'li, 's, etc.
    line = re.split(r"['’‘]", line)[0]

    # 5. Remove specific noise patterns (quotes, redundant punctuation)
    line = re.sub(r'["“”]', '', line)

    # 6. Remove leading/trailing excessive punctuation
    # e.g., ", Bağdat", "/Beyoğlu", "''Billboard"
    line = re.sub(r"^[\W_]+", "", line)

    # 7. Remove trailing noise punctuation (but keep dots for abbr like A.B.D)
    line = line.rstrip("-,/\\.")

    line = line.strip()

    # 8. Validation / Filtering Logic

    # Too short? (e.g. 1 char).
    # Exception: "O" is valid in some contexts but questionable for locations/people in this dataset context.
    # Let's say min 2 chars.
    if len(line) < 2:
        return None

    # Is it just numbers? (e.g. "2012" or "19-20")
    if line.replace(".", "").replace("-", "").isdigit():
        return None

    # Is it a date range? (e.g. "1969-70")
    if re.search(r'\d{4}', line):
        return None

    # Filter URLs/Filenames
    if re.search(r'\.(com|net|org|fm|tv|jpg|png|gov|edu)$', line, re.IGNORECASE):
        return None

    # [NEW] Filter entities starting with lowercase (mostly noise like 'adını', 'olarak')
    if line[0].islower():
        return None


    # Is it likely garbage? (e.g. "'' ''")
    if not any(c.isalpha() for c in line):
        return None

    return line

def clean_file(filepath):
    if not os.path.exists(filepath):
        return

    print(f"Cleaning {filepath}...")

    unique_entries = set()
    trash_count = 0
    original_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            original_count += 1
            cleaned = clean_line(line)
            if cleaned:
                unique_entries.add(cleaned)
            else:
                trash_count += 1

    # Sort for readability
    sorted_entries = sorted(list(unique_entries))

    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in sorted_entries:
            f.write(entry + "\n")

    print(f"  - Original lines: {original_count}")
    print(f"  - Final Unique Entries: {len(sorted_entries)}")
    print(f"  - Removed (Trash/Empty/Duplicates): {original_count - len(sorted_entries)}")

def main():
    gaz_dir = "gazetteers"
    files = [
        "film_muzik.txt",
        "kisiler.txt",
        "kurumlar.txt",
        "sirketler.txt",
        "topluluklar.txt",
        "yerler.txt"
    ]

    for filename in files:
        clean_file(os.path.join(gaz_dir, filename))

    print("\nAll gazetteers cleaned.")

if __name__ == "__main__":
    main()
