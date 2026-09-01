"""Lightweight duplicate/similar complaint detection.

Uses TF-IDF cosine similarity so the feature works without downloading another
large language model. This is intentionally a ranking signal, not an automatic
rejection: authorities still decide whether two complaints are duplicates.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ComplaintSimilarity:
    def __init__(self, threshold=0.55):
        self.threshold = threshold

    def find_similar(self, text, complaints, limit=5):
        candidates = [c for c in complaints if c.text]
        if not candidates or not text.strip():
            return []

        corpus = [text] + [c.text for c in candidates]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        ranked = sorted(zip(candidates, scores), key=lambda item: item[1], reverse=True)
        return [
            {"complaint": complaint, "score": round(float(score) * 100, 1)}
            for complaint, score in ranked[:limit]
            if score >= self.threshold
        ]
