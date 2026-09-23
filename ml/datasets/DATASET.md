# Dataset

Source: [kanishk3813/pathogen-dataset](https://www.kaggle.com/datasets/kanishk3813/pathogen-dataset) on Kaggle.

Five visual symptom categories, matching `backend/app/ml/dataset_labels.CLASS_LABELS`:

| Class | Images (approx.) |
|-------|-------------------|
| Bacteria | ~7999 |
| Fungi | ~8000 |
| Healthy | ~8000 |
| Pests | ~7999 |
| Virus | ~3679 |

Virus is meaningfully smaller than the other four classes — `ml/training/train_cnn.py`
applies inverse-frequency class weighting to compensate, and evaluation reports
macro F1 alongside accuracy for that reason (see `docs/ML_PIPELINE.md`).

## Fetching it

```bash
pip install -r ml/requirements.txt
python ml/datasets/download.py
```

This downloads the dataset via `kagglehub` (cached locally after the first run —
needs Kaggle credentials, see the script's docstring) and writes it to
`ml/datasets/raw/<Label>/` in `ImageFolder` layout, which is what
`ml/training/train_cnn.py --data ml/datasets/raw` expects.

`ml/datasets/raw/` is gitignored: it's several GB of images, regenerated on
demand rather than committed.

## Scientific framing

As with the rest of the platform (`docs/ML_PIPELINE.md`), these labels are
**visual symptom categories**, not laboratory-confirmed pathogen identification.
A model trained on this dataset predicts "this looks bacterial/fungal/viral/pest
damage," not a confirmed species or strain.
