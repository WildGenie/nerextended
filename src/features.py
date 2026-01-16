import os
import re
import numpy as np

class BERTFeatureExtractor:
    _instance = None

    def __new__(cls, model_name="dbmdz/bert-base-turkish-cased"):
        if cls._instance is None:
            cls._instance = super(BERTFeatureExtractor, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, model_name="dbmdz/bert-base-turkish-cased"):
        if self.initialized:
            return

        import torch
        from transformers import AutoTokenizer, AutoModel

        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        # Use AutoModel to handle BERT, BART (VBART), and GPT (Kumru) architectures
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device).eval()
        self.cache = {}
        self.initialized = True

    def get_sentence_embeddings(self, tokens):
        """
        Extracts contextual embeddings for a sentence.
        Returns a list of vectors (1 per token).
        """
        sent_str = " ".join(tokens)
        if sent_str in self.cache:
            return self.cache[sent_str]

        import torch
        inputs = self.tokenizer(tokens, is_split_into_words=True, return_tensors="pt", padding=True, truncation=True).to(self.device)

        # Filter inputs to only include what the model accepts
        import inspect
        sig = inspect.signature(self.model.forward)
        model_inputs = {k: v for k, v in inputs.items() if k in sig.parameters}

        with torch.no_grad():
            outputs = self.model(**model_inputs)
            # Use last hidden state
            last_hidden_state = outputs.last_hidden_state[0] # (seq_len, 768)

            # Map word tokens back to original tokens (handling subwords)
            word_ids = inputs.word_ids()
            word_embeddings = []

            current_word_idx = -1
            current_word_vecs = []

            for i, word_idx in enumerate(word_ids):
                if word_idx is None: continue # Skip [CLS], [SEP], [PAD]

                if word_idx != current_word_idx:
                    if current_word_vecs:
                        word_embeddings.append(torch.stack(current_word_vecs).mean(dim=0).cpu().numpy())
                    current_word_idx = word_idx
                    current_word_vecs = [last_hidden_state[i]]
                else:
                    current_word_vecs.append(last_hidden_state[i])

            if current_word_vecs:
                word_embeddings.append(torch.stack(current_word_vecs).mean(dim=0).cpu().numpy())

        # Ensure we have the same number of vectors as tokens
        if len(word_embeddings) != len(tokens):
            # This can happen due to truncation or tokenizer edge cases
            if len(word_embeddings) < len(tokens):
                word_embeddings.extend([np.zeros(768)] * (len(tokens) - len(word_embeddings)))
            else:
                word_embeddings = word_embeddings[:len(tokens)]

        self.cache[sent_str] = word_embeddings
        return word_embeddings

