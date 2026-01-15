import sparknlp
from sparknlp.base import DocumentAssembler, Pipeline, LightPipeline
from sparknlp.annotator import Tokenizer, SentenceDetector, BertEmbeddings, NerDLModel, NerConverter
import os

try:
    print("Starting Spark NLP with Apple Silicon support...")
    # Fix for M1/M2/M3 Macs
    spark = sparknlp.start(apple_silicon=True)

    print("Loading models...")
    documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")

    # Exact pipeline
    embeddings = BertEmbeddings.pretrained('bert_multi_cased', 'xx').setInputCols(["sentence", "token"]).setOutputCol("embeddings")
    public_ner = NerDLModel.pretrained('turkish_ner_bert', 'tr').setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    ner_converter = NerConverter().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")

    nlp_pipeline = Pipeline(stages=[documentAssembler, sentenceDetector, tokenizer, embeddings, public_ner, ner_converter])

    print("Fitting empty dataframe...")
    empty_df = spark.createDataFrame([['']]).toDF('text')
    pipeline_model = nlp_pipeline.fit(empty_df)

    print("Creating LightPipeline...")
    light_pipe = LightPipeline(pipeline_model)

    text = "Fenerbahçe şampiyon oldu."
    print(f"Testing text: {text}")
    res = light_pipe.fullAnnotate(text)

    print("Result:", res[0]['ner_chunk'])
    print("\nSUCCESS!")

except Exception as e:
    print("\nFAILED!")
    print("Error message:", str(e))
    import traceback
    traceback.print_exc()
