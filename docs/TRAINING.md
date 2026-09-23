# Training the pathogen dataset

## Dataset (already extracted)

Path: `ml/datasets/raw` — see also `ml/datasets/DATASET.md`

| Class | Images |
|-------|--------|
| Bacteria | ~7999 |
| Fungi | ~8000 |
| Healthy | ~8000 |
| Pests | ~7999 |
| Virus | ~3679 |

Source zip: `pathogen.zip` in the project root.

The app knowledge base, recommendation templates, and inference labels are aligned to these five classes.

## Quick start (Windows)

Double-click or run:

```bat
train_model.bat
```

Or manually:

```powershell
cd C:\Users\Viraj\Desktop\PlantPathogenDetection
.\.venv\Scripts\Activate.ps1

# Install PyTorch (CPU). Use CUDA wheels if you have an NVIDIA GPU.
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install scikit-learn pillow numpy

# Faster first run (800 images/class ≈ 4k total)
python ml\training\train_cnn.py --data ml\datasets\raw --out backend\models --arch resnet18 --epochs 6 --batch-size 32 --max-per-class 800 --workers 0
```

## Full dataset training (slower)

```powershell
python ml\training\train_cnn.py --data ml\datasets\raw --out backend\models --arch resnet18 --epochs 10 --batch-size 32 --max-per-class 0 --workers 0
```

Optional architectures: `resnet18`, `mobilenet_v3_small`, `efficientnet_b0`.

## Outputs

- `backend/models/resnet18_plantguard.pt` — best checkpoint
- `backend/models/production_cnn.pt` — alias used by the API
- `backend/models/production_cnn.meta.json` — metrics + labels

## After training

Restart the API so it loads the new CNN:

```powershell
cd backend
..\.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

**Note:** Predictions are visual symptom / category classification (Bacteria, Fungi, Healthy, Pests, Virus), not laboratory pathogen confirmation.
