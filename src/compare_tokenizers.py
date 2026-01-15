import logging
import re
from zemberek import TurkishTokenizer
from transformers import AutoTokenizer

def compare_tokenizers(text):
    print(f"Original Text: {text}\n")

    # 1. Simple Regex Split
    simple_tokens = re.findall(r"[\w']+|[.,!?;]", text)
    print(f"Simple Regex: {simple_tokens}")

    # 2. Zemberek Tokenizer
    tokenizer = TurkishTokenizer.DEFAULT
    z_tokens = [t.content for t in tokenizer.tokenize(text)]
    print(f"Zemberek:     {z_tokens}")

    # 3. BERT Tokenizer (Subwords)
    bert_tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")
    bert_tokens = bert_tokenizer.tokenize(text)
    print(f"BERT (Subword): {bert_tokens}")

    # 4. Kumru Tokenizer (VNGRS)
    try:
        kumru_tokenizer = AutoTokenizer.from_pretrained("vngrs-ai/Kumru-2B", trust_remote_code=True)
        kumru_tokens = kumru_tokenizer.tokenize(text)
        # Decode individual tokens for readable output
        decoded_kumru = [kumru_tokenizer.convert_tokens_to_string([t]) for t in kumru_tokens]
        print(f"Kumru (VNGRS): {decoded_kumru}")
    except Exception as e:
        print(f"Kumru Tokenizer failed: {e}")

    # 5. VBART Tokenizer (VNGRS)
    try:
        vbart_tokenizer = AutoTokenizer.from_pretrained("vngrs-ai/VBART-Large-Base", trust_remote_code=True)
        vbart_tokens = vbart_tokenizer.tokenize(text)
        decoded_vbart = [vbart_tokenizer.convert_tokens_to_string([t]) for t in vbart_tokens]
        print(f"VBART (VNGRS): {decoded_vbart}")
    except Exception as e:
        print(f"VBART Tokenizer failed: {e}")

    print("-" * 50)

if __name__ == "__main__":
    test_cases = [
        "İstanbul'un Avrupa yakası çok kalabalık.",
        "Prof. Dr. Ahmet Bey, Ankara'dan geldi.",
        "A.Ş. ve Ltd. Şti. arasındaki anlaşma imzalandı.",
        "Gidiyoruz ama dönmeyeceğiz."
    ]

    for tc in test_cases:
        compare_tokenizers(tc)
