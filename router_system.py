"""Production-oriented inference for CivXpert's trained DistilBERT models.

Models are loaded lazily so the Flask application and lightweight tests do not
need model artifacts just to import the application. Predictions use the
trained model logits directly; no hand-written keyword or logit overrides are
used to manufacture a prediction.
"""

import json
from functools import lru_cache
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent
PRIORITY_MODEL_PATH = ROOT / "models" / "priority_bert"
DEPT_MODEL_PATH = ROOT / "models" / "department_bert"
PRIORITY_LABELS = {0: "High", 1: "Medium", 2: "Low"}
DEPT_TO_GOV = {
    "Electricity": "State Electricity Board",
    "Water": "Water Supply Department",
    "Roads": "Public Works Department",
    "Sanitation": "Municipal Sanitation Department",
    "Health": "Public Health Department",
    "Safety": "Police Department",
    "Education": "Education Department",
    "Housing": "Housing Board",
    "Transport": "Transport Department",
    "Environment": "Environment Department",
    "Animal Control": "Animal Control Department",
    "Municipal": "Municipal Corporation",
}


def _load(model_path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifacts not found at {model_path}. Train/download the model before inference."
        )
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
    model.eval()
    return tokenizer, model


@lru_cache(maxsize=1)
def _priority_model():
    return _load(PRIORITY_MODEL_PATH)


@lru_cache(maxsize=1)
def _department_model():
    return _load(DEPT_MODEL_PATH)


def _predict(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.inference_mode():
        logits = model(**inputs).logits
    probabilities = torch.softmax(logits, dim=-1)[0]
    index = int(torch.argmax(probabilities).item())
    return index, float(probabilities[index].item()), probabilities.tolist()


def route_complaint(text):
    """Return (government department, model category, confidence percentage)."""
    tokenizer, model = _department_model()
    index, confidence, _ = _predict(text, tokenizer, model)
    label_map = model.config.id2label
    category = label_map.get(index, label_map.get(str(index), str(index)))
    department = DEPT_TO_GOV.get(category, "General Department")
    return department, category, round(confidence * 100, 2)


def predict_priority(text):
    """Return (priority label, confidence percentage) from raw model probabilities."""
    tokenizer, model = _priority_model()
    index, confidence, _ = _predict(text, tokenizer, model)
    configured = model.config.id2label
    raw_label = configured.get(index, configured.get(str(index)))
    label = PRIORITY_LABELS.get(index, raw_label or "Medium")
    return label, round(confidence * 100, 2)


def analyze_complaint(text):
    """Run both classifiers and expose a stable, API-friendly prediction object."""
    department, category, department_confidence = route_complaint(text)
    priority, priority_confidence = predict_priority(text)
    return {
        "department": department,
        "category": category,
        "department_confidence": department_confidence,
        "priority": priority,
        "priority_confidence": priority_confidence,
    }
