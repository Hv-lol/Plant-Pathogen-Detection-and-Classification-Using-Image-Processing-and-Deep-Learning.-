from dataclasses import dataclass
from io import BytesIO
from typing import List

import numpy as np
from PIL import Image as PILImage, ImageStat, UnidentifiedImageError

from app.core.config import settings
from app.core.errors import AppError


@dataclass
class QualityResult:
    status: str
    score: float
    messages: List[str]
    width: int
    height: int


def assess_image_quality(data: bytes) -> QualityResult:
    try:
        img = PILImage.open(BytesIO(data))
        img.verify()
        img = PILImage.open(BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise AppError("INVALID_IMAGE", "Uploaded image is corrupt or unsupported.", 400) from exc

    width, height = img.size
    messages: list[str] = []
    score = 100.0

    if width < settings.MIN_IMAGE_WIDTH or height < settings.MIN_IMAGE_HEIGHT:
        messages.append("Resolution is below the recommended minimum.")
        score -= 35

    # Downsample for blur estimate performance
    small = img.resize((min(256, width), min(256, height)))
    gray = np.asarray(small.convert("L"))
    # Fast gradient-based sharpness proxy
    gx = np.abs(np.diff(gray.astype(np.float32), axis=1)).mean()
    gy = np.abs(np.diff(gray.astype(np.float32), axis=0)).mean()
    sharpness = float(gx + gy)
    if sharpness < 8:
        messages.append("Image appears blurry.")
        score -= 25

    stat = ImageStat.Stat(img)
    brightness = float(sum(stat.mean) / 3.0)
    if brightness < 45:
        messages.append("Image is too dark.")
        score -= 20
    elif brightness > 220:
        messages.append("Image is excessively bright.")
        score -= 20

    # Green vegetation presence heuristic
    arr = np.asarray(img.resize((128, 128))).astype(np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    green_ratio = float(np.mean((g > r) & (g > b)))
    if green_ratio < 0.08:
        messages.append("Insufficient visible leaf/plant area detected.")
        score -= 30

    score = max(0.0, min(100.0, score))
    if score < settings.QUALITY_POOR_THRESHOLD:
        status = "POOR"
    elif score < 70:
        status = "ACCEPTABLE"
    else:
        status = "GOOD"

    if not messages:
        messages.append("Image quality is suitable for analysis.")

    return QualityResult(status=status, score=score, messages=messages, width=width, height=height)
