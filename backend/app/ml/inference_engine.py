"""Inference for the pathogen-category dataset (Bacteria/Fungi/Healthy/Pests/Virus).

Prefers a trained CNN at backend/models/production_cnn.pt.
Falls back to a small sklearn bootstrap with the same 5 labels until CNN training completes.
"""

from __future__ import annotations

import json
import pickle
import random
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFilter
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.ml.dataset_labels import CLASS_LABELS, DATASET_CLAIM, DATASET_NOTE


def artifact_paths() -> tuple[Path, Path]:
    """Primary production artifact paths (CNN preferred; sklearn used as bootstrap)."""
    root = settings.model_root
    root.mkdir(parents=True, exist_ok=True)
    cnn = root / "production_cnn.pt"
    if cnn.exists():
        return cnn, root / "production_cnn.meta.json"
    return root / "sklearn_baseline.pkl", root / "sklearn_baseline.meta.json"


def sklearn_artifact_paths() -> tuple[Path, Path]:
    root = settings.model_root
    root.mkdir(parents=True, exist_ok=True)
    return root / "sklearn_baseline.pkl", root / "sklearn_baseline.meta.json"


def _synthetic_leaf(label_idx: int, size: int = 128, rng: random.Random | None = None) -> PILImage.Image:
    rng = rng or random.Random()
    img = PILImage.new("RGB", (size, size), (20, 80, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse((10, 10, size - 10, size - 10), fill=(34, 120, 45))
    label = CLASS_LABELS[label_idx]
    if label == "Healthy":
        for _ in range(8):
            x, y = rng.randint(20, size - 20), rng.randint(20, size - 20)
            draw.ellipse((x, y, x + 4, y + 4), fill=(40, 140, 50))
    elif label == "Bacteria":
        for _ in range(16):
            x, y = rng.randint(20, size - 30), rng.randint(20, size - 30)
            r = rng.randint(6, 14)
            draw.ellipse((x, y, x + r, y + r), fill=(180, 160, 40))
            draw.ellipse((x + 2, y + 2, x + r - 2, y + r - 2), fill=(90, 120, 40))
    elif label == "Fungi":
        for _ in range(18):
            x, y = rng.randint(20, size - 25), rng.randint(20, size - 25)
            r = rng.randint(4, 12)
            draw.ellipse((x, y, x + r, y + r), fill=(120, 80, 20))
    elif label == "Pests":
        for _ in range(25):
            x, y = rng.randint(15, size - 20), rng.randint(15, size - 20)
            draw.ellipse((x, y, x + 5, y + 5), fill=(25, 25, 20))
            draw.line((x, y, x + 8, y + 3), fill=(30, 30, 25), width=1)
    elif label == "Virus":
        for _ in range(30):
            x, y = rng.randint(15, size - 15), rng.randint(15, size - 15)
            draw.rectangle((x, y, x + 6, y + 4), fill=(160, 190, 70))
    return img


def extract_features(image: PILImage.Image) -> np.ndarray:
    img = image.convert("RGB").resize((64, 64))
    arr = np.asarray(img).astype(np.float32) / 255.0
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    hist_r, _ = np.histogram(r, bins=8, range=(0, 1), density=True)
    hist_g, _ = np.histogram(g, bins=8, range=(0, 1), density=True)
    hist_b, _ = np.histogram(b, bins=8, range=(0, 1), density=True)
    brown = float(np.mean((r > g + 0.05) & (r > 0.3)))
    dark = float(np.mean(gray < 0.25))
    green = float(np.mean((g > r) & (g > b)))
    yellow = float(np.mean((r > 0.4) & (g > 0.4) & (b < 0.35)))
    feats = np.concatenate(
        [
            [r.mean(), g.mean(), b.mean(), r.std(), g.std(), b.std(), gx, gy, brown, dark, green, yellow],
            hist_r,
            hist_g,
            hist_b,
        ]
    )
    return feats.astype(np.float32)


def bootstrap_model(samples_per_class: int = 50) -> Path:
    rng = random.Random(42)
    xs, ys = [], []
    for class_idx in range(len(CLASS_LABELS)):
        for _ in range(samples_per_class):
            img = _synthetic_leaf(class_idx, 128, rng)
            xs.append(extract_features(img))
            ys.append(class_idx)
    clf = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=600, random_state=42)),
        ]
    )
    clf.fit(np.stack(xs), np.array(ys))
    weight_path, meta_path = sklearn_artifact_paths()
    with weight_path.open("wb") as f:
        pickle.dump({"model": clf, "labels": CLASS_LABELS, "backend": "sklearn"}, f)
    meta_path.write_text(
        json.dumps(
            {
                "architecture": "LogisticRegression+handcrafted_features",
                "framework": "scikit-learn",
                "labels": CLASS_LABELS,
                "claim": DATASET_CLAIM,
                "note": DATASET_NOTE + " Temporary bootstrap until production_cnn.pt is trained.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return weight_path


def _try_import_torch():
    try:
        import torch
        from torchvision import models, transforms

        return torch, models, transforms
    except ImportError:
        return None


def _build_torch_model(torch_nn_module_factory, arch: str, num_classes: int):
    torch, models, _ = torch_nn_module_factory
    arch = (arch or "resnet18").lower()
    if arch == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=None)
        model.classifier[-1] = torch.nn.Linear(model.classifier[-1].in_features, num_classes)
        return model
    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[-1] = torch.nn.Linear(model.classifier[-1].in_features, num_classes)
        return model
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    return model


class InferenceEngine:
    def __init__(self) -> None:
        self._backend: str = "none"
        self._model: Any = None
        self._labels = list(CLASS_LABELS)
        self._ready = False
        self._arch = "unknown"
        self._img_size = 224
        self._mean = [0.485, 0.456, 0.406]
        self._std = [0.229, 0.224, 0.225]
        self._torch = None
        self._transforms = None

    def ensure_ready(self) -> bool:
        cnn_path = settings.model_root / "production_cnn.pt"
        mods = _try_import_torch()
        if cnn_path.exists() and mods is not None:
            torch, models, transforms = mods
            ckpt = torch.load(cnn_path, map_location="cpu", weights_only=True)
            labels = ckpt.get("labels", CLASS_LABELS)
            arch = ckpt.get("architecture", "resnet18")
            model = _build_torch_model(mods, arch, len(labels))
            model.load_state_dict(ckpt["state_dict"])
            model.eval()
            self._model = model
            self._labels = list(labels)
            self._arch = arch
            self._img_size = int(ckpt.get("img_size", 224))
            self._mean = ckpt.get("normalize_mean", self._mean)
            self._std = ckpt.get("normalize_std", self._std)
            self._torch = torch
            self._transforms = transforms
            self._backend = "torch"
            self._ready = True
            return True

        weight_path, _ = sklearn_artifact_paths()
        # Rebuild bootstrap if missing or trained on old label set
        need_bootstrap = not weight_path.exists()
        if weight_path.exists():
            with weight_path.open("rb") as f:
                ckpt = pickle.load(f)
            if list(ckpt.get("labels", [])) != list(CLASS_LABELS):
                need_bootstrap = True
        if need_bootstrap and settings.AUTO_BOOTSTRAP_MODEL:
            bootstrap_model()
        if not weight_path.exists():
            return False
        with weight_path.open("rb") as f:
            ckpt = pickle.load(f)
        self._model = ckpt["model"]
        self._labels = list(ckpt.get("labels", CLASS_LABELS))
        self._arch = "LogisticRegression+handcrafted_features"
        self._backend = "sklearn"
        self._ready = True
        return True

    @property
    def is_ready(self) -> bool:
        return self._ready

    def predict(self, image_bytes: bytes, top_k: int = 5) -> dict:
        if not self._ready and not self.ensure_ready():
            raise RuntimeError("MODEL_NOT_AVAILABLE")
        img = PILImage.open(BytesIO(image_bytes)).convert("RGB")
        top_k = min(top_k, len(self._labels))

        if self._backend == "torch":
            assert self._torch is not None and self._transforms is not None
            tfm = self._transforms.Compose(
                [
                    self._transforms.Resize((self._img_size, self._img_size)),
                    self._transforms.ToTensor(),
                    self._transforms.Normalize(self._mean, self._std),
                ]
            )
            tensor = tfm(img).unsqueeze(0)
            with self._torch.no_grad():
                logits = self._model(tensor)
                probs = self._torch.softmax(logits, dim=1)[0].cpu().numpy()
        else:
            feats = extract_features(img).reshape(1, -1)
            probs = self._model.predict_proba(feats)[0]

        order = np.argsort(-probs)[:top_k]
        predictions = [
            {"label": self._labels[i], "probability": float(probs[i]), "rank": rank + 1}
            for rank, i in enumerate(order)
        ]
        return {
            "predictions": predictions,
            "labels": self._labels,
            "architecture": self._arch,
            "claim": DATASET_CLAIM,
        }

    def gradcam(self, image_bytes: bytes, class_index: Optional[int] = None) -> np.ndarray:
        """Heatmap: Grad-CAM for CNN; atypical-region proxy for sklearn fallback."""
        img = PILImage.open(BytesIO(image_bytes)).convert("RGB")
        if self._backend == "torch" and self._torch is not None and self._transforms is not None:
            return self._torch_gradcam(img, class_index)
        arr = np.asarray(img).astype(np.float32) / 255.0
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        green = (g > r) & (g > b)
        atypical = (~green).astype(np.float32)
        heat = PILImage.fromarray((atypical * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
        cam = np.asarray(heat).astype(np.float32) / 255.0
        if cam.max() > 0:
            cam /= cam.max()
        return cam

    def _torch_gradcam(self, img: PILImage.Image, class_index: Optional[int]) -> np.ndarray:
        assert self._torch is not None and self._transforms is not None
        orig_size = img.size
        tfm = self._transforms.Compose(
            [
                self._transforms.Resize((self._img_size, self._img_size)),
                self._transforms.ToTensor(),
                self._transforms.Normalize(self._mean, self._std),
            ]
        )
        tensor = tfm(img).unsqueeze(0)
        tensor.requires_grad_(True)

        activations: list = []
        gradients: list = []

        def fwd_hook(_m, _i, o):
            activations.append(o)

        def bwd_hook(_m, _gi, go):
            gradients.append(go[0])

        target = None
        # Prefer last conv for ResNet / MobileNet / EfficientNet
        for name, module in self._model.named_modules():
            if isinstance(module, self._torch.nn.Conv2d):
                target = module
        if target is None:
            return np.zeros((orig_size[1], orig_size[0]), dtype=np.float32)

        h_f = target.register_forward_hook(fwd_hook)
        h_b = target.register_full_backward_hook(bwd_hook)
        logits = self._model(tensor)
        if class_index is None:
            class_index = int(logits.argmax(dim=1).item())
        self._model.zero_grad()
        logits[0, class_index].backward()
        h_f.remove()
        h_b.remove()

        act = activations[0][0].detach().cpu().numpy()
        grad = gradients[0][0].detach().cpu().numpy()
        weights = grad.mean(axis=(1, 2))
        cam = np.zeros(act.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += float(w) * act[i]
        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam /= cam.max()
        cam_img = PILImage.fromarray((cam * 255).astype(np.uint8)).resize(orig_size)
        return np.asarray(cam_img).astype(np.float32) / 255.0


inference_engine = InferenceEngine()


def estimate_severity(image_bytes: bytes) -> tuple[float, str]:
    img = PILImage.open(BytesIO(image_bytes)).convert("RGB")
    arr = np.asarray(img.resize((256, 256))).astype(np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lesion = ((r > g + 15) & (r > 80)) | ((r + g + b) / 3 < 50)
    score = float(lesion.mean() * 100.0)
    if score <= 10:
        label = "Low"
    elif score <= 30:
        label = "Moderate"
    elif score <= 60:
        label = "High"
    else:
        label = "Severe"
    return score, label


def overlay_heatmap(image_bytes: bytes, heatmap: np.ndarray) -> bytes:
    base = PILImage.open(BytesIO(image_bytes)).convert("RGBA")
    heat = PILImage.fromarray((heatmap * 255).astype(np.uint8)).resize(base.size)
    tint = PILImage.new("RGBA", base.size, (200, 40, 20, 0))
    alpha = heat.point(lambda p: int(p * 0.45))
    tint.putalpha(alpha)
    composed = PILImage.alpha_composite(base, tint).convert("RGB")
    out = BytesIO()
    composed.save(out, format="JPEG", quality=90)
    return out.getvalue()
