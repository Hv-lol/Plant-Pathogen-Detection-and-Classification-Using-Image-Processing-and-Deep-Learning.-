# Full-dataset training results

**Model:** ResNet-18 (ImageNet pretrained, fine-tuned)  
**Device:** CPU  
**Dataset:** `ml/datasets/raw` (Bacteria, Fungi, Healthy, Pests, Virus)  
**Split:** 27,997 train / 5,997 val / 6,003 test  
**Epochs:** 8  

## Validation (best checkpoint)

- Best val accuracy: **99.60%** (epoch 8)
- Best val macro F1: **99.60%**

## Held-out test set

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Bacteria | 0.999 | 0.995 | 0.997 |
| Fungi | 0.992 | 0.995 | 0.993 |
| Healthy | 0.994 | 0.990 | 0.992 |
| Pests | 0.992 | 0.996 | 0.994 |
| Virus | 0.998 | 0.998 | 0.998 |

- **Test accuracy:** 99.48%
- **Test macro F1:** 99.48%

## Scientific note

Outputs are **visual pathogen-category** predictions, not laboratory-confirmed species identification.

Artifact (local, not in git): `backend/models/production_cnn.pt`
