import logging
from src.nlp_utils import NLPUtils
from src.wiki_client import WikiClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EntityLinker:
    def __init__(self):
        self.nlp = NLPUtils()
        self.wiki = WikiClient()
        logging.info("EntityLinker initialized.")

    def link_entities(self, text):
        """
        Main method to find and link entities in text.
        """
        tokens = self.nlp.clean_text(text)
        ngrams = self.nlp.generate_ngrams(tokens, n=3) # Look for up to 3-word entities

        found_entities = []
        covered_indices = set() # To avoid overlapping entities (e.g. "Koç Holding" vs "Holdings")

        # Sort N-grams by size (DESC) to prioritize longest matches
        sorted_ngrams = sorted(ngrams, key=lambda x: x['size'], reverse=True)

        for item in sorted_ngrams:
            start, end = item['start'], item['end']
            term = item['term']

            # Check overlap
            if any(i in covered_indices for i in range(start, end)):
                continue

            # Query Wikipedia
            page = self.wiki.get_page(term)

            if page.exists():
                # Check for disambiguation
                if self.wiki.is_disambiguation(page):
                     logging.info(f"Disambiguating '{term}' (Page: {page.title})...")

                     # 1. Get options
                     candidates = self.wiki.get_disambiguation_candidates(page, limit=5)

                     if candidates:
                         # 2. Compare summaries with context (entire input text)
                         best_page = self.disambiguate_tf_idf(text, candidates)

                         if best_page:
                             logging.info(f"  -> Resolved to: {best_page.title}")
                             page = best_page
                         else:
                             logging.warning("  -> TF-IDF failed, keeping disambiguation page.")
                     else:
                         logging.warning("  -> No candidates found, keeping disambiguation page.")

                entity_info = {
                    "text": term,
                    "wiki_title": page.title,
                    "url": page.fullurl,
                    "summary": page.summary[:200] + "...",
                    "span": (start, end)
                }

                found_entities.append(entity_info)

                # Mark indices as covered
                for i in range(start, end):
                    covered_indices.add(i)

        # Sort results by position in text (optional)
        return sorted(found_entities, key=lambda x: x['span'][0])

    def disambiguate_tf_idf(self, context_text, candidates):
        """
        Advanced: Select best candidate using TF-IDF cosine similarity.
        candidates: List of page objects.
        """
        if not candidates:
            return None

        docs = [context_text] + [c.summary for c in candidates]
        tfidf = TfidfVectorizer().fit_transform(docs)
        cosine_similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

        best_idx = cosine_similarities.argmax()
        return candidates[best_idx]
