# PlantGuard AI — ML Pipeline

## Scientific framing

1. **Visual disease classification** — predicts disease/symptom classes from images.
2. **Pathogen identification** — only when training labels are pathogen-confirmed and documented.

UI, reports, and API fields must not conflate these claims.

## Inference pipeline

```
Raw image
  → Image validation (MIME, size, corruption)
  → Quality assessment (blur, lighting, resolution, leaf area)
  → Resize + color normalization (+ noise handling)
  → Plant/leaf detection gate
  → Disease classification
  → Confidence calibration
  → Explainability (Grad-CAM / Grad-CAM++)
  → Optional severity (lesion/leaf area)
  → Knowledge + sourced recommendations
  → Persist results
```

If quality status is `POOR`, inference is refused with actionable capture guidance.

Quality statuses: `GOOD` | `ACCEPTABLE` | `POOR` (score 0–100 + messages).

## Training pipeline

```
Dataset
  → Cleaning + label validation
  → Duplicate / near-duplicate detection
  → Class imbalance analysis
  → Leakage-safe train/val/test split
  → Augmentation (train only)
  → Baseline Custom CNN
  → ResNet50 / EfficientNet / MobileNet (+ optional ConvNeXt / ViT)
  → Hyperparameter tuning (Optuna)
  → Evaluation (macro F1 prioritized under imbalance)
  → Error analysis + misclassified review
  → Model registry + approval workflow
  → Production deployment
```

## Mandatory model experiments

| Model | Role |
|-------|------|
| Custom CNN | Baseline |
| ResNet50 | Strong CNN baseline |
| EfficientNet-B0/B2 | Efficiency/accuracy tradeoff |
| MobileNetV3 | Edge/mobile candidate |
| ConvNeXt / ViT | Optional advanced |

Compare: Accuracy, Precision, Recall, F1, Macro F1, Weighted F1, confusion matrix, per-class metrics, inference time, model size, memory.

Under class imbalance, **do not** select production models on accuracy alone.

## Explainability

- Grad-CAM and Grad-CAM++
- Optional segmentation overlay
- Plain-language disclaimer: highlights are regions that influenced the prediction; not pathogen proof

## Severity (when data supports it)

Configurable thresholds (example defaults): Low 0–10%, Moderate 11–30%, High 31–60%, Severe 61%+.  
Always labeled as an AI estimate.

## Recommendations

Deterministic retrieval from verified knowledge base keyed by disease + crop + severity (+ optional environment). Each recommendation carries source metadata. No unsafe chemical advice without verified, localized sources.

## Reproducibility

Store random seed, dataset version, code version, model version, hyperparameters, and metrics with every training run (see RESEARCH_METHODOLOGY.md).
