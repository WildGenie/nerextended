"""
NER Extended - Test Suite
========================
Tüm modüllerin birim testleri
"""

import unittest
import os
import sys
import json

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPreprocessing(unittest.TestCase):
    """Preprocessing modülü testleri"""

    def test_import(self):
        """Modül import edilebilmeli"""
        from src.preprocessing import Preprocessor
        self.assertTrue(True)

    def test_preprocessor_init(self):
        """Preprocessor başlatılabilmeli"""
        from src.preprocessing import Preprocessor
        prep = Preprocessor()
        self.assertIsNotNone(prep)

    def test_process_sentence(self):
        """Cümle işlenebilmeli"""
        from src.preprocessing import Preprocessor
        prep = Preprocessor()
        tokens = ["Merhaba", "dünya"]
        result = prep.process_sentence(tokens)
        self.assertEqual(len(result), 2)
        self.assertIn("word", result[0])


class TestFeatures(unittest.TestCase):
    """Feature extraction modülü testleri"""

    def test_import(self):
        """Modül import edilebilmeli"""
        from src.features import FeatureExtractor
        self.assertTrue(True)

    def test_feature_extractor_init(self):
        """FeatureExtractor başlatılabilmeli"""
        from src.features import FeatureExtractor
        feat = FeatureExtractor("gazetteers")
        self.assertIsNotNone(feat)

    def test_gazetteers_loaded(self):
        """Gazetteerler yüklenmeli"""
        from src.features import FeatureExtractor
        feat = FeatureExtractor("gazetteers")
        # En azından bir gazetteer yüklenmeli
        self.assertGreater(len(feat.full_names), 0)

    def test_word2features(self):
        """Token için özellikler çıkarılabilmeli"""
        from src.features import FeatureExtractor
        from src.preprocessing import Preprocessor

        prep = Preprocessor()
        feat = FeatureExtractor("gazetteers")

        sent = prep.process_sentence(["İstanbul", "güzel"])
        features = feat.word2features(sent, 0)

        self.assertIsInstance(features, dict)
        self.assertIn("word.lower()", features)


class TestDataAugmentor(unittest.TestCase):
    """Data augmentation modülü testleri"""

    def test_import(self):
        """Modül import edilebilmeli"""
        from src.data_augmentor import DataAugmentor
        self.assertTrue(True)

    def test_augmentor_init(self):
        """DataAugmentor başlatılabilmeli"""
        from src.data_augmentor import DataAugmentor
        aug = DataAugmentor("gazetteers")
        self.assertIsNotNone(aug)

    def test_generate_sentence(self):
        """Sentetik cümle üretilebilmeli"""
        from src.data_augmentor import DataAugmentor
        aug = DataAugmentor("gazetteers")
        tokens, tags = aug.generate_sentence('kisiler')

        self.assertGreater(len(tokens), 0)
        self.assertEqual(len(tokens), len(tags))


class TestModels(unittest.TestCase):
    """Model sınıfları testleri"""

    def test_crf_import(self):
        """CRF modeli import edilebilmeli"""
        from src.models.crf_model import CRFModel
        self.assertTrue(True)

    def test_hmm_import(self):
        """HMM modeli import edilebilmeli"""
        from src.models.hmm_model import HMMModel
        self.assertTrue(True)

    def test_crf_init(self):
        """CRF modeli başlatılabilmeli"""
        from src.models.crf_model import CRFModel
        model = CRFModel()
        self.assertIsNotNone(model)


class TestGazetteers(unittest.TestCase):
    """Gazetteer dosyaları testleri"""

    def test_gazetteers_exist(self):
        """Tüm gazetteer dosyaları mevcut olmalı"""
        expected_files = [
            "kisiler.txt",
            "yerler.txt",
            "kurumlar.txt",
            "sirketler.txt",
            "topluluklar.txt",
            "film_muzik.txt"
        ]

        for filename in expected_files:
            path = os.path.join("gazetteers", filename)
            self.assertTrue(os.path.exists(path), f"{filename} bulunamadı")

    def test_gazetteers_not_empty(self):
        """Gazetteer dosyaları boş olmamalı"""
        for filename in os.listdir("gazetteers"):
            if filename.endswith(".txt"):
                path = os.path.join("gazetteers", filename)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                self.assertGreater(len(content), 0, f"{filename} boş")


