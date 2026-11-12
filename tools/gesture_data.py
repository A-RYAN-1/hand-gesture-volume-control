"""Load the recorded hands in data/ as (label, [id, x, y] points), the shape the app's landmarks have."""
import gzip
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
SCALE = 1000  # landmarks are stored as fractions of the image; any common scale keeps the ratios


def load(name):
    """`name` is fit or test (the HaGRID splits) or a path to a file written by tools/record_landmarks.py."""
    path = DATA / f"hagrid-{name}.json.gz" if name in ("fit", "test") else Path(name)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        text = f.read()
    rows = json.loads(text) if text.lstrip().startswith("[") else [json.loads(l) for l in text.splitlines() if l.strip()]
    return [(r["label"], [[i, x * SCALE, y * SCALE] for i, (x, y) in enumerate(r["lm"])]) for r in rows]


def scores(predicted, labels, positive="fist"):
    """Precision, recall and the false positive rate for one class, from parallel lists."""
    tp = sum(p and l == positive for p, l in zip(predicted, labels))
    fp = sum(p and l != positive for p, l in zip(predicted, labels))
    fn = sum((not p) and l == positive for p, l in zip(predicted, labels))
    negatives = sum(l != positive for l in labels)
    return {
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "false_positive_rate": fp / negatives if negatives else 0.0,
        "tp": tp, "fp": fp, "fn": fn,
    }
