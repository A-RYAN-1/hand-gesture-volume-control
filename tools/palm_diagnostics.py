"""Print, per HaGRID label, the spread of candidate open-palm measurements on the fit split.

Used to choose what the open-palm classifier should measure: a good feature has the open-hand labels
(`palm`, `stop`, `stop_inverted`) apart from the rest. It reads only the fit split, never the test split.
Run in CI, not on the laptop.
"""
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from gestures import FINGERS, MIDDLE_MCP, WRIST, _distance  # noqa: E402
import gesture_data  # noqa: E402

NAMES = ("min_ext", "mean_ext", "thumb_reach", "thumb_ext", "tip_spread", "thumb_index_gap")


def measures(points):
    size = _distance(points, WRIST, MIDDLE_MCP)
    if size == 0:
        return None
    ext = []
    for tip, pip in FINGERS:
        to_pip = _distance(points, WRIST, pip)
        if to_pip == 0:
            return None
        ext.append(_distance(points, WRIST, tip) / to_pip)
    to_mcp = _distance(points, WRIST, 2)
    if to_mcp == 0:
        return None
    return (min(ext), sum(ext) / 4, _distance(points, 4, MIDDLE_MCP) / size,
            _distance(points, WRIST, 4) / to_mcp, _distance(points, 8, 20) / size,
            _distance(points, 4, 5) / size)


def quantile(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, math.floor(q * len(values)))]


def main():
    by_label = {}
    for label, points in gesture_data.load("fit"):
        m = measures(points)
        if m is not None:
            by_label.setdefault(label, []).append(m)
    print("per label: p10 / median / p90 of each measure")
    print(f"{'label':<16}{'n':>5}  " + "  ".join(f"{n:^22}" for n in NAMES))
    for label, rows in sorted(by_label.items()):
        cells = []
        for j in range(len(NAMES)):
            col = [r[j] for r in rows]
            cells.append(f"{quantile(col, 0.1):5.2f} {statistics.median(col):5.2f} {quantile(col, 0.9):5.2f}   ")
        print(f"{label:<16}{len(rows):>5}  " + "  ".join(cells))


if __name__ == "__main__":
    main()
