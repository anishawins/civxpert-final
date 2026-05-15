import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from torch.utils.data import Dataset
import os

LABELS = {"High": 0, "Medium": 1, "Low": 2}
MODEL_PATH = "models/priority_bert"

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
    df = pd.read_csv("data/priority_master.csv")
    df = df.dropna()
    df = df[df["priority"].isin(LABELS.keys())]
    
    texts = df["text"].tolist()
    labels = [LABELS[p] for p in df["priority"].tolist()]

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    print("Loading tokenizer...")
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    
    train_dataset = ComplaintDataset(train_texts, train_labels, tokenizer)
    val_dataset = ComplaintDataset(val_texts, val_labels, tokenizer)

    print("Loading model...")
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=3
    )

    os.makedirs(MODEL_PATH, exist_ok=True)

    args = TrainingArguments(
        output_dir=MODEL_PATH,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir="./logs",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    print("Training started... (this will take 5-10 mins)")
    trainer.train()

    print("Saving model...")
    model.save_pretrained(MODEL_PATH)
    tokenizer.save_pretrained(MODEL_PATH)

    print("Evaluating...")
    preds = trainer.predict(val_dataset)
    pred_labels = preds.predictions.argmax(-1)
    reverse_labels = {v: k for k, v in LABELS.items()}
    y_true = [reverse_labels[l] for l in val_labels]
    y_pred = [reverse_labels[l] for l in pred_labels]
    print(classification_report(y_true, y_pred))
    print("✅ Training complete! Model saved to", MODEL_PATH)

if __name__ == "__main__":
    train()
