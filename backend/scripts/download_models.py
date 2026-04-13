"""Download all transformer models to MODEL_CACHE_DIR at build time."""
import os
import sys

CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "/models")

TRANSFORMER_MODELS = [
    "distilbert-base-uncased-finetuned-sst-2-english",
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "valhalla/distilbart-mnli-12-1",
]

SENTENCE_TRANSFORMER_MODELS = [
    "all-MiniLM-L6-v2",
]

def download_transformer_models():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    for model_id in TRANSFORMER_MODELS:
        print(f"  Downloading transformer model: {model_id}")
        AutoTokenizer.from_pretrained(model_id, cache_dir=CACHE_DIR)
        AutoModelForSequenceClassification.from_pretrained(model_id, cache_dir=CACHE_DIR)
        print(f"  Done: {model_id}")

def download_sentence_transformer_models():
    from sentence_transformers import SentenceTransformer
    for model_id in SENTENCE_TRANSFORMER_MODELS:
        print(f"  Downloading sentence-transformer model: {model_id}")
        SentenceTransformer(model_id, cache_folder=CACHE_DIR)
        print(f"  Done: {model_id}")

if __name__ == "__main__":
    print(f"Downloading models to {CACHE_DIR} ...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    download_transformer_models()
    download_sentence_transformer_models()
    print("All models downloaded successfully.")
