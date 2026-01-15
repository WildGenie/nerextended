from nltk.tag import HiddenMarkovModelTagger, HiddenMarkovModelTrainer
from nltk.tag.hmm import HiddenMarkovModelTrainer
import logging

class HMMModel:
    def __init__(self):
        self.model = None

    def train(self, train_data):
        """
        Train HMM model.
        train_data: List of List of (token, label) tuples.
        """
        logging.info("Training HMM Model...")
        trainer = HiddenMarkovModelTrainer()
        self.model = trainer.train_supervised(train_data)
        logging.info("HMM Training Complete.")

    def predict(self, tokens):
        """
        Predict tags for a list of tokens.
        """
        if not self.model:
            raise ValueError("Model not trained.")

        # HMM requires list of tokens
        tagged = self.model.tag(tokens)
        return [tag for word, tag in tagged]
