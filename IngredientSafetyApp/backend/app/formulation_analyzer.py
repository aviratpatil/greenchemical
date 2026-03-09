"""
Formulation-level cosmetic safety analyzer.
Implements the expert system prompt logic as a rule-based engine.
Returns structured JSON matching the agreed output schema.
"""

from __future__ import annotations
import re
from typing import List, Optional

# ---------------------------------------------------------------------------
# REGULATORY KNOWLEDGE BASE
# ---------------------------------------------------------------------------

# Structure:
#   name_key (lowercase) -> {
#       "function": str,
#       "eu_status": "allowed" | "restricted" | "banned",
#       "eu_limit_pct": float | None,          # max % in finished product
#       "eu_limit_note": str,
#       "usage_type_concern": dict,             # keyed by usage type
#       "groups_concern": list[str],            # e.g. ["children_under_3"]
#       "sensitizer": bool,
#       "formaldehyde_releaser": bool,
#       "paraben": bool,
#       "base_verdict": str                     # SAFE | CAUTION | FLAG | BANNED_IN_CONTEXT
#   }

INGREDIENT_DB: dict = {
    "aqua": {
        "function": "Solvent",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "water": {
        "function": "Solvent",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "sodium lauryl sulfate": {
        "function": "Primary surfactant (anionic)",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No EU concentration limit; CIR advises rinse-off use. Caution in leave-on.",
        "usage_type_concern": {
            "leave-on": "CIR recommends avoidance in leave-on products due to skin irritation potential.",
        },
        "groups_concern": ["sensitive_skin"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "sls": {
        "function": "Primary surfactant (anionic)",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No EU concentration limit; CIR advises rinse-off use.",
        "usage_type_concern": {
            "leave-on": "CIR recommends avoidance in leave-on products.",
        },
        "groups_concern": ["sensitive_skin"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "sodium laureth sulfate": {
        "function": "Primary surfactant (anionic, ethoxylated)",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted. May contain 1,4-dioxane trace impurity — EU requires minimisation.",
        "usage_type_concern": {
            "leave-on": "Irritation risk in leave-on; rinse-off preferred.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "sles": {
        "function": "Primary surfactant (anionic, ethoxylated)",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted. 1,4-dioxane impurity risk — EU requires minimisation.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "ammonium lauryl sulfate": {
        "function": "Primary surfactant (anionic)",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted in rinse-off. CIR cautions leave-on use.",
        "usage_type_concern": {
            "leave-on": "Not recommended per CIR.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "cocamidopropyl betaine": {
        "function": "Amphoteric co-surfactant",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted. SCCS (2012): safe in rinse-off and leave-on at typical concentrations.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
        "sensitizer_note": "Sensitization risk arises from impurities (amidoamine, DMAPA), not CAPB itself. Low risk in high-purity grade.",
    },
    "capb": {
        "function": "Amphoteric co-surfactant",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted. Mitigates SLS irritation.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "glycerin": {
        "function": "Humectant / conditioner",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "glycerol": {
        "function": "Humectant / conditioner",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "methylparaben": {
        "function": "Preservative (EU Annex V, entry 12)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.4,
        "eu_limit_note": "Max 0.4% solo; total all parabens ≤ 0.8%. Mixture rules apply when combined with other parabens.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "CAUTION",
    },
    "propylparaben": {
        "function": "Preservative (EU Annex V, entry 14)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.14,
        "eu_limit_note": "Max 0.14% — strictest individual paraben limit in EU. Not for use on children <3 or nappy area. Combined with butylparaben: also ≤ 0.14%.",
        "usage_type_concern": {},
        "groups_concern": ["children_under_3"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "CAUTION",
    },
    "butylparaben": {
        "function": "Preservative (EU Annex V, entry 15)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.14,
        "eu_limit_note": "Max 0.14% combined with propylparaben. Banned in children <3 and nappy/intimate area products.",
        "usage_type_concern": {},
        "groups_concern": ["children_under_3"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "FLAG",
    },
    "ethylparaben": {
        "function": "Preservative (EU Annex V)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.4,
        "eu_limit_note": "Max 0.4% solo; total parabens ≤ 0.8%.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "CAUTION",
    },
    "isobutylparaben": {
        "function": "Preservative",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in EU (Regulation 358/2014). Not permitted in any cosmetic product.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "isopropylparaben": {
        "function": "Preservative",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in EU (Regulation 358/2014).",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "phenylparaben": {
        "function": "Preservative",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in EU.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": True,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "phenoxyethanol": {
        "function": "Preservative (EU Annex V, entry 29)",
        "eu_status": "restricted",
        "eu_limit_pct": 1.0,
        "eu_limit_note": "Max 1.0% in all product types. SCCS (2016) confirmed safe at ≤1%.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "dmdm hydantoin": {
        "function": "Preservative — formaldehyde releaser (EU Annex V, entry 35)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.6,
        "eu_limit_note": "Max 0.6% (≤0.1% free formaldehyde released). Mandatory label: 'contains formaldehyde' if released HCHO >0.05%.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": True,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "quaternium-15": {
        "function": "Preservative — formaldehyde releaser",
        "eu_status": "restricted",
        "eu_limit_pct": 0.2,
        "eu_limit_note": "Max 0.2% (as released formaldehyde). Mandatory 'contains formaldehyde' label above 0.05% released HCHO.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": True,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "imidazolidinyl urea": {
        "function": "Preservative — formaldehyde releaser",
        "eu_status": "restricted",
        "eu_limit_pct": 0.6,
        "eu_limit_note": "Max 0.6% with mandatory formaldehyde label above 0.05% released HCHO.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": True,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "diazolidinyl urea": {
        "function": "Preservative — formaldehyde releaser",
        "eu_status": "restricted",
        "eu_limit_pct": 0.5,
        "eu_limit_note": "Max 0.5%. Mandatory formaldehyde label above threshold.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": True,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "fragrance": {
        "function": "Scent (undisclosed blend)",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "EU Regulation 2023/1545: individual allergens ≥0.01% (rinse-off) or ≥0.001% (leave-on) must be declared. Effective August 2025.",
        "usage_type_concern": {
            "leave-on": "Lower allergen disclosure threshold: ≥0.001% triggers mandatory per-allergen listing.",
        },
        "groups_concern": ["sensitive_skin"],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "parfum": {
        "function": "Scent (undisclosed blend)",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "EU Regulation 2023/1545: per-allergen declaration required. Effective August 2025.",
        "usage_type_concern": {
            "leave-on": "Stricter allergen disclosure threshold applies.",
        },
        "groups_concern": ["sensitive_skin"],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "citric acid": {
        "function": "pH adjuster",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction at pH-adjustment concentrations.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "sodium chloride": {
        "function": "Viscosity modifier / electrolyte",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "retinol": {
        "function": "Active — Vitamin A (anti-ageing)",
        "eu_status": "restricted",
        "eu_limit_pct": 0.3,
        "eu_limit_note": "EU SCCS (2022): max 0.3% in face/body leave-on; 0.05% in hand creams. Not recommended for children <3. Labelling: 'Not for children'.",
        "usage_type_concern": {
            "leave-on": "Max 0.3% (face/body). Mandatory 'not for children' label.",
            "rinse-off": "Not typically meaningful in rinse-off; very short contact time.",
        },
        "groups_concern": ["children_under_3", "pregnant"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "salicylic acid": {
        "function": "Keratolytic / exfoliant / anti-dandruff",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Rinse-off hair: max 3%. Leave-on: max 2%. Face/body leave-on: max 2%. Not for children <3.",
        "usage_type_concern": {
            "rinse-off": "Max 3% in hair rinse-off products.",
            "leave-on": "Max 2% in leave-on products.",
        },
        "groups_concern": ["children_under_3"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "titanium dioxide": {
        "function": "UV filter / opacifier / colorant",
        "eu_status": "restricted",
        "eu_limit_pct": 25.0,
        "eu_limit_note": "BANNED in powder/aerosol/spray form (EU 2021 — carcinogen cat 2 by inhalation). Permitted in non-spray leave-on and rinse-off up to 25% UV filter.",
        "usage_type_concern": {
            "aerosol": "BANNED — carcinogen by inhalation (SCCS, IARC).",
            "spray": "BANNED — carcinogen by inhalation.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "glycolic acid": {
        "function": "AHA exfoliant",
        "eu_status": "restricted",
        "eu_limit_pct": 10.0,
        "eu_limit_note": "Max 10% at pH ≥3.5 (leave-on, professional). Consumer leave-on: max 10% with pH ≥3.5 and mandatory sun protection advice.",
        "usage_type_concern": {
            "leave-on": "Mandatory label: 'use sun protection; increased UV sensitivity'.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "lactic acid": {
        "function": "AHA exfoliant / humectant",
        "eu_status": "restricted",
        "eu_limit_pct": 10.0,
        "eu_limit_note": "Same AHA rules as glycolic acid.",
        "usage_type_concern": {
            "leave-on": "Mandatory sun protection labeling.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "sodium benzoate": {
        "function": "Preservative",
        "eu_status": "restricted",
        "eu_limit_pct": 0.5,
        "eu_limit_note": "Max 0.5% as preservative in cosmetics.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "potassium sorbate": {
        "function": "Preservative",
        "eu_status": "restricted",
        "eu_limit_pct": 0.6,
        "eu_limit_note": "Max 0.6% (as sorbic acid) in cosmetics.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "methylisothiazolinone": {
        "function": "Preservative",
        "eu_status": "banned",
        "eu_limit_pct": None,
        "eu_limit_note": "BANNED in leave-on products (EU 2016/1198). Max 0.0015% in rinse-off only.",
        "usage_type_concern": {
            "leave-on": "BANNED in leave-on products in EU.",
        },
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "mit": {
        "function": "Preservative",
        "eu_status": "banned",
        "eu_limit_pct": None,
        "eu_limit_note": "BANNED in leave-on (EU). Max 0.0015% rinse-off only.",
        "usage_type_concern": {
            "leave-on": "BANNED in EU leave-on products.",
        },
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "methylchloroisothiazolinone": {
        "function": "Preservative (often with MIT)",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Max 0.0015% (as 3:1 mixture with MIT) in rinse-off only.",
        "usage_type_concern": {
            "leave-on": "BANNED in EU leave-on products.",
        },
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "triclosan": {
        "function": "Antimicrobial",
        "eu_status": "restricted",
        "eu_limit_pct": 0.3,
        "eu_limit_note": "Restricted to specific product types (toothpaste, face wash, deodorant) at ≤0.3%. Banned in hand soaps in US FDA (2016).",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "talc": {
        "function": "Absorbent / filler",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Banned in aerosols for children <3 (EU). Must be asbestos-free. IARC Group 2A (inhaled talc).",
        "usage_type_concern": {
            "aerosol": "Banned in aerosol form for children under 3.",
        },
        "groups_concern": ["children_under_3"],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "formaldehyde": {
        "function": "Preservative / nail hardener",
        "eu_status": "restricted",
        "eu_limit_pct": 0.2,
        "eu_limit_note": "Max 0.2% in finished products (as biocide). BANNED as nail hardener above 2.2%. Mandatory 'contains formaldehyde' label. IARC Group 1 carcinogen.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": True,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "hydroquinone": {
        "function": "Skin-lightening agent",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in consumer cosmetics in EU. Still allowed in US (OTC) at ≤2%.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "lead acetate": {
        "function": "Progressive hair colorant",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in EU. FDA banned in 2018 in US for hair products.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "oxybenzone": {
        "function": "UV filter (chemical sunscreen)",
        "eu_status": "restricted",
        "eu_limit_pct": 2.2,
        "eu_limit_note": "Max 2.2% EU (revised 2022, down from 10%). Suspected endocrine disruptor. Hawaii/Palau banned in reef sunscreens.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "benzophenone-3": {
        "function": "UV filter / stabilizer",
        "eu_status": "restricted",
        "eu_limit_pct": 2.2,
        "eu_limit_note": "Max 2.2% as UV filter. Same as oxybenzone.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "dimethicone": {
        "function": "Silicone / emollient",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "Permitted. No specific EU limit.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "cyclopentasiloxane": {
        "function": "Cyclic silicone / volatile emollient",
        "eu_status": "restricted",
        "eu_limit_pct": 0.1,
        "eu_limit_note": "Restricted to ≤0.1% in wash-off products (EU 2018/1516 — PBT substance). Permitted with limits in leave-on.",
        "usage_type_concern": {
            "rinse-off": "Max 0.1% in wash-off products (EU PBT restriction).",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "d5": {
        "function": "Cyclic silicone",
        "eu_status": "restricted",
        "eu_limit_pct": 0.1,
        "eu_limit_note": "Max 0.1% in rinse-off products (PBT restriction).",
        "usage_type_concern": {
            "rinse-off": "Max 0.1% in rinse-off (EU).",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "niacinamide": {
        "function": "Vitamin B3 / brightening active",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction. Well-tolerated at 2–10%.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "hyaluronic acid": {
        "function": "Humectant / skin hydrator",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "sodium hyaluronate": {
        "function": "Humectant / hydrating active",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No restriction.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "zinc oxide": {
        "function": "UV filter / skin protectant",
        "eu_status": "restricted",
        "eu_limit_pct": 25.0,
        "eu_limit_note": "Max 25% as UV filter (non-spray). Not for inhalation (sprays) for SCCS review.",
        "usage_type_concern": {
            "aerosol": "Risk of inhalation; SCCS under review for spray formats.",
        },
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "ethylhexylglycerin": {
        "function": "Preservative booster / emollient",
        "eu_status": "allowed",
        "eu_limit_pct": None,
        "eu_limit_note": "No specific limit. Used as co-preservative with phenoxyethanol.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "SAFE",
    },
    "benzyl alcohol": {
        "function": "Preservative / solvent",
        "eu_status": "restricted",
        "eu_limit_pct": 1.0,
        "eu_limit_note": "Max 1% as preservative (Annex V). Also a listed fragrance allergen — must be declared ≥0.001% leave-on, ≥0.01% rinse-off.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "linalool": {
        "function": "Fragrance component",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Listed EU fragrance allergen. Declare if ≥0.001% leave-on; ≥0.01% rinse-off.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "limonene": {
        "function": "Fragrance component",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Listed EU fragrance allergen. Declare if ≥0.001% leave-on; ≥0.01% rinse-off.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "cinnamal": {
        "function": "Fragrance component",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "High-priority EU allergen. Declare at ≥0.001% leave-on; ≥0.01% rinse-off.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "eugenol": {
        "function": "Fragrance component",
        "eu_status": "restricted",
        "eu_limit_pct": None,
        "eu_limit_note": "Listed EU allergen. Mandatory declaration at threshold.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "cocamide dea": {
        "function": "Surfactant / foam booster",
        "eu_status": "banned",
        "eu_limit_pct": 0.0,
        "eu_limit_note": "BANNED in EU cosmetics (Commission Decision 2014/842). Potential nitrosamine precursor.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "BANNED_IN_CONTEXT",
    },
    "tea": {
        "function": "Surfactant / pH adjuster (Triethanolamine)",
        "eu_status": "restricted",
        "eu_limit_pct": 2.5,
        "eu_limit_note": "Max 2.5% in EU (nitrosamine precursor risk). Cannot be used with nitrosating agents.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "triethanolamine": {
        "function": "pH adjuster / surfactant",
        "eu_status": "restricted",
        "eu_limit_pct": 2.5,
        "eu_limit_note": "Max 2.5% (nitrosamine risk). Not with nitrosating agents.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
    "p-phenylenediamine": {
        "function": "Permanent hair dye oxidative base",
        "eu_status": "restricted",
        "eu_limit_pct": 2.0,
        "eu_limit_note": "Max 2% (as free base, oxidative hair dye only). Mandatory allergen warning labels. Strong sensitizer.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "ppd": {
        "function": "Permanent hair dye oxidative base",
        "eu_status": "restricted",
        "eu_limit_pct": 2.0,
        "eu_limit_note": "Max 2%. Mandatory sensitization warnings.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": True,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "FLAG",
    },
    "hydrogen peroxide": {
        "function": "Oxidising agent / bleaching agent",
        "eu_status": "restricted",
        "eu_limit_pct": 12.0,
        "eu_limit_note": "Max 12% in hair products. Max 6% in nail products. Max 4% tooth whitening. Mandatory warning labels.",
        "usage_type_concern": {},
        "groups_concern": [],
        "sensitizer": False,
        "formaldehyde_releaser": False,
        "paraben": False,
        "base_verdict": "CAUTION",
    },
}

# ---------------------------------------------------------------------------
# COMBINATION RULES ENGINE
# ---------------------------------------------------------------------------

COMBINATION_RULES = [
    {
        "ingredients": ["sodium lauryl sulfate", "sls", "ammonium lauryl sulfate"],
        "mitigators": ["cocamidopropyl betaine", "capb"],
        "type": "BENEFICIAL",
        "alert": (
            "SLS + Cocamidopropyl Betaine: CAPB forms mixed micelles with SLS, "
            "significantly reducing skin and eye irritation. This is a positive, "
            "intentional formulation synergy (CIR, SCCS confirmed)."
        ),
    },
    {
        "ingredients": ["dmdm hydantoin", "quaternium-15", "imidazolidinyl urea",
                        "diazolidinyl urea", "formaldehyde"],
        "mitigators": [],
        "type": "HARMFUL",
        "alert": (
            "Multiple formaldehyde releasers detected. Additive formaldehyde release "
            "significantly increases free HCHO concentration, amplifying sensitization "
            "and irritation risk. Each additional releaser multiplies allergic contact "
            "dermatitis probability."
        ),
        "min_count": 2,
    },
    {
        "ingredients": ["dmdm hydantoin", "quaternium-15", "imidazolidinyl urea",
                        "diazolidinyl urea", "formaldehyde"],
        "mitigators": [],
        "co_triggers": ["fragrance", "parfum"],
        "type": "HARMFUL",
        "alert": (
            "Formaldehyde releaser + Fragrance: Free formaldehyde released can react "
            "with aldehyde-containing fragrance components, amplifying contact "
            "sensitization risk and increasing the probability of allergic contact "
            "dermatitis in fragrance-sensitized individuals."
        ),
    },
    {
        "ingredients": ["retinol"],
        "co_triggers": ["glycolic acid", "lactic acid", "salicylic acid",
                        "citric acid", "aha", "bha"],
        "mitigators": [],
        "type": "HARMFUL",
        "alert": (
            "Retinol + AHA/BHA: Combined use compounds photosensitization, accelerates "
            "skin barrier disruption, and increases UV damage risk. EU and CIR recommend "
            "avoiding high-concentration combinations in leave-on products."
        ),
    },
    {
        "ingredients": ["methylparaben", "ethylparaben", "propylparaben",
                        "butylparaben", "isobutylparaben", "isopropylparaben"],
        "mitigators": [],
        "type": "REGULATORY",
        "alert": (
            "Multiple parabens: EU mixture concentration rules apply. Total all parabens "
            "≤ 0.8%. Propylparaben individually ≤ 0.14% regardless of total. "
            "Butylparaben + propylparaben combined ≤ 0.14%. Unknown concentrations make "
            "compliance unverifiable — concentration-dependent regulatory risk."
        ),
        "min_count": 2,
    },
    {
        "ingredients": ["phenoxyethanol", "methylparaben", "propylparaben",
                        "ethylparaben", "butylparaben", "dmdm hydantoin",
                        "quaternium-15", "imidazolidinyl urea", "diazolidinyl urea",
                        "methylisothiazolinone", "mit", "benzyl alcohol",
                        "sodium benzoate", "potassium sorbate"],
        "mitigators": [],
        "type": "CAUTION",
        "alert": (
            "Excessive preservative load: 3+ distinct preservatives detected in a single "
            "formulation. While each may be individually compliant, cumulative sensitization "
            "burden increases. Formulation rationality should be reviewed — is each "
            "preservative necessary?"
        ),
        "min_count": 3,
    },
    {
        "ingredients": ["triethanolamine", "tea"],
        "co_triggers": ["dmdm hydantoin", "quaternium-15", "imidazolidinyl urea"],
        "mitigators": [],
        "type": "HARMFUL",
        "alert": (
            "Triethanolamine (TEA) + Formaldehyde Releaser: TEA is a secondary amine "
            "that can react with released formaldehyde to form carcinogenic nitrosamines "
            "under certain conditions. This combination should be avoided."
        ),
    },
    {
        "ingredients": ["methylisothiazolinone", "mit", "methylchloroisothiazolinone"],
        "mitigators": [],
        "type": "HARMFUL",
        "alert": (
            "Isothiazolinone preservatives (MIT/CMIT): These are among the most potent "
            "contact allergens in cosmetics. Any combination or high concentration "
            "significantly elevates sensitization risk. MIT is banned in EU leave-on products."
        ),
        "min_count": 1,
    },
    {
        "ingredients": ["sodium laureth sulfate", "sles"],
        "co_triggers": ["triethanolamine", "tea", "diethanolamine", "dea"],
        "mitigators": [],
        "type": "HARMFUL",
        "alert": (
            "SLES + Amine (TEA/DEA): Ethoxylated surfactants combined with secondary "
            "amines can form N-nitrosoamines under certain pH/temperature conditions. "
            "EU restricts TEA to ≤2.5% for this reason."
        ),
    },
]

# ---------------------------------------------------------------------------
# GROUP & USAGE TYPE CONTEXT
# ---------------------------------------------------------------------------

GROUP_LABELS = {
    "children_under_3": "children under 3",
    "sensitive_skin": "sensitive skin users",
    "pregnant": "pregnant women",
}

# Classify product type to usage type
RINSE_OFF_KEYWORDS = ["shampoo", "conditioner rinse", "body wash", "face wash",
                      "cleanser", "shower gel", "hand wash", "rinse"]
LEAVE_ON_KEYWORDS = ["cream", "serum", "lotion", "moisturizer", "face cream",
                     "eye cream", "lip", "deodorant", "foundation", "primer",
                     "leave-in", "leave-on", "sunscreen", "toner", "essence"]
AEROSOL_KEYWORDS = ["spray", "aerosol", "mist", "dry shampoo"]


def classify_usage_type(product_type: str) -> str:
    pt = product_type.lower()
    for kw in AEROSOL_KEYWORDS:
        if kw in pt:
            return "aerosol"
    for kw in RINSE_OFF_KEYWORDS:
        if kw in pt:
            return "rinse-off"
    for kw in LEAVE_ON_KEYWORDS:
        if kw in pt:
            return "leave-on"
    return "unknown"


# ---------------------------------------------------------------------------
# LOOKUP HELPER
# ---------------------------------------------------------------------------

def _lookup(name: str) -> Optional[dict]:
    key = name.strip().lower()
    if key in INGREDIENT_DB:
        return INGREDIENT_DB[key]
    # Partial match (e.g. "sodium lauryl sulfate" inside "sodium lauryl sulfate (sls)")
    for db_key, data in INGREDIENT_DB.items():
        if db_key in key or key in db_key:
            return data
    return None


# ---------------------------------------------------------------------------
# MAIN ANALYSIS FUNCTION
# ---------------------------------------------------------------------------

def analyze_formulation(
    ingredient_list: List[str],
    product_type: str,
    region: str,
    target_group: str,
    known_concentrations: Optional[dict] = None,
) -> dict:
    """
    Analyze a cosmetic formulation and return structured JSON.

    Parameters
    ----------
    ingredient_list       : Ordered list of INCI ingredient names (first = highest conc.)
    product_type          : e.g. "shampoo", "face cream", "leave-in conditioner"
    region                : e.g. "EU", "US", "both"
    target_group          : e.g. "general adult", "children under 3", "sensitive skin"
    known_concentrations  : Optional dict {ingredient_name_lower: float_percentage}

    Returns
    -------
    dict with keys: overall_verdict, executive_summary, ingredients,
                    combination_alerts, regulatory_flags
    """
    if known_concentrations is None:
        known_concentrations = {}

    usage_type = classify_usage_type(product_type)
    region_lower = region.lower()
    group_lower = target_group.lower()

    # ---- Per-ingredient analysis ----
    ingredients_out = []
    found_names_lower = [i.strip().lower() for i in ingredient_list]
    formaldehyde_releasers_found = []
    parabens_found = []
    preservatives_found = []
    sensitizers_found = []

    for raw_name in ingredient_list:
        name_lower = raw_name.strip().lower()
        data = _lookup(name_lower)
        known_pct = known_concentrations.get(name_lower)

        if data is None:
            ingredients_out.append({
                "name": raw_name,
                "function": "Unknown",
                "eu_status": "unknown",
                "verdict": "CAUTION",
                "concentration_concern": "unknown — not in regulatory database",
                "combination_effect": "None identified",
                "usage_type_concern": "None identified",
                "reason": (
                    f"'{raw_name}' was not found in the regulatory knowledge base. "
                    "Manual review against EU Annex II–VI is recommended."
                ),
            })
            continue

        verdict = data["base_verdict"]

        # -- Concentration check
        conc_concern = "No"
        if data["eu_limit_pct"] is not None:
            if known_pct is not None:
                if known_pct > data["eu_limit_pct"]:
                    conc_concern = (
                        f"YES — provided {known_pct}% EXCEEDS EU limit of {data['eu_limit_pct']}%"
                    )
                    verdict = "FLAG"
                else:
                    conc_concern = (
                        f"No — {known_pct}% is within EU limit of {data['eu_limit_pct']}%"
                    )
            else:
                conc_concern = (
                    f"concentration-dependent — EU limit is {data['eu_limit_pct']}%. "
                    "Concentration not provided; compliance unverifiable."
                )
        else:
            conc_concern = "No strict EU numerical limit" if known_pct is None else "No strict EU numerical limit"

        # -- Usage type concern
        usage_concern = data["usage_type_concern"].get(usage_type, "None")

        # -- Group concern
        group_flags = []
        for g in data["groups_concern"]:
            label = GROUP_LABELS.get(g, g)
            if g in group_lower or g.replace("_", " ") in group_lower:
                group_flags.append(f"APPLIES TO THIS USER GROUP: {label}")
            else:
                group_flags.append(f"Restriction exists for {label}")

        # -- Track categories
        if data["formaldehyde_releaser"]:
            formaldehyde_releasers_found.append(name_lower)
        if data["paraben"]:
            parabens_found.append(name_lower)
        if data.get("sensitizer"):
            sensitizers_found.append(raw_name)

        # Count as preservative if function contains "preservative"
        if "preservative" in data["function"].lower():
            preservatives_found.append(name_lower)

        ingredients_out.append({
            "name": raw_name,
            "function": data["function"],
            "eu_status": data["eu_status"].capitalize(),
            "verdict": verdict,
            "concentration_concern": conc_concern,
            "combination_effect": "See COMBINATION ALERTS section",
            "usage_type_concern": usage_concern if usage_concern != "None" else "None for this product type",
            "group_concern": "; ".join(group_flags) if group_flags else "None",
            "reason": data["eu_limit_note"],
        })

    # ---- Combination alerts ----
    combo_alerts = []
    for rule in COMBINATION_RULES:
        rule_ings = rule["ingredients"]
        co_triggers = rule.get("co_triggers", [])
        min_count = rule.get("min_count", 1)

        # Count primary matches
        primary_found = [n for n in found_names_lower
                         if any(ri in n or n in ri for ri in rule_ings)]

        if co_triggers:
            co_found = [n for n in found_names_lower
                        if any(ct in n or n in ct for ct in co_triggers)]
            if primary_found and co_found:
                combo_alerts.append(rule["alert"])
        else:
            if len(primary_found) >= min_count:
                combo_alerts.append(rule["alert"])

    # ---- Regulatory flags ----
    reg_flags = []

    # EU mandatory formaldehyde label
    if formaldehyde_releasers_found:
        reg_flags.append(
            f"EU MANDATORY LABEL: Products containing formaldehyde releasers "
            f"({', '.join(formaldehyde_releasers_found)}) must state "
            f"'contains formaldehyde' if released HCHO concentration exceeds 0.05% "
            f"(EU Annex III, entry 13)."
        )

    # EU paraben mixture rule
    if len(parabens_found) >= 2:
        reg_flags.append(
            f"EU PARABEN MIXTURE RULE: Multiple parabens present "
            f"({', '.join(parabens_found)}). Total combined parabens must not exceed 0.8%. "
            f"Propylparaben individually ≤ 0.14%. Verify all concentrations."
        )

    # Fragrance allergen disclosure
    frag_present = any("fragrance" in n or "parfum" in n for n in found_names_lower)
    if frag_present:
        threshold = "0.01%" if usage_type == "rinse-off" else "0.001%"
        reg_flags.append(
            f"EU FRAGRANCE DISCLOSURE (Regulation 2023/1545, effective Aug 2025): "
            f"All fragrance allergens present at ≥{threshold} in this "
            f"{usage_type} product must be individually declared on the label. "
            f"Listing only 'Fragrance/Parfum' will be non-compliant."
        )

    # Banned ingredients
    for ing_out in ingredients_out:
        if ing_out["verdict"] == "BANNED_IN_CONTEXT":
            reg_flags.append(
                f"EU BAN: '{ing_out['name']}' is prohibited under EU Regulation 1223/2009. "
                f"Must be removed from formulation for EU market."
            )

    # Leave-on specific: retinol label
    retinol_present = any("retinol" in n for n in found_names_lower)
    if retinol_present and usage_type == "leave-on":
        reg_flags.append(
            "EU MANDATORY LABEL (Retinol): Leave-on products containing retinol must bear "
            "'Not recommended for use on children' warning (SCCS 2022). "
            "Concentration must not exceed 0.3% on face/body for adult products."
        )

    # Salicylic acid limit
    sa_present = any("salicylic acid" in n for n in found_names_lower)
    if sa_present:
        limit = "3%" if usage_type == "rinse-off" else "2%"
        reg_flags.append(
            f"EU CONCENTRATION LIMIT: Salicylic acid max {limit} in {usage_type} products. "
            f"Not for use in children under 3."
        )

    # Aerosol titanium dioxide
    tio2_present = any("titanium dioxide" in n for n in found_names_lower)
    if tio2_present and usage_type == "aerosol":
        reg_flags.append(
            "EU BAN: Titanium dioxide is PROHIBITED in aerosol/spray products "
            "due to inhalation carcinogenicity (Category 2, EU 2021). "
            "This formulation CANNOT be marketed as a spray in the EU."
        )

    # MIT in leave-on
    mit_present = any(
        "methylisothiazolinone" in n or n == "mit" for n in found_names_lower
    )
    if mit_present and usage_type == "leave-on":
        reg_flags.append(
            "EU BAN: Methylisothiazolinone (MIT) is BANNED in leave-on cosmetics "
            "in the EU (Commission Regulation 2016/1198). Remove immediately."
        )

    # ---- Overall verdict logic ----
    verdicts = [i["verdict"] for i in ingredients_out]
    has_banned = "BANNED_IN_CONTEXT" in verdicts
    has_flag = "FLAG" in verdicts
    has_caution = "CAUTION" in verdicts
    harmful_combos = sum(1 for c in combo_alerts if "HARMFUL" in c or "BANNED" in c or "carcinogen" in c.lower())

    if has_banned or (has_flag and harmful_combos > 0):
        overall_verdict = "RED"
    elif has_flag or (has_caution and harmful_combos > 0):
        overall_verdict = "YELLOW"
    elif has_caution:
        overall_verdict = "YELLOW"
    else:
        overall_verdict = "GREEN"

    # ---- Executive summary ----
    n_flag = verdicts.count("FLAG")
    n_caution = verdicts.count("CAUTION")
    n_banned = verdicts.count("BANNED_IN_CONTEXT")
    n_safe = verdicts.count("SAFE")

    summary_parts = [
        f"This {product_type} ({usage_type}) formulation for {target_group} was analyzed "
        f"against {region} regulations.",
        f"Of {len(ingredient_list)} ingredients: {n_safe} are SAFE, {n_caution} CAUTION, "
        f"{n_flag} FLAG, {n_banned} BANNED.",
    ]
    if n_banned > 0:
        summary_parts.append(
            f"Banned ingredients must be removed before EU market entry."
        )
    if formaldehyde_releasers_found:
        summary_parts.append(
            f"Formaldehyde-releasing preservative(s) detected "
            f"({', '.join(formaldehyde_releasers_found)}): mandatory EU label required "
            f"if released HCHO exceeds 0.05%."
        )
    if len(parabens_found) >= 2:
        summary_parts.append(
            "Multiple parabens require concentration verification under EU mixture rules."
        )
    if frag_present:
        summary_parts.append(
            "Fragrance allergen disclosure compliance is required by August 2025 per EU 2023/1545."
        )
    if combo_alerts:
        summary_parts.append(
            f"{len(combo_alerts)} combination interaction(s) identified "
            f"(see combination_alerts)."
        )

    executive_summary = " ".join(summary_parts)

    return {
        "overall_verdict": overall_verdict,
        "executive_summary": executive_summary,
        "product_type": product_type,
        "usage_type": usage_type,
        "region": region,
        "target_group": target_group,
        "ingredients": ingredients_out,
        "combination_alerts": combo_alerts if combo_alerts else ["No significant interactions detected."],
        "regulatory_flags": reg_flags if reg_flags else ["No mandatory regulatory flags triggered."],
    }
