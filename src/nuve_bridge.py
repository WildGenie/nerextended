import subprocess
import os
import logging
import json

class NuveBridge:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NuveBridge, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.nuve_path = "nuve_wrapper"
        self.initialized = True
        self.cache = {}

    def pre_analyze(self, tokens_list):
        """
        Pre-fills the cache for all tokens in tokens_list in a single call.
        """
        unique_tokens = list(set(tokens_list))
        logging.info(f"Nuve Pre-analyzing {len(unique_tokens)} unique tokens...")
        return self.analyze_batch(unique_tokens)

    def analyze_batch(self, tokens):
        """
        Analyzes a large list of tokens in one subprocess call.
        """
        # Filter tokens not in cache
        to_analyze = [t for t in tokens if t not in self.cache]

        if not to_analyze:
            return {t: self.cache[t] for t in tokens}

        try:
            process = subprocess.Popen(
                ["dotnet", "run", "--project", self.nuve_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            input_text = "\n".join(to_analyze) + "\n"
            stdout, stderr = process.communicate(input=input_text)

            for line in stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    res_json = json.loads(line)
                    word = res_json.get("Word")
                    analyses = res_json.get("Analyses", [])

                    if word and analyses:
                        # Store first analysis (highest probability usually in Nuve)
                        best = analyses[0]
                        self.cache[word] = {
                            "lemma": best.get("Stem"),
                            "morphemes": best.get("Morphemes", []),
                            "full_analysis": res_json
                        }
                    elif word:
                        self.cache[word] = {"lemma": word, "morphemes": [], "is_unknown": True}
                except json.JSONDecodeError:
                    pass

            # Fallback for failed ones
            for t in to_analyze:
                if t not in self.cache:
                    self.cache[t] = {"lemma": t, "morphemes": [], "pos": "UNK"}

        except Exception as e:
            logging.error(f"NuveBridge Error: {e}")
            for t in to_analyze:
                if t not in self.cache:
                    self.cache[t] = {"lemma": t, "morphemes": [], "pos": "UNK"}

        return {t: self.cache[t] for t in tokens}

    def analyze(self, token):
        if token in self.cache:
            return self.cache[token]
        return self.analyze_batch([token])[token]
