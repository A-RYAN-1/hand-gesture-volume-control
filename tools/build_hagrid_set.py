"""Build the compact gesture evaluation set in data/ from HaGRID annotation files.

HaGRID (Kapitanov et al., https://github.com/hukenovs/hagrid, CC BY-SA 4.0) labels every hand in its photos
and gives MediaPipe's 21 landmarks for it, normalised to the image. This script keeps only the label and the
landmarks (rounded to 4 decimals), never an image, a user id or a box:

  data/hagrid-fit.json.gz   every hand of the `ann_subsample` split: thresholds are fitted on it
  data/hagrid-test.json.gz  a seeded sample of the `ann_test` split, reported once and never tuned on

Download the annotation JSON files from Kaggle (`kapitanov/hagrid`, folders `ann_subsample/` and `ann_test/`)
and run: python tools/build_hagrid_set.py <ann_subsample dir> <ann_test dir>
"""
import gzip
import json
import random
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data"
TEST_IMAGES_PER_CLASS = 150
SEED = 12


def hands(records):
    """(label, 21 [x, y] points) for every hand that has a full set of landmarks."""
    for rec in records:
        for label, lm in zip(rec.get("labels", []), rec.get("landmarks", [])):
            if lm and len(lm) == 21:
                yield label, [[round(x, 4), round(y, 4)] for x, y in lm]


def load(folder):
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(Path(folder).glob("*.json"))}


def write(name, rows):
    OUT.mkdir(exist_ok=True)
    with gzip.open(OUT / name, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump([{"label": label, "lm": lm} for label, lm in rows], f, separators=(",", ":"))
    counts = {}
    for label, _ in rows:
        counts[label] = counts.get(label, 0) + 1
    print(f"{name}: {len(rows)} hands, {len(counts)} labels")


def main(fit_dir, test_dir):
    fit = load(fit_dir)
    seen = {img for recs in fit.values() for img in recs}
    write("hagrid-fit.json.gz", [h for recs in fit.values() for h in hands(recs.values())])
    rng = random.Random(SEED)
    rows = []
    for _, recs in sorted(load(test_dir).items()):
        ids = sorted(i for i in recs if i not in seen)  # no photo is in both splits
        rows += hands(recs[i] for i in rng.sample(ids, min(TEST_IMAGES_PER_CLASS, len(ids))))
    write("hagrid-test.json.gz", rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
