import sklearn_crfsuite
from sklearn_crfsuite import metrics
import logging
import joblib
import os
import json

class CRFModel:
    def __init__(self, c1=0.1, c2=0.1):
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=c1,
            c2=c2,
            max_iterations=100,
            all_possible_transitions=True
        )

    def train(self, X_train, y_train):
        """
        Train CRF model.
        X_train: List of feature lists
        y_train: List of label lists
        """
        logging.info("Training CRF Model...")
        self.model.fit(X_train, y_train)
        logging.info("CRF Training Complete.")

    def get_top_features(self, n=20):
        """Returns the top N state features and their weights."""
        from collections import Counter
        features = Counter(self.model.state_features_).most_common(n)
        return [{"feature": f, "weight": w} for f, w in features]

    def get_top_transitions(self, n=20):
        """Returns the top N transition features and their weights."""
        from collections import Counter
        transitions = Counter(self.model.transition_features_).most_common(n)
        return [{"from": t[0], "to": t[1], "weight": w} for t, w in transitions]

    def save(self, filepath):
        """Saves the model to a joblib file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)
        logging.info(f"Model saved to {filepath}")

    def save_weights(self, filepath):
        """Saves top features and transitions to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        weights = {
            "top_features": self.get_top_features(100),
            "top_transitions": self.get_top_transitions(100)
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=4, ensure_ascii=False)
        logging.info(f"Weights saved to {filepath}")

    def predict(self, X_test):
        return self.model.predict(X_test)

    def evaluate(self, X_test, y_test):
        y_pred = self.predict(X_test)
        labels = list(self.model.classes_)
        labels.remove('O') if 'O' in labels else None

        f1 = metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels)
        report = metrics.flat_classification_report(y_test, y_pred, labels=labels)
        return f1, report

    @classmethod
    def load(cls, filepath):
        """Loads a model from a joblib file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No model found at {filepath}")

        instance = cls()
        instance.model = joblib.load(filepath)
        logging.info(f"Model loaded from {filepath}")
        return instance
