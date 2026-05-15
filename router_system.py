import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json

# ── Priority BERT ─────────────────────────────────────────────
PRIORITY_MODEL_PATH = "models/priority_bert"
PRIORITY_LABELS = {0: "High", 1: "Medium", 2: "Low"}

print("Loading Priority BERT...")
priority_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
priority_model = AutoModelForSequenceClassification.from_pretrained(PRIORITY_MODEL_PATH)
priority_model.eval()

# ── Department BERT ───────────────────────────────────────────
DEPT_MODEL_PATH = "models/department_bert"

print("Loading Department BERT...")
dept_tokenizer = AutoTokenizer.from_pretrained(DEPT_MODEL_PATH)
dept_model = AutoModelForSequenceClassification.from_pretrained(DEPT_MODEL_PATH)
dept_model.eval()

with open(f"{DEPT_MODEL_PATH}/label_map.json") as f:
    DEPT_LABEL_MAP = json.load(f)
    DEPT_LABEL_MAP = {int(k): v for k, v in DEPT_LABEL_MAP.items()}

print("Both BERT models loaded!")

# Department → actual government department name
DEPT_TO_GOV = {
    "Electricity":    "State Electricity Board",
    "Water":          "Water Supply Department",
    "Roads":          "Public Works Department",
    "Sanitation":     "Municipal Sanitation Department",
    "Health":         "Public Health Department",
    "Safety":         "Police Department",
    "Education":      "Education Department",
    "Housing":        "Housing Board",
    "Transport":      "Transport Department",
    "Environment":    "Environment Department",
    "Animal Control": "Animal Control Department",
    "Municipal":      "Municipal Corporation",
}

# Priority overrides for specific department+keyword combos
HIGH_OVERRIDE_KEYWORDS = ["fire", "accident", "attack", "robbery", "murder", "flood",
                           "collapse", "emergency", "violence", "death", "injury",
                           "rabies", "dengue", "epidemic", "explosion", "electrocution"]
LOW_OVERRIDE_KEYWORDS  = ["suggestion", "request", "minor", "small", "feedback",
                           "paint", "name board", "beautify", "missing dog",
                           "missing cat", "missing pet", "stray dog barking"]

def route_complaint(text):
    inputs = dept_tokenizer(text, return_tensors="pt", truncation=True,
                            padding=True, max_length=128)
    with torch.no_grad():
        outputs = dept_model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    confidence = torch.max(probs).item()
    pred = torch.argmax(probs, dim=1).item()
    category = DEPT_LABEL_MAP[pred]
    department = DEPT_TO_GOV.get(category, "General Department")
    return department, category

def predict_priority(text):
    text_lower = text.lower()

    # Hard overrides first
    for word in HIGH_OVERRIDE_KEYWORDS:
        if word in text_lower:
            inputs = priority_tokenizer(text, return_tensors="pt",
                                        truncation=True, padding=True, max_length=128)
            with torch.no_grad():
                outputs = priority_model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence = torch.max(probs).item()
            return "High", round(confidence * 100, 2)

    for word in LOW_OVERRIDE_KEYWORDS:
        if word in text_lower:
            inputs = priority_tokenizer(text, return_tensors="pt",
                                        truncation=True, padding=True, max_length=128)
            with torch.no_grad():
                outputs = priority_model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            confidence = torch.max(probs).item()
            return "Low", round(confidence * 100, 2)

    # BERT prediction
    inputs = priority_tokenizer(text, return_tensors="pt", truncation=True,
                                padding=True, max_length=128)
    with torch.no_grad():
        outputs = priority_model(**inputs)

    logits = outputs.logits
    adjusted = logits.clone()
    adjusted[0][0] *= 0.9   # High
    adjusted[0][1] *= 1.0   # Medium
    adjusted[0][2] *= 1.2   # Low

    probs = torch.softmax(adjusted, dim=1)
    confidence = torch.max(probs).item()
    pred = torch.argmax(probs, dim=1).item()
    return PRIORITY_LABELS[pred], round(confidence * 100, 2)
