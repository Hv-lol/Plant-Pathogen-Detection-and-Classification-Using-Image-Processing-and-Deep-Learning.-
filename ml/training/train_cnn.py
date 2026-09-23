"""Train the pathogen visual-symptom CNN (Bacteria/Fungi/Healthy/Pests/Virus).

Produces backend/models/<arch>_plantguard.pt (best checkpoint by
validation macro F1), a production_cnn.pt alias, and
production_cnn.meta.json. backend/app/ml/inference_engine.py picks up
production_cnn.pt automatically on the next API restart — no code
changes needed after training.

Usage:
    python ml/datasets/download.py                 # fetch the dataset first
    python ml/training/train_cnn.py --data ml/datasets/raw --out backend/models \
        --arch resnet18 --epochs 6 --batch-size 32 --max-per-class 800 --workers 0

Optional architectures: resnet18, mobilenet_v3_small, efficientnet_b0.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, f1_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, models, transforms

REPO_ROOT = Path(__file__).resolve().parents[2]

IMG_SIZE = 224
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]


def build_model(arch: str, num_classes: int, pretrained: bool) -> tuple[nn.Module, str]:
    weights = "DEFAULT" if pretrained else None
    arch = (arch or "resnet18").lower()
    if arch == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=weights)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
    elif arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=weights)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
    else:
        arch = "resnet18"
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model, arch


def stratified_split(
    targets: list[int], num_classes: int, val_frac: float, test_frac: float, seed: int, max_per_class: int
) -> tuple[list[int], list[int], list[int]]:
    """Per-class shuffle + slice so every split sees every class, and no
    image (the dataset has no precomputed augmented duplicates) can leak
    across splits."""
    rng = random.Random(seed)
    by_class: dict[int, list[int]] = {c: [] for c in range(num_classes)}
    for idx, target in enumerate(targets):
        by_class[target].append(idx)

    train_idx, val_idx, test_idx = [], [], []
    for indices in by_class.values():
        rng.shuffle(indices)
        if max_per_class > 0:
            indices = indices[:max_per_class]
        n = len(indices)
        n_val = max(1, int(n * val_frac))
        n_test = max(1, int(n * test_frac))
        val_idx += indices[:n_val]
        test_idx += indices[n_val : n_val + n_test]
        train_idx += indices[n_val + n_test :]
    return train_idx, val_idx, test_idx


class TransformSubset(Dataset):
    """Shares one ImageFolder scan across train/val/test while applying a
    different transform (augmentation only belongs on the train split)."""

    def __init__(self, base: datasets.ImageFolder, indices: list[int], transform):
        self.base = base
        self.indices = indices
        self.transform = transform

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, i: int):
        path, target = self.base.samples[self.indices[i]]
        img = self.base.loader(path)
        return self.transform(img), target


def run_epoch(model, loader, device, optimizer=None, criterion=None):
    train = optimizer is not None
    model.train(train)
    all_preds: list[int] = []
    all_targets: list[int] = []
    total_loss = 0.0
    for images, targets in loader:
        images, targets = images.to(device), targets.to(device)
        with torch.set_grad_enabled(train):
            logits = model(images)
            loss = criterion(logits, targets)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        total_loss += loss.item() * images.size(0)
        all_preds += logits.argmax(1).detach().cpu().tolist()
        all_targets += targets.detach().cpu().tolist()
    avg_loss = total_loss / max(len(loader.dataset), 1)
    acc = accuracy_score(all_targets, all_preds)
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    return avg_loss, acc, macro_f1, all_targets, all_preds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default=str(REPO_ROOT / "ml" / "datasets" / "raw"))
    parser.add_argument("--out", default=str(REPO_ROOT / "backend" / "models"))
    parser.add_argument("--arch", default="resnet18", choices=["resnet18", "mobilenet_v3_small", "efficientnet_b0"])
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--max-per-class", type=int, default=0, help="0 = use all available images")
    parser.add_argument("--val-split", type=float, default=0.15)
    parser.add_argument("--test-split", type=float, default=0.15)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-pretrained", action="store_true", help="Train from random init instead of ImageNet weights"
    )
    args = parser.parse_args()

    data_root = Path(args.data)
    if not data_root.exists():
        raise SystemExit(
            f"{data_root} does not exist. Run ml/datasets/download.py first (or point "
            "--data at an ImageFolder-style dataset with Bacteria/Fungi/Healthy/Pests/Virus subfolders)."
        )

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    base = datasets.ImageFolder(str(data_root))
    labels = base.classes
    expected = ["Bacteria", "Fungi", "Healthy", "Pests", "Virus"]
    if labels != expected:
        print(
            f"Warning: dataset classes {labels} don't match the expected {expected}. "
            "backend/app/ml/dataset_labels.py assumes this exact label set."
        )

    train_tfm = transforms.Compose(
        [
            transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(NORM_MEAN, NORM_STD),
        ]
    )
    eval_tfm = transforms.Compose(
        [
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(NORM_MEAN, NORM_STD),
        ]
    )

    targets = [s[1] for s in base.samples]
    train_idx, val_idx, test_idx = stratified_split(
        targets, len(labels), args.val_split, args.test_split, args.seed, args.max_per_class
    )
    print(f"Split: {len(train_idx)} train / {len(val_idx)} val / {len(test_idx)} test")

    train_loader = DataLoader(
        TransformSubset(base, train_idx, train_tfm),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
    )
    val_loader = DataLoader(
        TransformSubset(base, val_idx, eval_tfm), batch_size=args.batch_size, shuffle=False, num_workers=args.workers
    )
    test_loader = DataLoader(
        TransformSubset(base, test_idx, eval_tfm), batch_size=args.batch_size, shuffle=False, num_workers=args.workers
    )

    # Inverse-frequency class weights: this dataset is imbalanced (the Virus
    # class has roughly half as many images as the other four), and
    # docs/ML_PIPELINE.md calls out not relying on plain accuracy here.
    train_targets = [targets[i] for i in train_idx]
    class_counts = np.bincount(train_targets, minlength=len(labels)).astype(np.float32)
    class_counts[class_counts == 0] = 1.0
    class_weights = torch.tensor(class_counts.sum() / (class_counts * len(labels)), dtype=torch.float32).to(device)

    model, arch = build_model(args.arch, len(labels), pretrained=not args.no_pretrained)
    model.to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / f"{arch}_plantguard.pt"
    best_macro_f1 = -1.0
    history = []

    for epoch in range(1, args.epochs + 1):
        start = time.time()
        train_loss, _, _, _, _ = run_epoch(model, train_loader, device, optimizer, criterion)
        val_loss, val_acc, val_f1, _, _ = run_epoch(model, val_loader, device, None, criterion)
        elapsed = time.time() - start
        print(
            f"epoch {epoch}/{args.epochs}  train_loss={train_loss:.4f}  "
            f"val_acc={val_acc:.4f}  val_macro_f1={val_f1:.4f}  ({elapsed:.0f}s)"
        )
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_accuracy": val_acc,
                "val_macro_f1": val_f1,
                "seconds": elapsed,
            }
        )
        if val_f1 > best_macro_f1:
            best_macro_f1 = val_f1
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "labels": labels,
                    "architecture": arch,
                    "img_size": IMG_SIZE,
                    "normalize_mean": NORM_MEAN,
                    "normalize_std": NORM_STD,
                },
                best_path,
            )

    # Evaluate the best checkpoint (not necessarily the last epoch) on the held-out test split.
    ckpt = torch.load(best_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["state_dict"])
    _, test_acc, test_f1, test_targets, test_preds = run_epoch(model, test_loader, device, None, criterion)
    report = classification_report(test_targets, test_preds, target_names=labels, digits=4, zero_division=0)
    print(f"\nTest accuracy={test_acc:.4f}  macro_f1={test_f1:.4f}\n{report}")

    production_path = out_dir / "production_cnn.pt"
    production_path.write_bytes(best_path.read_bytes())

    meta = {
        "architecture": arch,
        "labels": labels,
        "img_size": IMG_SIZE,
        "best_val_macro_f1": best_macro_f1,
        "test_accuracy": test_acc,
        "test_macro_f1": test_f1,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "max_per_class": args.max_per_class,
        "seed": args.seed,
        "dataset_root": str(data_root.resolve()),
        "artifact": str(best_path),
        "claim": "visual_symptom_classification",
        "history": history,
        "classification_report": report,
    }
    (out_dir / "production_cnn.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"\nSaved {best_path}\nSaved {production_path}\nSaved {out_dir / 'production_cnn.meta.json'}")
    print("Restart the API for it to load the new CNN.")


if __name__ == "__main__":
    main()
