"""Fetch the pathogen dataset from Kaggle and lay it out as an
ImageFolder-compatible tree at ml/datasets/raw/<Label>, matching
backend/app/ml/dataset_labels.CLASS_LABELS exactly (Bacteria, Fungi,
Healthy, Pests, Virus).

Source: https://www.kaggle.com/datasets/kanishk3813/pathogen-dataset

Requires Kaggle credentials: either ~/.kaggle/kaggle.json or the
KAGGLE_USERNAME / KAGGLE_KEY environment variables. See
https://github.com/Kaggle/kagglehub#authenticate for setup.

Usage:
    pip install -r ml/requirements.txt
    python ml/datasets/download.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.ml.dataset_labels import CLASS_LABELS  # noqa: E402

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_class_dirs(root: Path) -> dict[str, Path]:
    """Map each CLASS_LABELS entry to the directory holding its images.

    Kaggle archives don't have a guaranteed layout (extra top-level
    folder, different casing, etc.), so this scans every directory under
    `root` and matches by name instead of assuming a fixed structure.
    """
    found: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        name = path.name.strip().lower()
        for label in CLASS_LABELS:
            if name == label.lower() and label not in found:
                found[label] = path
    return found


def link_or_copy(src: Path, dst: Path, hardlink: bool) -> None:
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if hardlink:
        try:
            os.link(src, dst)
            return
        except OSError:
            pass  # different volume, unsupported fs, etc. — fall back to copy
    shutil.copy2(src, dst)


def materialize(class_dirs: dict[str, Path], out_root: Path, hardlink: bool) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label, src_dir in class_dirs.items():
        images = sorted(p for p in src_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
        for img in images:
            link_or_copy(img, out_root / label / img.name, hardlink)
        counts[label] = len(images)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(REPO_ROOT / "ml" / "datasets" / "raw"))
    parser.add_argument(
        "--hardlink",
        action="store_true",
        help="Hardlink images from the Kaggle cache instead of copying (saves "
        "disk space; silently falls back to copying when that isn't possible).",
    )
    args = parser.parse_args()

    try:
        import kagglehub
    except ImportError:
        raise SystemExit("kagglehub is not installed. Run: pip install -r ml/requirements.txt")

    print("Downloading kanishk3813/pathogen-dataset from Kaggle (cached locally after the first run)...")
    cache_path = Path(kagglehub.dataset_download("kanishk3813/pathogen-dataset"))
    print(f"Kaggle cache: {cache_path}")

    class_dirs = find_class_dirs(cache_path)
    missing = [label for label in CLASS_LABELS if label not in class_dirs]
    if missing:
        raise SystemExit(
            f"Could not find a folder for these classes under {cache_path}: {missing}\n"
            f"Found: {sorted(class_dirs)}\n"
            "The dataset's internal layout may not match what this script expects — "
            "inspect the cache path above and adjust find_class_dirs() if needed."
        )

    out_root = Path(args.out)
    counts = materialize(class_dirs, out_root, args.hardlink)

    print(f"\nDataset ready at {out_root}:")
    for label in CLASS_LABELS:
        print(f"  {label:10s} {counts[label]:>6d} images")
    print(f"\nTotal: {sum(counts.values())} images across {len(CLASS_LABELS)} classes")
    print("\nNext: python ml/training/train_cnn.py --data ml/datasets/raw --out backend/models")


if __name__ == "__main__":
    main()