class TestDataFiles(unittest.TestCase):
    """Veri dosyaları testleri"""

    def test_json_exports_exist(self):
        """JSON export dosyaları mevcut olmalı"""
        expected_files = [
            "wikiann_final.json",
            "wikiner_final.json",
            "synthetic_final.json",
            "gold_extended_final.json"
        ]

        for filename in expected_files:
            path = os.path.join("data", "json_export", filename)
            self.assertTrue(os.path.exists(path), f"{filename} bulunamadı")

    def test_json_valid(self):
        """JSON dosyaları geçerli formatta olmalı"""
        for filename in os.listdir("data/json_export"):
            if filename.endswith(".json"):
                path = os.path.join("data", "json_export", filename)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        self.assertIsInstance(data, list)
                    except json.JSONDecodeError:
                        self.fail(f"{filename} geçersiz JSON")

    def test_taxonomy_valid(self):
        """taxonomy.json geçerli olmalı"""
        path = "data/taxonomy.json"
        self.assertTrue(os.path.exists(path))

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("supported_tags", data)


class TestTrainedModel(unittest.TestCase):
    """Eğitilmiş model testleri"""

    def test_model_exists(self):
        """Eğitilmiş model dosyası mevcut olmalı"""
        self.assertTrue(os.path.exists("models/ner_crf_model.pkl"))

    def test_model_loadable(self):
        """Model yüklenebilmeli"""
        import pickle
        with open("models/ner_crf_model.pkl", "rb") as f:
            model = pickle.load(f)
        self.assertIsNotNone(model)

    def test_model_prediction(self):
        """Model tahmin yapabilmeli"""
        import pickle
        from src.preprocessing import Preprocessor
        from src.features import FeatureExtractor

        with open("models/ner_crf_model.pkl", "rb") as f:
            model = pickle.load(f)

        prep = Preprocessor()
        feat = FeatureExtractor("gazetteers")

        tokens = ["Tarkan", "İstanbul", "konser"]
        processed = prep.process_sentence(tokens)
        features = feat.sent2features(processed)

        predictions = model.predict([features])[0]

        self.assertEqual(len(predictions), 3)
        self.assertIn(predictions[0], ["B-PER", "I-PER", "O", "B-LOC", "I-LOC",
                                        "B-ORG", "I-ORG", "B-COMPANY", "I-COMPANY",
                                        "B-GROUP", "I-GROUP", "B-MOVIE", "I-MOVIE"])


class TestIntegration(unittest.TestCase):
    """Entegrasyon testleri"""

    def test_full_pipeline(self):
        """Tam pipeline çalışmalı"""
        import pickle
        from src.preprocessing import Preprocessor
        from src.features import FeatureExtractor

        # Model yükle
        with open("models/ner_crf_model.pkl", "rb") as f:
            model = pickle.load(f)

        prep = Preprocessor()
        feat = FeatureExtractor("gazetteers")

        # Test cümleleri
        test_sentences = [
            "Tarkan İstanbul'da konser verdi.",
            "Koç Holding yeni yatırım açıkladı.",
            "Fenerbahçe maç kazandı."
        ]

        for sent in test_sentences:
            tokens = sent.split()
            processed = prep.process_sentence(tokens)
            features = feat.sent2features(processed)
            predictions = model.predict([features])[0]

            self.assertEqual(len(predictions), len(tokens))

    def test_known_entities(self):
        """Bilinen varlıklar doğru tanınmalı"""
        import pickle
        from src.preprocessing import Preprocessor
        from src.features import FeatureExtractor

        with open("models/ner_crf_model.pkl", "rb") as f:
            model = pickle.load(f)

        prep = Preprocessor()
        feat = FeatureExtractor("gazetteers")

        # Tarkan kişi olarak tanınmalı
        tokens = ["Tarkan", "sahneye", "çıktı"]
        processed = prep.process_sentence(tokens)
        features = feat.sent2features(processed)
        predictions = model.predict([features])[0]

        self.assertEqual(predictions[0], "B-PER")


if __name__ == "__main__":
    # Test runner
    unittest.main(verbosity=2)
