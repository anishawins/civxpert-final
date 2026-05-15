import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset
import os, json

MODEL_PATH = "models/department_bert"

class ComplaintDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

def train():
    print("Loading dataset...")
    df = pd.read_csv("data/department_data.csv")
    df = df.dropna()

    le = LabelEncoder()
    df["label"] = le.fit_transform(df["department"])

    os.makedirs(MODEL_PATH, exist_ok=True)
    label_map = {i: label for i, label in enumerate(le.classes_)}
    with open(f"{MODEL_PATH}/label_map.json", "w") as f:
        json.dump(label_map, f)
    print("Labels:", label_map)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    tokenizer.save_pretrained(MODEL_PATH)

    train_dataset = ComplaintDataset(train_texts, train_labels, tokenizer)
    val_dataset = ComplaintDataset(val_texts, val_labels, tokenizer)

    print("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=len(le.classes_)
    )

    # Class weights to handle imbalance
    from collections import Counter
    import numpy as np
    count = Counter(labels)
    total = len(labels)
    weights = [total / (len(count) * count[i]) for i in range(len(count))]
    print("Class weights:", weights)

    args = TrainingArguments(
        output_dir=MODEL_PATH,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=20,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    print("Training started... (5-10 mins)")
    trainer.train()

    print("Saving model...")
    model.save_pretrained(MODEL_PATH)

    print("Evaluating...")
    preds = trainer.predict(val_dataset)
    pred_labels = preds.predictions.argmax(-1)
    y_true = [label_map[l] for l in val_labels]
    y_pred = [label_map[l] for l in pred_labels]
    print(classification_report(y_true, y_pred))
    print("✅ Department BERT trained! Saved to", MODEL_PATH)

if __name__ == "__main__":
    train()
