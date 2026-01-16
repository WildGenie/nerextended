import os
import logging
import re
from datasets import load_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to import Zemberek, fall back to regex-based analysis if unavailable
try:
    from zemberek import TurkishMorphology
    ZEMBEREK_AVAILABLE = True
except ImportError:
    ZEMBEREK_AVAILABLE = False
    logging.warning("Zemberek not available, using regex-based morphological analysis")


class Preprocessor:
    def __init__(self, engine="zemberek"):
        """
        engine: "zemberek" (default) or "nuve"
        """
        self.engine = engine
        self.morphology = None
        self.nuve = None

        if self.engine == "zemberek":
            if ZEMBEREK_AVAILABLE:
                logging.info("Initializing Zemberek Morphology...")
                try:
                    self.morphology = TurkishMorphology.create_with_defaults()
                    logging.info("Zemberek initialized.")
                except Exception as e:
                    logging.warning(f"Zemberek initialization failed: {e}, using fallback")
            else:
                logging.info("Using regex-based Turkish morphological analysis")
        elif self.engine == "nuve":
            from src.nuve_bridge import NuveBridge
            logging.info("Initializing Nuve Bridge...")
            self.nuve = NuveBridge()
            logging.info("Nuve Bridge initialized.")
        elif self.engine == "hybrid":
            # Initialize BOTH
            if ZEMBEREK_AVAILABLE:
                logging.info("Initializing Zemberek (Hybrid)...")
                try:
                    self.morphology = TurkishMorphology.create_with_defaults()
                except Exception as e:
                    logging.warning(f"Zemberek init failed: {e}")
            else:
                logging.warning("Zemberek not available for hybrid mode.")

            from src.nuve_bridge import NuveBridge
            logging.info("Initializing Nuve Bridge (Hybrid)...")
            self.nuve = NuveBridge()

    def load_wikiann(self, split="train", limit=None):
        """
        Loads the WikiANN (tr) dataset.
        """
        logging.info(f"Loading WikiANN (tr) split: {split}")
        try:
            dataset = load_dataset("wikiann", "tr", split=split)
            if limit:
                dataset = dataset.select(range(limit))
            return dataset
        except Exception as e:
            logging.error(f"Failed to load dataset: {e}")
            return None

    def load_wikiner(self, split="train", limit=None):
        """
        Loads the turkish-nlp-suite/turkish-wikiNER dataset.
        """
        logging.info(f"Loading Turkish WikiNER split: {split}")
        try:
            dataset = load_dataset("turkish-nlp-suite/turkish-wikiNER", split=split)
            if limit:
                dataset = dataset.select(range(limit))
            return dataset
        except Exception as e:
            logging.error(f"Failed to load dataset: {e}")
            return None

    def _regex_analyze(self, word):
        """
        Regex-based Turkish morphological analysis fallback.
        Strips common Turkish suffixes to find approximate lemma.
        """
        # Common Turkish suffixes (order matters - longer first)
        suffixes = [
            "'tan", "'ten", "'dan", "'den",  # Ablative
            "'ta", "'te", "'da", "'de",       # Locative
            "'nın", "'nin", "'nun", "'nün",   # Genitive
            "'ın", "'in", "'un", "'ün",       # Genitive without buffer
            "'ya", "'ye", "'a", "'e",         # Dative
            "'yı", "'yi", "'ı", "'i", "'u", "'ü",  # Accusative
            "lar", "ler",                      # Plural
            "dır", "dir", "dur", "dür",       # Copula
            "mış", "miş", "muş", "müş",       # Past participle
            "yor", "iyor", "uyor", "üyor",    # Present continuous
        ]

        lemma = word
        for suffix in suffixes:
            if lemma.lower().endswith(suffix):
                lemma = lemma[:-len(suffix)]
                break

        # Determine POS based on patterns
        if word[0].isupper():
            pos = "Noun"  # Proper noun
        elif word.endswith(("mak", "mek")):
            pos = "Verb"
        elif word.endswith(("lı", "li", "lu", "lü", "sız", "siz")):
            pos = "Adj"
        else:
            pos = "Noun"

        return lemma if lemma else word, pos

    def analyze_word(self, word):
        """
        Analyzes a word using Zemberek, Nuve, or regex fallback.
        Returns: lemma, pos, morph_info (dict)
        """
        if self.engine == "zemberek" and self.morphology:
            try:
                results = self.morphology.analyze(word)
                if results.analysis_results:
                    best = results.analysis_results[0]
                    lemma = best.get_stem()
                    pos = best.item.primary_pos.value if hasattr(best.item, 'primary_pos') else "UNK"

                    # Extract rich morph info
                    morphemes = []
                    for md in best.morpheme_data_list:
                        m_id = md.morpheme.id_
                        morphemes.append({
                            "Id": m_id,
                            "Surface": md.surface,
                            "HasChange": len(md.surface) > 0 and md.surface != md.morpheme.id_, # Simple heuristic
                            "Type": "Root" if md == best.morpheme_data_list[0] else "Suffix",
                            "Labels": [] # Zemberek doesn't expose labels the same way as Nuve
                        })

                    return lemma, pos, morphemes
                else:
                    return word, "UNK", []
            except Exception:
                l, p = self._regex_analyze(word)
                return l, p, []
        elif self.engine == "nuve" and self.nuve:
            analysis = self.nuve.analyze(word)
            return analysis['lemma'], "UNK", analysis.get('morphemes', [])
        else:
            l, p = self._regex_analyze(word)
            return l, p, {}

    def process_sentence(self, tokens):
        """
        Analyzes a list of tokens.
        Returns a list of dicts: [{'word': w, 'lemma': l, 'pos': p, 'morph': m}, ...]
        """
        if self.engine == "nuve" and self.nuve:
            # Batch process tokens for speed
            nuve_results = self.nuve.analyze_batch(tokens)
            processed = []
            for token in tokens:
                res = nuve_results.get(token, {'lemma': token, 'morphemes': []})
                processed.append({
                    'word': token,
                    'lemma': res['lemma'],
                    'pos': "UNK",
                    'morph': res.get('morphemes', [])
                })
            return processed

        if self.engine == "hybrid":
            # 1. Get Nuve Results (Batch)
            nuve_results = {}
            if self.nuve:
                nuve_results = self.nuve.analyze_batch(tokens)

            processed = []
            for token in tokens:
                # 2. Get Zemberek Results (Word-by-word)
                z_lemma, z_pos, z_morph = self.analyze_word(token) # analyze_word uses self.morphology if set

                # 3. Get Nuve Result
                n_res = nuve_results.get(token, {'lemma': token, 'morphemes': []})

                processed.append({
                    'word': token,
                    'lemma': n_res['lemma'], # Default to Nuve lemma as primary
                    'pos': z_pos,            # Default to Zemberek POS as primary
                    'morph': n_res.get('morphemes', []), # Default morph

                    # Store Both explicitly
                    'nuve_lemma': n_res['lemma'],
                    'nuve_morph': n_res.get('morphemes', []),

                    'zemberek_lemma': z_lemma,
                    'zemberek_pos': z_pos,
                    'zemberek_morph': z_morph
                })
            return processed

        processed = []
        for token in tokens:
            lemma, pos, morph = self.analyze_word(token)
            processed.append({
                'word': token,
                'lemma': lemma,
                'pos': pos,
                'morph': morph
            })
        return processed


if __name__ == "__main__":
    p = Preprocessor()
    ds = p.load_wikiann(limit=10)
    if ds:
        print("Example 0:", ds[0])
        print("Analysis:", p.process_sentence(ds[0]['tokens']))