class FeatureExtractor:
    def __init__(self, gazetteer_dir="gazetteers", use_gazetteers=True, use_morphology=True,
                 use_embeddings=False, embedding_model="dbmdz/bert-base-turkish-cased"):
        self.use_gazetteers = use_gazetteers
        self.use_morphology = use_morphology
        self.use_embeddings = use_embeddings
        self.gazetteers = {}
        self.embedding_extractor = None
        if self.use_embeddings:
            self.embedding_extractor = BERTFeatureExtractor(model_name=embedding_model)

        # Only load if enabled
        if self.use_gazetteers:
            self.load_gazetteers(gazetteer_dir)
        else:
            self.full_names = {}
            self.tokens_set = {}

    def load_gazetteers(self, gazetteer_dir):
        """
        Loads gazetteer files into sets for fast lookup.
        Stores both full entries and individual tokens.
        """
        self.full_names = {}
        self.tokens_set = {} # For partial membership signal

        if not os.path.exists(gazetteer_dir):
            return

        for filename in os.listdir(gazetteer_dir):
            if filename.endswith(".txt"):
                name = filename.replace(".txt", "")
                path = os.path.join(gazetteer_dir, filename)
                self.full_names[name] = set()
                self.tokens_set[name] = set()

                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = line.strip().lower()
                        if entry:
                            self.full_names[name].add(entry)
                            # Also add individual tokens
                            for t in entry.split():
                                self.tokens_set[name].add(t)

    def check_gazetteer(self, text, gazetteer_name, is_token=False):
        if not self.use_gazetteers:
            return False
        text = text.lower()
        if is_token:
            return text in self.tokens_set.get(gazetteer_name, set())
        return text in self.full_names.get(gazetteer_name, set())

    def word2features(self, sent, i):
        """
        Extracts features for a single word in a sentence.
        """
        word = sent[i]['word']
        lemma = sent[i]['lemma']
        pos = sent[i]['pos']

        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
            'word.has_apostrophe': "'" in word or "’" in word,
        }

        # Morphology Features (Optional)
        if self.use_morphology:
            features['lemma'] = lemma
            features['pos'] = pos

            # Deep Morphology (Nuve) - Standard or Hybrid
            if 'nuve_morph' in sent[i]:
                 morph = sent[i]['nuve_morph']
                 prefix = "nuve."
            else:
                 morph = sent[i].get('morph', [])
                 prefix = "morph." # Backward compatibility

            if isinstance(morph, list) and len(morph) > 0:
                features[f'{prefix}count'] = len(morph)
                features[f'{prefix}last_suffix_id'] = morph[-1].get('Id', '')
                features[f'{prefix}has_change'] = any(m.get('HasChange', False) for m in morph)

                # Suffix sequence feature
                suffix_seq = "-".join([m.get('Id', '') for m in morph if m.get('Type') != 'Root'])
                if suffix_seq:
                    features[f'{prefix}suffix_seq'] = suffix_seq

                # Combine all labels
                for m in morph:
                    for label in m.get('Labels', []):
                        features[f'{prefix}label_{label}'] = True

            # Zemberek Morphology (Hybrid Only)
            if 'zemberek_morph' in sent[i]:
                z_morph = sent[i]['zemberek_morph']
                prefix = "zember."

                if isinstance(z_morph, list) and len(z_morph) > 0:
                     features[f'{prefix}count'] = len(z_morph)
                     features[f'{prefix}last_suffix_id'] = z_morph[-1].get('Id', '')

                     suffix_seq = "-".join([m.get('Id', '') for m in z_morph if m.get('Type') != 'Root'])
                     if suffix_seq:
                        features[f'{prefix}suffix_seq'] = suffix_seq

        # Gazetteer Features (Optional - controlled by self.use_gazetteers)
        if self.use_gazetteers:
            # Multi-word Lookup via Windows
            for g_name in ['kisiler', 'yerler', 'sirketler', 'kurumlar', 'film_muzik', 'topluluklar']:
                # Single word membership
                features[f'in_{g_name}_tokens'] = self.check_gazetteer(word, g_name, is_token=True)

                # Contextual Match (is this word the START of a multi-word gazetteer entry?)
                # Check current + next
                if i < len(sent) - 1:
                    bigram = f"{word} {sent[i+1]['word']}"
                    if self.check_gazetteer(bigram, g_name):
                        features[f'start_bigram_{g_name}'] = True

                # Check current + next + next next
                if i < len(sent) - 2:
                    trigram = f"{word} {sent[i+1]['word']} {sent[i+2]['word']}"
                    if self.check_gazetteer(trigram, g_name):
                        features[f'start_trigram_{g_name}'] = True

                # Check prev + current
                if i > 0:
                    prev_bigram = f"{sent[i-1]['word']} {word}"
                    if self.check_gazetteer(prev_bigram, g_name):
                        features[f'inside_bigram_{g_name}'] = True

            # Specific keyword indicators (often tied to specific categories like Company/Org)
            word_l = word.lower()
            features.update({
                'kw_holding': 'holding' in word_l,
                'kw_bank': 'banka' in word_l,
                'kw_company_suffix': any(s in word_l for s in ['a.ş', 'ltd', 'şirketi']),
                'kw_group_suffix': any(s in word_l for s in ['grubu', 'kulübü', 'derneği', 'partisi']),
                'kw_org_suffix': any(s in word_l for s in ['vakfı', 'üniversitesi', 'belediyesi'])
            })

            # Regex Features (Extended NER cues)
            if re.search(r'(Derneği|Kulübü|Topluluğu)$', word):
                features['suffix_group'] = True
            if re.search(r'(Vakfı|Birliği|Fonu)$', word):
                features['suffix_org'] = True

        # Context Features
        if i > 0:
            word1 = sent[i-1]['word']
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
                '-1:word.isupper()': word1.isupper(),
            })
            if self.use_morphology:
                features['-1:lemma'] = sent[i-1]['lemma']
        else:
            features['BOS'] = True

        if i < len(sent)-1:
            word1 = sent[i+1]['word']
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
                '+1:word.isupper()': word1.isupper(),
            })
            if self.use_morphology:
                 features['+1:lemma'] = sent[i+1]['lemma']
        else:
            features['EOS'] = True

        return features

    def sent2features(self, sent):
        features_list = [self.word2features(sent, i) for i in range(len(sent))]

        # Add embedding features if enabled
        if self.use_embeddings and self.embedding_extractor:
            tokens = [w['word'] for w in sent]
            embeddings = self.embedding_extractor.get_sentence_embeddings(tokens)
            for i, emb in enumerate(embeddings):
                # We use a very simplified mapping or just a few dimensions to avoid exploding CRF features
                # In a real scenario, we might use PCA. Here we'll just use the first 16 values as a demo.
                for j in range(16):
                    features_list[i][f'emb_{j}'] = float(emb[j])

        return features_list
