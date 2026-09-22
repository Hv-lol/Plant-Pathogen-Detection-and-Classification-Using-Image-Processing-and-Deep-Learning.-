# PlantGuard AI — Research Methodology

## Goals

Provide a reproducible research workspace for dataset management, model training, evaluation, comparison, and governed promotion to production.

## Dataset documentation requirements

Each dataset version must record:

- Source and license
- Number of classes and images per class
- Resolution statistics
- Class distribution / imbalance notes
- Train / validation / test split methodology
- Checksum
- Creator and timestamp

## Data leakage prevention

Mandatory validation rules:

- Exact duplicate detection (checksum)
- Near-duplicate detection across splits
- No shared original photograph across train and test
- Augmented copies must not cross splits
- Documented split seed and protocol

## Experiment tracking

Every training run stores:

- Random seed
- Dataset version ID
- Code/git version (when available)
- Model architecture + hyperparameters
- Metrics JSON (including macro F1, per-class recall)
- Confusion matrix artifact
- Inference time and model size
- Status and timestamps

Preferred tooling: MLflow for experiment tracking; registry rows mirrored in PostgreSQL for product UI.

## Evaluation protocol

1. Hold out a fixed test set never used for tuning.
2. Tune on validation only.
3. Report macro and weighted F1 under imbalance.
4. Review misclassified samples before promotion.
5. Do not promote on accuracy alone.

## Model lifecycle

```
Development → Validation → Candidate → Approved → Production → Retired
```

Promotion requires recorded metrics, dataset version link, checksummed artifact, and (for production) admin/researcher approval with audit log entry.

## Reporting for papers / demos

Research dashboard must be able to export:

- Dataset description
- Augmentation policy
- Architecture and hyperparameters
- Metrics tables and confusion matrices
- Error analysis notes
- Reproducibility block (seeds + versions)
