"""Evaluate CivXpert classifiers on held-out validation data.

Usage:
    python ml/evaluate_models.py --model department
    python ml/evaluate_models.py --model priority

The script reports accuracy, macro/weighted precision, recall and F1, plus
per-class metrics. It never writes fabricated metrics into the repository.
"""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

ROOT = Path(__file__).resolve().parents[1]

CONFIG = {
    "department": {
        "data": ROOT / "data" / "department_data.csv",
        "text": "text",
        "label": "department",
        "model": ROOT / "models" / "department_bert",
    },
    "priority": {
        "data": ROOT / "data" / "priority_master.csv",
        "text": "text",
        "label": "priority",
        "model": ROOT / "models" / "priority_bert",
    },
}


def evaluate(name):
    cfg = CONFIG[name]
    df = pd.read_csv(cfg["data"]).dropna(subset=[cfg["text"], cfg["label"]])

    texts = df[cfg["text"]].astype(str).tolist()
    labels = df[cfg["label"]].astype(str).tolist()
    _, val_texts, _, val_labels = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"])
    model = AutoModelForSequenceClassification.from_pretrained(cfg["model"])
    model.eval()

    predictions = []
    for start in range(0, len(val_texts), 32):
        batch = val_texts[start:start + 32]
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.inference_mode():
            logits = model(**inputs).logits
        predictions.extend(torch.argmax(logits, dim=-1).tolist())

    id_to_label = {int(k): v for k, v in model.config.id2label.items()}
    pred_labels = [id_to_label[i] for i in predictions]

    print(f"\n=== CivXpert {name.title()} Model ===")
    print(f"Validation samples: {len(val_labels)}")
    print(f"Accuracy: {accuracy_score(val_labels, pred_labels):.4f}")
    print("\nClassification report:")
    print(classification_report(val_labels, pred_labels, digits=4, zero_division=0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=CONFIG.keys(), required=True)
    args = parser.parse_args()
    evaluate(args.model)
