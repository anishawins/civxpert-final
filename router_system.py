import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from rapidfuzz import fuzz
import os

MODEL_PATH = "models/priority_bert"
LABELS = {0: "High", 1: "Medium", 2: "Low"}

print("Loading BERT model...")
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()
print("BERT model loaded!")

ROUTING_KEYWORDS = {
    "Electricity": {
        "department": "State Electricity Board",
        "category": "Electricity",
        "keywords": ["power cut", "electricity", "streetlight", "transformer", "wire", "voltage", "electric", "light pole", "short circuit", "power outage"]
    },
    "Water": {
        "department": "Water Supply Department",
        "category": "Water",
        "keywords": ["water", "pipe burst", "no water", "drainage", "sewage", "leakage", "tap", "borewell", "water supply", "contaminated water"]
    },
    "Roads": {
        "department": "Public Works Department",
        "category": "Roads",
        "keywords": ["pothole", "road", "footpath", "pavement", "speed breaker", "road damage", "traffic", "bridge", "construction", "broken road"]
    },
    "Sanitation": {
        "department": "Municipal Sanitation Department",
        "category": "Environment",
        "keywords": ["garbage", "waste", "trash", "dustbin", "sweeping", "cleaning", "litter", "dump", "sanitation", "garbage collection"]
    },
    "Health": {
        "department": "Public Health Department",
        "category": "Health",
        "keywords": ["hospital", "ambulance", "medicine", "disease", "mosquito", "dengue", "covid", "health", "doctor", "clinic"]
    },
    "Safety": {
        "department": "Police Department",
        "category": "Safety",
        "keywords": ["crime", "theft", "robbery", "accident", "fire", "attack", "harassment", "danger", "unsafe", "violence"]
    },
    "Education": {
        "department": "Education Department",
        "category": "Education",
        "keywords": ["school", "teacher", "college", "education", "students", "classroom", "books", "fees", "scholarship", "library"]
    }
}

def route_complaint(text):
    text_lower = text.lower()
    best_score = 0
    best_match = None

    for dept_key, info in ROUTING_KEYWORDS.items():
        for keyword in info["keywords"]:
            score = fuzz.partial_ratio(keyword, text_lower)
            if score > best_score:
                best_score = score
                best_match = info

    if best_score >= 60 and best_match:
        return best_match["department"], best_match["category"]
    return "General Department", "General"

def predict_priority(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    
    # Adjusted class weights to avoid overpredicting High
    adjusted = logits.clone()
    adjusted[0][0] *= 0.9   # High
    adjusted[0][1] *= 1.0   # Medium
    adjusted[0][2] *= 1.2   # Low
    
    probs = torch.softmax(adjusted, dim=1)
    confidence = torch.max(probs).item()
    pred = torch.argmax(probs, dim=1).item()
    
    return LABELS[pred]
