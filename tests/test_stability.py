import unittest
import os
import sys
import platform

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStability(unittest.TestCase):
    """Sistem kararlılığı ve yeni eklenen özelliklerin testleri"""

    def test_hardware_detection(self):
        """ARM64 algılama mantığı doğru çalışmalı"""
        is_arm = platform.machine() == "arm64"
        # Bu test sadece bir bilgilendirme niteliğindedir, başarısız olmaz
        print(f"\n[INFO] Donanım: {platform.machine()}, ARM64 mu? {is_arm}")
        self.assertIsInstance(is_arm, bool)

    def test_professional_models_exist(self):
        """Teslim edilecek profesyonel modeller mevcut olmalı"""
        required_models = [
            "models/crf_gold_best.pkl",
            "models/crf_gold_no_emb.pkl",
            "models/crf_gold_gaz_only.pkl"
        ]
        for m in required_models:
            self.assertTrue(os.path.exists(m), f"Eksik model: {m}")

    def test_dependencies_installed(self):
        """Kritik kütüphaneler yüklü olmalı"""
        try:
            import streamlit
            import pandas
            import plotly
            import annotated_text
            import sparknlp
            import pyspark
            print("\n[INFO] Tüm kritik bağımlılıklar yüklü.")
        except ImportError as e:
            self.fail(f"Eksik bağımlılık: {str(e)}")

    def test_spark_nlp_init(self):
        """Spark NLP oturumu başlatılabilmeli (M1/M2 uyumu dahil)"""
        import sparknlp
        is_arm = platform.machine() == "arm64"
        try:
            # Sadece testi başlatıp kapatıyoruz
            spark = sparknlp.start(apple_silicon=is_arm)
            self.assertIsNotNone(spark)
            spark.stop()
            print("\n[INFO] Spark NLP başarıyla başlatıldı ve durduruldu.")
        except Exception as e:
            self.fail(f"Spark NLP başlatılamadı: {str(e)}")

class TestInference(unittest.TestCase):
    """Çıkarım (Inference) kalitesi testleri"""

    def test_best_model_entities(self):
        """En iyi model temel varlıkları tanıyabilmeli"""
        from src.models.crf_model import CRFModel
        from src.features import FeatureExtractor
        from src.preprocessing import Preprocessor
        from nltk.tokenize import word_tokenize

        model = CRFModel.load("models/crf_gold_best.pkl")
        extractor = FeatureExtractor(use_gazetteers=True, use_morphology=True, use_embeddings=True)
        preprocessor = Preprocessor(engine="nuve")

        text = "Mustafa Kemal Atatürk Ankara'da Türkiye Cumhuriyeti'ni kurdu."
        tokens = word_tokenize(text)
        processed = preprocessor.process_sentence(tokens)
        features = [extractor.sent2features(processed)]
        preds = model.predict(features)[0]

        # Temel kontroller
        self.assertIn("B-PER", preds)
        self.assertIn("B-LOC", preds)

if __name__ == "__main__":
    unittest.main(verbosity=2)
