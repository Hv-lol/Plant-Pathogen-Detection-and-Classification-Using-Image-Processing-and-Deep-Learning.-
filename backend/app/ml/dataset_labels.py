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
        "description": (
            "Visual patterns consistent with bacterial plant disease symptoms. "
            "Bacterial infections typically enter through wounds, stomata, or "
            "natural openings and spread fastest in warm, wet, or humid conditions "
            "where water can splash or film across foliage."
        ),
        "symptoms": (
            "Water-soaked lesions that often look greasy or translucent when held "
            "to light; angular leaf spots bounded by veins; yellow chlorotic halos "
            "ringing lesions; bacterial ooze or crust in severe, wet conditions; "
            "wilting or vascular streaking on stems depending on host and pathogen."
        ),
        "cause": (
            "Visual association with bacterial infection patterns commonly linked to "
            "genera such as Xanthomonas, Pseudomonas, and Erwinia. This category "
            "reflects symptom appearance only—species confirmation requires lab "
            "testing (e.g., culturing, PCR, or serological assays)."
        ),
        "prevention": (
            "Practice field sanitation and tool disinfection between plants; avoid "
            "working or irrigating foliage while wet; source certified disease-free "
            "seed and transplants; rotate away from susceptible hosts; minimize "
            "wounding during pruning, staking, and harvest handling."
        ),
        "management_notes": (
            "Do not apply bactericides or copper products without local extension "
            "guidance—bacteria are not affected by fungicides, and misuse can "
            "encourage resistance. Remove and destroy heavily infected material "
            "rather than composting it on-site. Confirm with a plant clinic before "
            "acting on regulatory or high-value crop decisions."
        ),
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
        "description": (
            "Visual patterns consistent with fungal plant disease symptoms. Fungi "
            "make up the largest and most visually diverse category here, spanning "
            "leaf-spotting pathogens, blights, mildews, and rusts."
        ),
        "symptoms": (
            "Discrete or coalescing leaf spots, often with concentric rings; "
            "blighted or scorched-looking tissue; powdery white or downy grey-purple "
            "growth on leaf surfaces; rust-colored pustules; chlorosis and necrosis; "
            "visible fruiting bodies (specks or tufts) in advanced infections."
        ),
        "cause": (
            "Visual association with fungal symptom complexes commonly linked to "
            "genera such as Alternaria, Fusarium, Botrytis, and powdery- or "
            "downy-mildew fungi. Species identification is not inferred from image "
            "alone and typically requires spore or culture examination."
        ),
        "prevention": (
            "Improve airflow through pruning and wider plant spacing; water at the "
            "base rather than overhead to reduce prolonged leaf wetness; rotate "
            "crops away from the same fungal family; remove and dispose of infected "
            "debris rather than leaving it in the field."
        ),
        "management_notes": (
            "Fungicide choice, timing, and rotation (to avoid resistance) must "
            "follow local extension recommendations and product labels. Preventive "
            "applications are often more effective than curative ones once symptoms "
            "are widespread."
        ),
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
        "description": (
            "No conspicuous disease or pest damage patterns detected in the "
            "sampled image. This is a visual baseline, not a certificate of "
            "health—it simply means the photographed tissue did not present "
            "recognizable symptom patterns."
        ),
        "symptoms": (
            "Uniform coloration and leaf structure; intact margins without "
            "chewing or mining damage; no obvious lesions, mosaics, wilting, or "
            "chlorotic mottling; normal turgor and growth habit for the visible "
            "growth stage."
        ),
        "cause": None,
        "prevention": (
            "Continue routine scouting on a regular schedule—early infections and "
            "low-density pest pressure can be visually subtle or hidden on leaf "
            "undersides and lower canopy."
        ),
        "management_notes": (
            "A healthy visual class does not guarantee absence of latent or "
            "asymptomatic infection, soil-borne issues, or early-stage pest "
            "colonization. Re-check high-value plantings periodically rather than "
            "relying on a single scan."
        ),
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
        "description": (
            "Visual patterns consistent with insect or mite feeding and other "
            "pest injury, as distinct from pathogen-driven disease symptoms."
        ),
        "symptoms": (
            "Irregular chewing holes or ragged margins; fine stippling or "
            "speckling from piercing-sucking pests; winding mining trails within "
            "leaf tissue; skeletonized leaves with veins left intact; visible frass "
            "or webbing; curled, puckered, or distorted new growth."
        ),
        "cause": (
            "Visual association with pest injury patterns typical of common groups "
            "such as aphids, mites, leaf miners, caterpillars, and beetles. This "
            "model identifies damage patterns, not the pest species itself—look "
            "closer at the tissue or use a hand lens to confirm the culprit."
        ),
        "prevention": (
            "Scout regularly, including leaf undersides; encourage beneficial "
            "insects and natural predators; remove heavily infested material "
            "promptly; use physical barriers, traps, or row covers where "
            "practical before reaching for chemical controls."
        ),
        "management_notes": (
            "Identify the pest before treatment—damage type alone can be "
            "ambiguous, and the wrong control can harm beneficial insects "
            "without addressing the actual cause. Avoid broad-spectrum pesticide "
            "use without expert advice, especially near pollinators."
        ),
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
        "description": (
            "Visual patterns consistent with viral plant disease symptoms. Viral "
            "infections are systemic, meaning symptoms usually reflect a "
            "whole-plant condition rather than a localized lesion."
        ),
        "symptoms": (
            "Mosaic or mottled light/dark green patterning; vein clearing or "
            "vein-banding; leaf curling, crinkling, or narrowing (shoestring "
            "growth); overall stunting or reduced vigor; ringspots or line "
            "patterns depending on host and virus family."
        ),
        "cause": (
            "Visual association with viral symptom patterns typical of mosaic "
            "viruses, potyviruses, and related groups, frequently spread by "
            "insect vectors such as aphids or whiteflies. Molecular assays "
            "(e.g., ELISA or PCR) are required for virus confirmation."
        ),
        "prevention": (
            "Use certified virus-free planting material and resistant varieties "
            "where available; manage insect vectors proactively rather than "
            "reactively; remove and destroy infected plants promptly to limit "
            "spread; sanitize tools between plants, especially during pruning."
        ),
        "management_notes": (
            "There is generally no field 'cure' for viral infections once "
            "established—management focuses on prevention, vector control, and "
            "removing infection sources. Work with an extension agent to confirm "
            "diagnosis before removing high-value plants."
        ),
        "source_metadata": {
            "sources": [{"title": "Platform curated category profile", "type": "curated_seed"}],
            "claim_level": "visual_category",
            "dataset_label": "Virus",
        },
    },
]
