import sys
import os

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.linker import EntityLinker

def main():
    print("Initializing Entity Linker (Wikipedia API)...")
    linker = EntityLinker()

    test_sentences = [
        "Barış Manço, Sarı Zeybek belgeselini hazırladı.",
        "Türkiye'nin başkenti Ankara'dır.",
        "Koç Holding, yeni elektrikli araç yatırımı yaptı.",
        "Gri madde beyinde bulunur.",
        "Mısır piramitleri çok etkileyicidir.",
        "Pazardan taze mısır aldım, haşlayıp yedik.",
        "Bugün hava çok sıcak, yüzünü yıka."
    ]

    print("\n--- Starting Demo ---\n")

    for text in test_sentences:
        print(f"Input: {text}")
        results = linker.link_entities(text)

        if not results:
            print("  No entities found.")

        for res in results:
            print(f"  Found: {res['text']}")
            print(f"    -> Link: {res['wiki_title']} ({res['url']})")
        print("-" * 40)

if __name__ == "__main__":
    main()
