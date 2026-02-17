from typing import List, Dict

# KNOWLEDGE BASE - EXPERT SYSTEM RULES
# Maps harmful ingredient names (lowercase) to safer alternatives and reasons.
SUBSTITUTION_MAP = {
    # SURFACTANTS (CLEANSERS)
    "sodium lauryl sulfate": {
        "risk": "Strong cleanser/Irritant",
        "alternatives": ["Sodium Cocoyl Isethionate", "Decyl Glucoside", "Coco-Glucoside"],
        "reason": "Gentler coconut-based cleansers that don't strip natural oils."
    },
    "sls": {
        "risk": "Strong cleanser/Irritant",
        "alternatives": ["Sodium Cocoyl Isethionate", "Decyl Glucoside", "Coco-Glucoside"],
        "reason": "Gentler coconut-based cleansers."
    },
    "ammonium lauryl sulfate": {
        "risk": "Harsh surfactant",
        "alternatives": ["Sodium Lauroyl Sarcosinate", "Sodium Methyl Cocoyl Taurate"],
        "reason": "Milder anionic surfactants."
    },

    # PRESERVATIVES
    "triclosan": {
        "risk": "Endocrine disruptor/Antibacterial",
        "alternatives": ["Zinc Citrate", "Tea Tree Oil", "Neem Extract"],
        "reason": "Natural or safer antimicrobial agents."
    },
    "paraben": { # Partial match key
        "risk": "Potential endocrine disruptor",
        "alternatives": ["Sodium Benzoate", "Potassium Sorbate", "Phenoxyethanol"],
        "reason": "Food-grade or milder preservatives."
    },
    "methylisothiazolinone": {
        "risk": "Strong Allergen",
        "alternatives": ["Benzyl Alcohol", "Sodium Benzoate"],
        "reason": "Lower sensitization risk preservatives."
    },
    "formaldehyde": {
         "risk": "Carcinogen",
         "alternatives": ["Sodium Benzoate", "Ethylhexylglycerin"],
         "reason": "Safe modern preservation systems."
    },

    # SILICONES (Build-up)
    "dimethicone": {
        "risk": "Build-up potential (insoluble)",
        "alternatives": ["Coco-Caprylate", "Broccoli Seed Oil", "Hemisqualane"],
        "reason": "Natural silicone alternatives that are biodegradable."
    },
    "cyclopentasiloxane": {
        "risk": "Environmental concern/Bioaccumulation",
        "alternatives": ["Coco-Caprylate/Caprate", "Dodecane"],
        "reason": "Eco-friendly volatile emollients."
    },

    # FRAGRANCE
    "fragrance": {
        "risk": "Undisclosed allergens",
        "alternatives": ["Essential Oils", "Natural Extracts", "Fragrance-Free"],
        "reason": "Transparency in ingredients."
    },
    "parfum": {
        "risk": "Undisclosed allergens",
        "alternatives": ["Essential Oils", "Natural Extracts"],
        "reason": "Transparency in ingredients."
    },
}

def get_recommendations(ingredients_list: List[Dict]) -> List[Dict]:
    """
    Analyzes a list of processed ingredients and returns recommendations
    for any harmful ingredients found.
    """
    recommendations = []
    
    for ing in ingredients_list:
        name_lower = ing['name'].lower()
        rec_data = None
        
        # 1. Exact Match Check
        if name_lower in SUBSTITUTION_MAP:
            rec_data = SUBSTITUTION_MAP[name_lower]
        
        # 2. Partial Match / Class Check (e.g. any "paraben")
        if not rec_data:
            for key in SUBSTITUTION_MAP:
                if key in name_lower and len(key) > 4: # Avoid short partials
                    rec_data = SUBSTITUTION_MAP[key]
                    break
        
        if rec_data:
            recommendations.append({
                "bad_ingredient": ing['name'],
                "risk_type": rec_data['risk'],
                "alternatives": rec_data['alternatives'],
                "reason": rec_data['reason']
            })
            
    return recommendations
