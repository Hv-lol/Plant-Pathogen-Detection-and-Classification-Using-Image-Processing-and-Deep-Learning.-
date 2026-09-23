# Training the pathogen dataset

## Dataset

Source: [kanishk3813/pathogen-dataset](https://www.kaggle.com/datasets/kanishk3813/pathogen-dataset)
on Kaggle — see `ml/datasets/DATASET.md` for details and class balance.

The app's knowledge base, recommendation templates, and inference labels are
aligned to five classes: Bacteria, Fungi, Healthy, Pests, Virus.

## 1. Install dependencies

```bash
pip install -r ml/requirements.txt
```

This installs `torch`/`torchvision` in addition to what `backend/requirements.txt`
already covers. If you have an NVIDIA GPU, install the matching CUDA build of
PyTorch from https://pytorch.org/get-started/locally/ instead of the default
CPU wheels `ml/requirements.txt` pulls in.

## 2. Fetch the dataset

```bash
python ml/datasets/download.py
```

Downloads and extracts into `ml/datasets/raw/<Label>/` (`ImageFolder` layout).
Requires Kaggle credentials — see the script's docstring.

## 3. Train

Faster first run, to sanity-check the pipeline (≈800 images/class):

```bash
python ml/training/train_cnn.py --data ml/datasets/raw --out backend/models \
  --arch resnet18 --epochs 6 --batch-size 32 --max-per-class 800 --workers 0
```

Full dataset (slower, better accuracy):

```bash
python ml/training/train_cnn.py --data ml/datasets/raw --out backend/models \
  --arch resnet18 --epochs 10 --batch-size 32 --max-per-class 0 --workers 0
```

Optional architectures: `resnet18` (default), `mobilenet_v3_small`, `efficientnet_b0`.
On Windows, keep `--workers 0` to avoid multiprocessing DataLoader issues.

## Outputs

- `backend/models/<arch>_plantguard.pt` — best checkpoint (by validation macro F1)
- `backend/models/production_cnn.pt` — alias the API loads
- `backend/models/production_cnn.meta.json` — metrics, labels, per-epoch history

## After training

Restart the API so it loads the new CNN:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

`inference_engine.ensure_ready()` prefers `backend/models/production_cnn.pt` and
falls back to the sklearn bootstrap only when it's absent.

**Note:** Predictions are visual symptom / category classification (Bacteria, Fungi,
Healthy, Pests, Virus), not laboratory pathogen confirmation.
