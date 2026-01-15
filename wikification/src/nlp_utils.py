import re
import string

class NLPUtils:
    def __init__(self):
        # Basic Turkish Stopwords list
        self.stop_words = {
            "ve", "veya", "ama", "ancak", "lakin", "fakat", "ile", "için", "bir",
            "bu", "şu", "o", "ben", "sen", "biz", "siz", "onlar", "de", "da",
            "ki", "mi", "mı", "mu", "mü", "gibi", "kadar", "olan", "tarafından",
            "olarak", "den", "dan", "çok", "daha", "en", "ne", "neden", "nasıl",
            "her", "şey", "diye", "yok", "var"
        }

    def clean_text(self, text):
        """
        Cleans punctuation but keeps inner structure relatively intact.
        Returns a list of tokens.
        """
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.split()

    def generate_ngrams(self, tokens, n=3):
        """
        Generates N-grams from tokens up to size n.
        Returns a list of (start_index, end_index, ngram_string) tuples.
        Longer N-grams come first (greedy approach potential).
        """
        ngrams = []
        l = len(tokens)

        # We iterate for each size from n down to 1
        for size in range(n, 0, -1):
            for i in range(l - size + 1):
                chunk = tokens[i:i+size]

                # Evaluation: Skip if starts or ends with stopword?
                # Usually entity names don't start/end with stopwords (e.g. "Ve Recep Tayyip Erdoğan")
                if chunk[0].lower() in self.stop_words or chunk[-1].lower() in self.stop_words:
                    continue

                term = " ".join(chunk)
                ngrams.append({
                    "start": i,
                    "end": i + size,
                    "term": term,
                    "size": size
                })
        return ngrams
