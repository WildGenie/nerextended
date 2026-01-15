import os
import zipfile
import re
from collections import defaultdict

# Reuse cleaning logic (simplified duplication to avoid import issues or circular deps)
def clean_line(line):
    line = line.strip()
    if not line: return None
    if line.startswith('(') and line.endswith(')'): line = line[1:-1].strip()
    if '(' in line: line = line.split('(')[0].strip()
    line = re.split(r"['’‘]", line)[0]
    line = re.sub(r'["“”]', '', line)
    line = re.sub(r"^[\W_]+", "", line)
    line = line.rstrip("-,/\\.")
    line = line.strip()
    if len(line) < 2: return None
    if line.replace(".", "").replace("-", "").isdigit(): return None
    if re.search(r'\d{4}', line): return None
    if re.search(r'\.(com|net|org|fm|tv|jpg|png|gov|edu)$', line, re.IGNORECASE): return None
    if not any(c.isalpha() for c in line): return None
    return line

# Tag Mappings
TAG_MAPPING = {
    "kisiler.txt": ["person", "actor", "director", "inventor", "artist", "athlete", "author", "politician", "character"],
    "yerler.txt": ["location", "city", "province", "country", "island", "mountain", "river", "capital", "place"],
    "kurumlar.txt": ["organization", "institution", "university", "school", "museum", "hospital", "party", "league"],
    "sirketler.txt": ["company", "business", "corporation", "developer", "manufacturer"],
    "film_muzik.txt": ["film", "movie", "cinema", "music", "song", "album", "band", "musical", "software", "operating_system", "tv_program", "broadcast"],
    "topluluklar.txt": ["group", "team", "club", "association", "band"]
}

def get_category(tag):
    tag_lower = tag.lower()
    # Priority checks
    for filename, keywords in TAG_MAPPING.items():
        for kw in keywords:
            if kw in tag_lower:
                return filename
    return None

def main():
    zip_path = "/Users/wildgenie/Downloads/TWNERTC_All_Versions/TWNERTC_TC_Fine Grained NER_No_NoiseReduction.zip"
    dump_filename = "TWNERTC_TC_Fine Grained NER_No_NoiseReduction.DUMP"
    gaz_dir = "gazetteers"

    # Store new unique entries
    new_entries = defaultdict(set)

    print(f"Processing {zip_path}...")

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open(dump_filename) as f:
                for idx, line in enumerate(f):
                    try:
                        line_str = line.decode('utf-8').strip()
                        parts = line_str.split('\t')
                        if len(parts) < 3: continue

                        tags = parts[1].split()
                        tokens = parts[2].split()

                        if len(tags) != len(tokens): continue

                        # Extract Entities
                        current_entity = []
                        current_tag_type = None

                        for token, tag in zip(tokens, tags):
                            if tag.startswith("B-"):
                                # Save previous if exists
                                if current_entity and current_tag_type:
                                    full_entity = " ".join(current_entity)
                                    target_file = get_category(current_tag_type)
                                    if target_file and clean_line(full_entity):
                                        new_entries[target_file].add(clean_line(full_entity))

                                # Start new
                                current_tag_type = tag[2:] # Remove B-
                                current_entity = [token]

                            elif tag.startswith("I-") and current_tag_type:
                                # Continue existing
                                # Check if tag type matches roughly or just append
                                # Usually I-tag matches B-tag type.
                                current_entity.append(token)

                            else: # O or mismatch
                                if current_entity and current_tag_type:
                                    full_entity = " ".join(current_entity)
                                    target_file = get_category(current_tag_type)
                                    if target_file and clean_line(full_entity):
                                        new_entries[target_file].add(clean_line(full_entity))
                                current_entity = []
                                current_tag_type = None

                        # Catch last entity
                        if current_entity and current_tag_type:
                            full_entity = " ".join(current_entity)
                            target_file = get_category(current_tag_type)
                            if target_file and clean_line(full_entity):
                                new_entries[target_file].add(clean_line(full_entity))

                        if idx % 50000 == 0:
                            print(f"Processed {idx} sentences...")

                    except Exception as e:
                        continue

        print("\nIngestion complete. Merging with existing gazetteers...")

        for filename, entries in new_entries.items():
            path = os.path.join(gaz_dir, filename)
            existing = set()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip(): existing.add(line.strip())

            initial_count = len(existing)
            # Merge
            existing.update(entries)
            final_count = len(existing)
            added = final_count - initial_count

            # Write back sorted
            with open(path, 'w', encoding='utf-8') as f:
                for item in sorted(list(existing)):
                    f.write(item + "\n")

            print(f"Updated {filename}: +{added} entries (Total: {final_count})")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
