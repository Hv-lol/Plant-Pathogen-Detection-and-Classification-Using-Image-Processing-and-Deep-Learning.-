"""Canonical labels for the pathogen.zip ImageFolder dataset.

Folder names under ml/datasets/raw must match CLASS_LABELS exactly
(ImageFolder sorts alphabetically):

  Bacteria / Fungi / Healthy / Pests / Virus
"""

CLASS_LABELS = [
    "Bacteria",
    "Fungi",
    "Healthy",
    "Pests",
    "Virus",
]

DATASET_CLAIM = "visual_pathogen_category_classification"
DATASET_NOTE = (
    "Model predicts broad visual symptom categories "
    "(bacterial-like, fungal-like, healthy, pest damage, viral-like). "
    "This is not laboratory-confirmed species-level pathogen identification."
)

# Curated knowledge entries keyed by label_key == CLASS_LABELS entry
CATEGORY_KNOWLEDGE = [
    {
        "name": "Bacterial disease symptoms",
        "slug": "bacteria",
        "label_key": "Bacteria",
        "pathogen_type": "bacteria",
        "pathogen_name": None,
        "description": "Visual patterns consistent with bacterial plant disease symptoms.",
        "symptoms": "Water-soaked lesions, angular spots, yellow halos, ooze in severe cases, wilting depending on host.",
        "cause": "Visual association with bacterial infection patterns; species confirmation requires lab testing.",
        "prevention": "Sanitation, avoid working wet foliage, use clean tools/seed where applicable, manage wounds.",
        "management_notes": "Do not apply bactericides without local expert guidance. Confirm with a plant clinic when stakes are high.",
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_category",
            "dataset_label": "Bacteria",
        },
    },
    {
        "name": "Fungal disease symptoms",
        "slug": "fungi",
        "label_key": "Fungi",
        "pathogen_type": "fungus",
        "pathogen_name": None,
        "description": "Visual patterns consistent with fungal plant disease symptoms.",
        "symptoms": "Leaf spots, blights, powdery/downy growth, chlorosis, necrosis, fruiting structures in some cases.",
        "cause": "Visual association with fungal symptom complexes; species ID is not inferred from image alone.",
        "prevention": "Improve airflow, reduce prolonged leaf wetness, rotate crops, remove infected debris.",
        "management_notes": "Fungicide decisions must follow local extension recommendations and product labels.",
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_category",
            "dataset_label": "Fungi",
        },
    },
    {
        "name": "Healthy plant tissue",
        "slug": "healthy",
        "label_key": "Healthy",
        "pathogen_type": None,
        "pathogen_name": None,
        "description": "No conspicuous disease or pest damage patterns detected in the sampled image.",
        "symptoms": "Uniform coloration and structure without obvious lesions, chlorotic mosaics, or feeding damage.",
        "cause": None,
        "prevention": "Continue scouting; early infections can be visually subtle.",
        "management_notes": "A healthy visual class does not guarantee absence of latent infection.",
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_class",
            "dataset_label": "Healthy",
        },
    },
    {
        "name": "Pest damage symptoms",
        "slug": "pests",
        "label_key": "Pests",
        "pathogen_type": "pest",
        "pathogen_name": None,
        "description": "Visual patterns consistent with insect or mite feeding / pest injury.",
        "symptoms": "Chewing holes, stippling, mining trails, skeletonizing, frass, distorted tissue.",
        "cause": "Visual association with pest injury; pest species is not identified by this model.",
        "prevention": "Scout regularly, encourage beneficials, remove heavily infested material, use barriers where practical.",
        "management_notes": "Identify the pest before treatment. Avoid broad pesticide use without expert advice.",
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_category",
            "dataset_label": "Pests",
        },
    },
    {
        "name": "Viral disease symptoms",
        "slug": "virus",
        "label_key": "Virus",
        "pathogen_type": "virus",
        "pathogen_name": None,
        "description": "Visual patterns consistent with viral plant disease symptoms.",
        "symptoms": "Mosaic mottling, vein clearing, leaf curling/distortion, stunting, ringspots depending on host.",
        "cause": "Visual association with viral symptom patterns; molecular assays are required for virus confirmation.",
        "prevention": "Use clean planting material, manage insect vectors, remove infected plants, sanitize tools.",
        "management_notes": "There is generally no field 'cure' for viruses; focus on prevention and vector management with expert support.",
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_category",
            "dataset_label": "Virus",
        },
    },
]
